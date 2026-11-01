"""Game loop and entry point: input, camera and drawing around a ``Run``."""

from __future__ import annotations

import math
import random
import sys
from dataclasses import asdict

import pygame

from src import materials as mat
from src import options as settings_store
from src import records
from src.audio import Audio
from src.depths import DEPTHS
from src.editor import WandEditor
from src.enemies import SPECIES
from src.floaters import FloatingNumbers
from src.gamepad import Gamepad, PadState
from src.hover import HoverInfo, describe
from src.hud import Hud, HudState
from src.inventory import SORT_MODES
from src.keybinds import ACTION_BY_KEY, binding_name_de
from src.menus import PAUSE_ITEMS, Menus, controls_rows, help_lines, title_items
from src.perks import PERK_BY_KEY
from src.projectiles import Blast
from src.rendering import (
    WorldRenderer,
    build_creature_sprites,
    build_player_sprites,
    draw_augmentation,
    draw_chunks,
    draw_creatures,
    draw_droplets,
    draw_exit,
    draw_pickups,
    draw_projectiles,
    draw_status,
    draw_thrown_flasks,
)
from src.run import Controls, Run
from src.runlog import RunLog
from src.settings import (
    BRUSH_DEFAULT,
    BRUSH_MAX,
    BRUSH_MIN,
    COLOR_BACKGROUND,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SIM_MARGIN,
    TITLE,
    VIEW_HEIGHT,
    VIEW_WIDTH,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from src.spells import BLOCKS, CATALOG
from src.viewport import Viewport

CAMERA_FOLLOW = 8.0  # 1/s, higher is snappier
LOOK_AHEAD = 0.22  # share of the cursor offset the camera leans towards
HEARTBEAT_RATE = 1.5  # beats per second while close to death
SIGHT_INTERVAL = 0.1  # seconds between line-of-sight updates
NOTICE_TIME = 3.0  # seconds a "Neu im Kodex" note stays
FADE_TIME = 0.7  # seconds of the fade-in after descending
SHAKE_DECAY = 18.0  # 1/s
BANNER_TIME = 3.0  # seconds the depth name is shown
PLAYER_LIGHT_RADIUS = 150.0
CREATURE_GLOW = (22.0, 0.22)  # (radius, intensity): creatures are faintly visible in the dark
PAD_AIM_DISTANCE = 90.0  # px between the player and the gamepad crosshair
PAD_CURSOR_SPEED = 900.0  # window px/s of the inventory cursor on the left stick
PAD_REPEAT = 0.22  # seconds between menu steps while a stick is held
STATUS_INTERVAL = 10.0  # seconds between position/health lines in the run log
# Sandbox: keys 1-9 and 0 select what the right mouse button paints.
PAINT_MATERIALS = (
    mat.BONE_DUST,
    mat.BLOOD,
    mat.TALLOW,
    mat.ACID,
    mat.FLESH,
    mat.BONE,
    mat.MUCUS,
    mat.FIRE,
    mat.GROWTH,
    mat.ENAMEL,
)
NUMBER_KEYS = (
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
)  # fmt: skip
SANDBOX_LINES = (
    "Rechte Maus: malen | Mittlere Maus: radieren",
    "Mausrad: Material | +/-: Pinselgröße",
    "N: Welt neu | Bild auf/ab: Tiefe wechseln",
    "Rucksack: Zauberbuch mit allen bekannten Zaubern",
    "ESC: Menü (Zum Titel beendet die Sandbox)",
)
MENU_STATES = ("title", "paused", "options", "codex", "controls")
# Gamepad buttons in menus act like these keys.
PAD_MENU_KEYS = {
    "hoch": pygame.K_UP, "runter": pygame.K_DOWN, "links": pygame.K_LEFT,
    "rechts": pygame.K_RIGHT, "a": pygame.K_RETURN, "b": pygame.K_ESCAPE,
    "start": pygame.K_ESCAPE,
}  # fmt: skip


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.viewport = Viewport(VIEW_WIDTH, VIEW_HEIGHT)
        self.canvas = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
        self.hud = Hud()
        self.editor = WandEditor()
        self.menus = Menus()
        self.audio = Audio()
        self.gamepad = Gamepad()
        self.log = RunLog()
        self.state = "title"
        self.menu_index = 0
        self.menu_rects: list[pygame.Rect] = []
        self.menu_return = "title"  # where options / controls go back to
        self.capturing = False  # waiting for a new key in the controls screen
        self.controls_note = ""
        self.records = records.load()
        self.options = settings_store.load()
        self.bindings = settings_store.load_bindings()
        self.saved_run = records.load_run()
        self.saved_checkpoint: object = None  # the checkpoint last written to disk
        self.floaters = FloatingNumbers()
        self.fade = 0.0
        self.sight_timer = 0.0
        self.visible: set[int] = set()
        self.heartbeat = 0.0
        self.last_cam = (0, 0)
        self.notice = ""
        self.notice_time = 0.0
        self.run_recorded = False
        self.cheated = False  # sandbox used this run: it does not count for the records
        self.in_run = False  # a run is being played (title screen: False)
        self.clock_time = 0.0
        self.seed = random.randrange(2**31)
        self.run = Run(self.seed)
        self.renderer = WorldRenderer(self.run.world, VIEW_WIDTH, VIEW_HEIGHT)
        self.sprite_right, self.sprite_left = build_player_sprites()
        self.creature_sprites = build_creature_sprites()
        self.camera = [0.0, 0.0]
        self.shake = 0.0
        self.sandbox = False
        self.paint_index = 0
        self.brush = BRUSH_DEFAULT
        self.lighting = True
        self.effects_rng = random.Random()
        self.queued: set[str] = set()  # press actions waiting for the next update
        self.pad_mode = False  # the gamepad was used last: aim with the right stick
        self.pad_aim = (1.0, 0.0)
        self.pad_repeat = 0.0
        self.pad_click = False  # A held as a mouse button in the inventory
        self.hover: HoverInfo | None = None
        self.shown_depth = -1
        self._place = ""
        self.status_timer = 0.0
        self._snap_camera()
        self._apply_options()

    # ------------------------------------------------------------------ state

    def _snap_camera(self) -> None:
        cx, cy = self.run.player.center
        self.camera = [cx - VIEW_WIDTH / 2, cy - VIEW_HEIGHT / 2]
        self._clamp_camera()

    def _clamp_camera(self) -> None:
        self.camera[0] = min(max(self.camera[0], 0.0), WORLD_WIDTH - VIEW_WIDTH)
        self.camera[1] = min(max(self.camera[1], 0.0), WORLD_HEIGHT - VIEW_HEIGHT)

    def _apply_options(self) -> None:
        options = self.options
        self.audio.set_volumes(options.effects / settings_store.STEPS, options.music / settings_store.STEPS)
        self.lighting = options.lighting
        if options.fullscreen != self.is_fullscreen:
            self.toggle_fullscreen()

    def toggle_fullscreen(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
        self.options.fullscreen = self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    def _go(self, state: str) -> None:
        """Switch to another screen (menus start at their first entry)."""
        if state in ("options", "controls") and self.state not in ("options", "controls"):
            self.menu_return = self.state
        self.state = state
        self.menu_index = 0
        self.menu_rects = []
        self.capturing = False
        self.controls_note = ""

    # ----------------------------------------------------------------- events

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_run_state()  # closing the window keeps the run, like in Noita
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.pad_mode = False
                self._menu_hover(event.pos)
            if self.state == "controls" and self.capturing:
                self._capture(event)
            elif self.state != "playing":
                if event.type == pygame.KEYDOWN:
                    self._on_menu_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._menu_click(event.pos)
                elif event.type == pygame.MOUSEWHEEL and self.state == "controls":
                    self._menu_step(-event.y)
            elif self.editor.open:
                if event.type == pygame.KEYDOWN and (
                    event.key == pygame.K_ESCAPE or "inventory" in self.bindings.actions_for(event.key)
                ):
                    self.editor.toggle()
                else:
                    self.editor.handle_event(event, self.run)
            elif event.type == pygame.KEYDOWN:
                self._on_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 2, 3):
                for action in self.bindings.actions_for(f"maus{event.button}"):
                    self._on_action(action)
            elif event.type == pygame.MOUSEWHEEL:
                if self.sandbox:  # the wheel picks the paint material
                    self.paint_index = (self.paint_index - event.y) % len(PAINT_MATERIALS)
                else:
                    self.run.inventory.cycle(-event.y)

    def _menu_items(self) -> list[tuple[str, str]]:
        if self.state == "title":
            return title_items(self._saved_depth(), self._saved_live())
        if self.state == "paused":
            return list(PAUSE_ITEMS)
        if self.state == "options":
            return list(settings_store.Options.ENTRIES)
        if self.state == "controls":
            return controls_rows()
        return []

    def _saved_depth(self) -> int | None:
        saved = self.saved_run.get("depth_index") if self.saved_run else None
        if not isinstance(saved, int):
            return None
        live = self.saved_run.get("live")
        if isinstance(live, dict):  # saved in the middle of a depth (or in a sanctum)
            return saved + (2 if live.get("in_sanctum") else 1)
        return saved + 2

    def _saved_live(self) -> bool:
        return bool(self.saved_run) and isinstance(self.saved_run.get("live"), dict)

    def _save_run_state(self) -> None:
        """Save the run exactly where it is (pause menu or closing the window)."""
        if not self.in_run or self.run.outcome or self.sandbox:
            return
        data = self.run.save_state()
        if records.save_run(data):
            self.saved_run = data
            self.saved_checkpoint = self.run.checkpoint
        records.save(self.records)
        self.log.write("gespeichert", ort=self._where())
        self.in_run = False

    def _menu_step(self, step: int) -> None:
        items = self._menu_items()
        if items:
            self.menu_index = (self.menu_index + step) % len(items)

    def _menu_hover(self, pos: tuple[int, int]) -> None:
        if self.state == "playing" or self.capturing:
            return
        for index, rect in enumerate(self.menu_rects):
            if rect.width and rect.collidepoint(pos):
                self.menu_index = index

    def _menu_click(self, pos: tuple[int, int]) -> None:
        for index, rect in enumerate(self.menu_rects):
            if rect.width and rect.collidepoint(pos):
                self.menu_index = index
                if self.state == "options":
                    self._change_option(1)
                else:
                    self._activate()
                return
        if self.state == "codex":
            self._go("title")

    def _on_menu_key(self, key: int) -> None:
        if key == pygame.K_F11:
            self.toggle_fullscreen()
        elif self.state == "codex":
            if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_k):
                self._go("title")
        elif key in (pygame.K_UP, pygame.K_w):
            self._menu_step(-1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._menu_step(1)
        elif self.state == "options" and key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            self._change_option(-1 if key in (pygame.K_LEFT, pygame.K_a) else 1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.state == "options":
                self._change_option(1)
            else:
                self._activate()
        elif key in (pygame.K_DELETE, pygame.K_BACKSPACE) and self.state == "controls":
            action = controls_rows()[self.menu_index][0]
            if action in ACTION_BY_KEY:
                self.bindings.reset(action)
                self._save_bindings(f"{ACTION_BY_KEY[action].label_de}: Standard wiederhergestellt.")
        elif key == pygame.K_ESCAPE:
            self._menu_back()

    def _menu_back(self) -> None:
        if self.state == "title":
            self.running = False
        elif self.state == "paused":
            self.state = "playing"
        elif self.state in ("options", "controls"):
            if self.state == "options":
                settings_store.save(self.options)
            back = self.menu_return
            self._go(back)
            if back == "paused":
                self.menu_index = 2 if self.state == "paused" else 0
        else:
            self._go("title")

    def _activate(self) -> None:
        items = self._menu_items()
        if not items:
            return
        key = items[self.menu_index][0]
        if self.state == "title":
            if key == "new":
                self._start_run()
            elif key == "sandbox":
                self._start_run(sandbox=True)
            elif key == "continue":
                self._continue_run()
            elif key == "quit":
                self.running = False
            else:
                self._go(key)
        elif self.state == "paused":
            if key == "resume":
                self.state = "playing"
            elif key == "inventory":
                self.state = "playing"
                self.editor.toggle()
            elif key == "restart":
                self._start_run(sandbox=self.sandbox)
            elif key == "title":
                self._save_run_state()
                self._go("title")
            elif key == "quit":
                self._save_run_state()
                self.running = False
            else:
                self._go(key)
        elif self.state == "controls":
            if key == "back":
                self._menu_back()
            elif key == "reset":
                self.bindings.reset()
                self._save_bindings("Alle Belegungen auf Standard zurückgesetzt.")
            else:
                self.capturing = True
                self.controls_note = ""

    def _change_option(self, step: int) -> None:
        name = settings_store.Options.ENTRIES[self.menu_index][0]
        self.options.change(name, step)
        self._apply_options()

    def _capture(self, event: pygame.event.Event) -> None:
        """The controls screen waits for the new key of the selected action."""
        action = controls_rows()[self.menu_index][0]
        label = ACTION_BY_KEY[action].label_de
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.capturing = False
                return
            losers = self.bindings.bind(action, event.key)
            self._bound(label, binding_name_de(event.key), losers)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 2, 3):
            token = f"maus{event.button}"
            losers = self.bindings.bind(action, token)
            self._bound(label, binding_name_de(token), losers)

    def _capture_pad(self, pad: PadState) -> None:
        action = controls_rows()[self.menu_index][0]
        for button in sorted(pad.pressed):
            if button == "start":
                self.capturing = False
                return
            losers = self.bindings.bind_pad(action, button)
            self._bound(ACTION_BY_KEY[action].label_de, button.upper(), losers)
            return

    def _bound(self, label: str, name: str, losers: list[str]) -> None:
        self.capturing = False
        note = f"{label}: {name}"
        if losers:
            note += " (entfernt bei: " + ", ".join(ACTION_BY_KEY[a].label_de for a in losers) + ")"
        self._save_bindings(note)

    def _save_bindings(self, note: str) -> None:
        self.controls_note = note
        settings_store.save_bindings(self.bindings)
        self.log.write("steuerung", aenderung=note)

    # ------------------------------------------------------------------- runs

    def _start_run(self, sandbox: bool = False) -> None:
        if not sandbox:
            records.delete_run()  # a new run replaces the saved one
            self.saved_run = None
        self.run.favoured_blocks, self.run.start_pearls = self.records.unlocks()
        self.run.log.clear()  # entries from before the run started (title screen)
        self.run.new_run()
        self._begin(fortgesetzt=False, sandbox=sandbox)

    def _continue_run(self) -> None:
        self.run.log.clear()
        try:
            self.run.restore(self.saved_run)
        except ValueError:  # from an older, incompatible version: start fresh instead
            self._start_run()
            return
        if self._saved_live():
            # a full save is used once: from now on the disk holds the last sanctum
            # again, so quitting without saving cannot rewind the run
            if self.run.checkpoint is not None:
                records.save_run(self.run.checkpoint)
                self.saved_run = self.run.checkpoint
            else:
                records.delete_run()
                self.saved_run = None
        self.saved_checkpoint = self.run.checkpoint
        self._begin(fortgesetzt=True)

    def _begin(self, sandbox: bool = False, **info: object) -> None:
        self.in_run = True
        self._snap_camera()
        self.sandbox = self.cheated = sandbox
        self.run.sandbox = sandbox
        self.run.god_mode = False
        self.run.known_blocks = set(self.records.blocks)
        self.run.known_blocks.update(k for w in self.run.inventory.wands for k in w.slots if k)
        known = set(self.records.blocks) | {k for w in self.run.inventory.wands for k in w.slots if k}
        self.editor.palette = [block.key for block in BLOCKS if block.key in known] if sandbox else []
        self.editor.palette_mode = sandbox
        self.editor.page = 0
        self.run_recorded = False
        self.state = "playing"
        self.editor.open = False
        self.log.start(
            version=getattr(sys.modules.get("src"), "__version__", "?"),
            seed=self.seed,
            route=[depth.key for depth in self.run.route],
            optionen=asdict(self.options),
            sandbox=sandbox,
            controller=self.gamepad.state.name or None,
            **info,
        )
        self._drain_run_log()
        self._place = self._where()

    def _where(self) -> str:
        return "sanktum" if self.run.in_sanctum else self.run.depth.key

    def _record_run(self) -> None:
        """Store a finished run in the persistent records (once per run)."""
        if self.run_recorded or not self.run.outcome:
            return
        self.run_recorded = True
        if not self.cheated:  # a sandbox test never touches the saved real run
            records.delete_run()  # the run is over: nothing to continue
            self.saved_run = None
        stats = self.run.stats
        self._drain_run_log()
        self.log.flush_frames(self._place)
        self.log.write(
            "ende", ergebnis=self.run.outcome, tiefe=self.run.next_depth_number, uraugen=self.run.eyes,
            getoetet=stats["kills"], blutperlen=stats["pearls"], zeit=round(float(stats["time"]), 1),
            sandbox=self.cheated, perks=sorted(self.run.perks),
        )  # fmt: skip
        if self.cheated:
            return
        self.records.add_run(
            won=self.run.outcome == "victory",
            depth=self.run.depth_index + 1,
            kills=int(stats["kills"]),
            pearls=int(stats["pearls"]),
            time=float(stats["time"]),
            eyes=self.run.eyes,
            ng=self.run.ng,
        )
        records.save(self.records)

    def _drain_run_log(self) -> None:
        for event, data in self.run.log:
            self.log.write(event, **data)
        self.run.log.clear()

    def _show_messages(self) -> None:
        for message in self.run.messages:
            self.notice, self.notice_time = message, NOTICE_TIME
        self.run.messages.clear()

    def _note_discoveries(self) -> None:
        if self.cheated:
            self.run.discoveries.clear()
            return
        for kind, key in self.run.discoveries:
            if self.records.discover(kind, key):
                name = CATALOG[key].name_de if kind == "block" else SPECIES[key].name_de
                self.notice, self.notice_time = f"Neu im Kodex: {name}", NOTICE_TIME
        self.run.discoveries.clear()

    def _save_checkpoint(self) -> None:
        """Write the run to disk whenever it reaches a new sanctum."""
        checkpoint = self.run.checkpoint
        if checkpoint is None or checkpoint is self.saved_checkpoint or self.cheated:
            return
        self.saved_checkpoint = checkpoint
        self.saved_run = checkpoint
        records.save_run(checkpoint)
        records.save(self.records)  # keep Kodex finds even if the game is closed now

    # ------------------------------------------------------------------ input

    def _on_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self._go("paused")
            return
        if key == pygame.K_RETURN and self.run.outcome:
            self._start_run(sandbox=self.sandbox)  # after death or victory: go again
            return
        if key in NUMBER_KEYS:
            number = NUMBER_KEYS.index(key)
            if number < 4:
                self.run.inventory.select(number)
            elif number < 8:
                self.run.select_flask(number - 4)
            return
        if self.sandbox and self._sandbox_key(key):
            return
        for action in self.bindings.actions_for(key):
            self._on_action(action)

    def _sandbox_key(self, key: int) -> bool:
        """Fixed keys of the sandbox (test mode from the title menu)."""
        run = self.run
        if key == pygame.K_g:
            run.god_mode = not run.god_mode
            self.notice = "Gottmodus " + ("an" if run.god_mode else "aus")
            self.notice_time = NOTICE_TIME
        elif key == pygame.K_n:
            run.enter_depth(run.depth_index)
            self._snap_camera()
        elif key in (pygame.K_PLUS, pygame.K_KP_PLUS):
            self.brush = min(self.brush + 1, BRUSH_MAX)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.brush = max(self.brush - 1, BRUSH_MIN)
        elif key == pygame.K_PAGEDOWN:
            run.enter_depth(min(run.depth_index + 1, len(run.route) - 1))
            self._snap_camera()
        elif key == pygame.K_PAGEUP:
            run.enter_depth(max(run.depth_index - 1, 0))
            self._snap_camera()
        else:
            return False
        return True

    def _on_action(self, action: str) -> None:
        """A press of an action's key, mouse button or gamepad button."""
        run = self.run
        if action in ("jump", "pickup", "drink", "throw", "kick"):
            self.queued.add(action)
        elif action == "next_wand":
            run.inventory.cycle(1)
        elif action == "prev_wand":
            run.inventory.cycle(-1)
        elif action == "next_flask":
            run.cycle_flask(1)
        elif action == "inventory":
            self.editor.toggle()
            self.log.write("rucksack", umbauen=run.can_edit_wands)
        elif action == "light":
            self.lighting = self.options.lighting = not self.lighting
        elif action == "mute":
            self.audio.toggle_mute()
        elif action == "fullscreen":
            self.toggle_fullscreen()
        elif action == "new_game_plus" and run.outcome == "victory":
            run.new_game_plus()
            self.run_recorded = False  # the next loop is recorded again
            self._snap_camera()
            self.fade = 1.0

    def _held(self, action: str, keys, mouse: tuple[bool, bool, bool], pad: PadState) -> bool:
        for binding in self.bindings.keys.get(action, ()):
            if isinstance(binding, int):
                try:
                    if keys[binding]:
                        return True
                except IndexError:
                    continue
            elif binding.startswith("maus") and mouse[int(binding[4]) - 1]:
                return True
        button = self.bindings.pad.get(action)
        return button is not None and button in pad.buttons

    def _handle_pad(self, pad: PadState, dt: float) -> None:
        """Gamepad presses: menus, the inventory cursor and in-game actions."""
        if pad.pressed or pad.move != (0.0, 0.0) or pad.aim != (0.0, 0.0):
            self.pad_mode = self.pad_mode or self.state == "playing"
        if pad.aim != (0.0, 0.0):
            length = math.hypot(*pad.aim)
            self.pad_aim = (pad.aim[0] / length, pad.aim[1] / length)
        if self.state == "controls" and self.capturing:
            self._capture_pad(pad)
            return
        if self.state != "playing":
            for button in pad.pressed:
                if self.state == "title" and button in ("b", "start"):
                    continue  # never quit the game by accident from the pad
                if button in PAD_MENU_KEYS:
                    self._on_menu_key(PAD_MENU_KEYS[button])
            self.pad_repeat -= dt
            if abs(pad.move[1]) > 0.5 and self.pad_repeat <= 0:
                self.pad_repeat = PAD_REPEAT
                self._on_menu_key(pygame.K_DOWN if pad.move[1] > 0 else pygame.K_UP)
            elif abs(pad.move[1]) <= 0.5:
                self.pad_repeat = 0.0
            return
        if self.editor.open:
            self._pad_inventory(pad, dt)
            return
        if "start" in pad.pressed:
            self._go("paused")
            return
        if self.run.outcome and "a" in pad.pressed:
            self._start_run(sandbox=self.sandbox)
            return
        for button in pad.pressed:
            for action in self.bindings.pad_actions_for(button):
                self._on_action(action)

    def _pad_inventory(self, pad: PadState, dt: float) -> None:
        """In the inventory the left stick moves the mouse cursor and A clicks."""
        if pad.pressed & {"b", "start"} or "inventory" in {
            a for b in pad.pressed for a in self.bindings.pad_actions_for(b)
        }:
            self.editor.toggle()
            return
        mx, my = pygame.mouse.get_pos()
        if pad.move != (0.0, 0.0):
            mx += round(pad.move[0] * PAD_CURSOR_SPEED * dt)
            my += round(pad.move[1] * PAD_CURSOR_SPEED * dt)
            pygame.mouse.set_pos((mx, my))
        if "x" in pad.pressed:  # like a right click: between the wand in hand and the bag
            self.editor.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(mx, my)), self.run)
        if "y" in pad.pressed:
            self.editor.sort_mode = (self.editor.sort_mode + 1) % len(SORT_MODES)
            self.run.inventory.sort_bag(SORT_MODES[self.editor.sort_mode][0])
        holding = "a" in pad.buttons
        if holding != self.pad_click:
            self.pad_click = holding
            kind = pygame.MOUSEBUTTONDOWN if holding else pygame.MOUSEBUTTONUP
            self.editor.handle_event(pygame.event.Event(kind, button=1, pos=(mx, my)), self.run)

    def _cursor_in_world(self) -> tuple[int, int]:
        if self.pad_mode:
            cx, cy = self.run.player.center
            return (
                int(cx + self.pad_aim[0] * PAD_AIM_DISTANCE),
                int(cy + self.pad_aim[1] * PAD_AIM_DISTANCE),
            )
        mouse_x, mouse_y = pygame.mouse.get_pos()
        view_x, view_y = self.viewport.to_virtual(mouse_x, mouse_y)
        return int(view_x + self.camera[0]), int(view_y + self.camera[1])

    def _cursor_on_screen(self, target: tuple[int, int]) -> tuple[int, int]:
        if not self.pad_mode:
            return pygame.mouse.get_pos()
        scale = self.viewport.scale
        return (
            int(self.viewport.offset_x + (target[0] - self.last_cam[0]) * scale),
            int(self.viewport.offset_y + (target[1] - self.last_cam[1]) * scale),
        )

    def _sim_area(self) -> tuple[int, int, int, int]:
        x0, y0 = int(self.camera[0]) - SIM_MARGIN, int(self.camera[1]) - SIM_MARGIN
        return (x0, y0, x0 + VIEW_WIDTH + 2 * SIM_MARGIN, y0 + VIEW_HEIGHT + 2 * SIM_MARGIN)

    # ----------------------------------------------------------------- update

    def update(self, dt: float) -> None:
        self.clock_time += dt
        pad = self.gamepad.poll(dt)
        self._handle_pad(pad, dt)
        self.editor.update(dt)
        in_menu_music = self.state in ("title", "codex") or (
            self.state in ("options", "controls") and self.menu_return == "title"
        )
        self.audio.play_music("sanktum" if in_menu_music or self.run.in_sanctum else self.run.depth.key)
        if self.editor.open or self.state != "playing":
            self.hover = None
            return  # menus and the inventory pause the game
        self.log.frame(dt)
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        target = self._cursor_in_world()

        def held(action: str) -> bool:
            return self._held(action, keys, mouse, pad)

        move = int(held("right")) - int(held("left"))
        if not move and abs(pad.move[0]) > 0.3:
            move = 1 if pad.move[0] > 0 else -1
        queued, self.queued = self.queued, set()
        controls = Controls(
            move=move,
            jump="jump" in queued,
            levitate=held("jump"),
            cast=held("cast"),
            aim=(float(target[0]), float(target[1])),
            pickup="pickup" in queued,
            pour=held("pour") and not (self.sandbox and mouse[2]),
            absorb=held("absorb"),
            drink="drink" in queued,
            throw="throw" in queued,
            kick="kick" in queued,
        )
        if self.sandbox and mouse[2]:
            self.run.world.paint(*target, self.brush, PAINT_MATERIALS[self.paint_index])
        elif self.sandbox and mouse[1]:
            self.run.world.paint(*target, self.brush, mat.AIR)

        depth_before, sanctum_before = self.run.depth_index, self.run.in_sanctum
        for blast in self.run.update(dt, controls, self._sim_area()):
            self._on_blast(blast)
        for event in self.run.events:
            self.audio.play(event)
        self._note_discoveries()
        self._show_messages()
        self._drain_run_log()
        player = self.run.player
        self.status_timer += dt
        if self.status_timer >= STATUS_INTERVAL and not self.run.outcome:
            self.status_timer = 0.0
            self.log.write(
                "status", ort=self._where(), x=round(player.x), y=round(player.y),
                leben=round(player.hp, 1), max_leben=round(player.max_hp), perlen=self.run.pearls,
                kreaturen=len(self.run.enemies.creatures), fps=round(self.clock.get_fps(), 1),
            )  # fmt: skip
        if 0 < player.hp < player.max_hp * 0.3 and not self.run.outcome:
            self.heartbeat -= dt
            if self.heartbeat <= 0:
                self.heartbeat = 2.0 / HEARTBEAT_RATE
                self.audio.play("heartbeat")
        self.floaters.update([self.run.player, *self.run.enemies.creatures], dt)
        self.sight_timer -= dt
        if self.sight_timer <= 0:  # line-of-sight checks a few times per second are enough
            self.sight_timer = SIGHT_INTERVAL
            self.visible = self.run.update_visibility()
            if self.sandbox:
                for item in self.run.pickups:
                    item.seen = True
        self.hover = describe(self.run, target[0], target[1], None)  # creatures are always shown
        self._save_checkpoint()
        self._record_run()
        self.notice_time = max(0.0, self.notice_time - dt)
        if self.run.depth_index != depth_before or self.run.in_sanctum != sanctum_before:
            self.log.flush_frames(self._place)
            self._place = self._where()
            self._snap_camera()
            self.fade = 1.0  # black, fading into the new place
        self.fade = max(0.0, self.fade - dt / FADE_TIME)

        cx, cy = self.run.player.center
        # like Noita, the camera leans towards where you aim
        cx += (target[0] - cx) * LOOK_AHEAD
        cy += (target[1] - cy) * LOOK_AHEAD
        follow = min(1.0, CAMERA_FOLLOW * dt)
        self.camera[0] += (cx - VIEW_WIDTH / 2 - self.camera[0]) * follow
        self.camera[1] += (cy - VIEW_HEIGHT / 2 - self.camera[1]) * follow
        self._clamp_camera()
        self.shake = max(0.0, self.shake - SHAKE_DECAY * dt)

    def _on_blast(self, blast: Blast) -> None:
        if self.options.shake:
            self.shake = min(6.0, self.shake + blast.radius / 3)

    # ------------------------------------------------------------------- draw

    def draw(self) -> None:
        jitter_x = random.uniform(-self.shake, self.shake)
        jitter_y = random.uniform(-self.shake, self.shake)
        cam_x = int(min(max(self.camera[0] + jitter_x, 0), WORLD_WIDTH - VIEW_WIDTH))
        cam_y = int(min(max(self.camera[1] + jitter_y, 0), WORLD_HEIGHT - VIEW_HEIGHT))
        if self.lighting:
            ambient = self.run.depth.ambient * self.run.darkness
            self.renderer.refresh(self.run.world, cam_x, cam_y, self._lights(), ambient)
        else:
            self.renderer.refresh(self.run.world, cam_x, cam_y)
        self.canvas.blit(self.renderer.surface, (0, 0))
        self._draw_entities(cam_x, cam_y)
        self.last_cam = (cam_x, cam_y)

        self.screen = pygame.display.get_surface()
        self.viewport.resize(*self.screen.get_size())
        self.screen.fill(COLOR_BACKGROUND)
        scaled = pygame.transform.scale(self.canvas, (self.viewport.target_width, self.viewport.target_height))
        self.screen.blit(scaled, (self.viewport.offset_x, self.viewport.offset_y))
        if self.fade > 0:
            veil = pygame.Surface(scaled.get_size())
            veil.set_alpha(int(255 * self.fade))
            self.screen.blit(veil, (self.viewport.offset_x, self.viewport.offset_y))
        menus = self.menus
        if self.state == "title":
            pulse = 0.5 + 0.5 * math.sin(self.clock_time * 3) ** 8
            items = title_items(self._saved_depth(), self._saved_live())
            self.menu_rects = menus.draw_title(
                self.screen, pulse, self.records.lines_de(), items, self.menu_index, self.clock_time
            )
        elif self.state == "codex":
            menus.draw_codex(self.screen, self.records)
            self.menu_rects = []
        elif self.state == "options":
            self.menu_rects = menus.draw_options(self.screen, self.options, self.menu_index)
        elif self.state == "controls":
            self.menu_rects = menus.draw_controls(
                self.screen, self.bindings, self.menu_index, self.capturing, self.controls_note
            )
        else:
            if self.state == "playing":  # the pause menu covers the whole screen
                if self.options.damage_numbers:
                    self.hud.draw_floaters(self.screen, self.viewport, self.floaters.items, self.last_cam)
                self.hud.draw(self.screen, self.viewport, self._hud_state())
            if self.editor.open:
                self.editor.draw(self.screen, self.run)
            if self.state == "paused":
                controls = help_lines(self.bindings, self.gamepad.state.connected)
                self.menu_rects = menus.draw_pause(self.screen, self._run_summary(), self.menu_index, controls)
        pygame.display.flip()

    def _lights(self) -> list[tuple[float, float, float, float]]:
        """Dynamic light sources: (x, y, radius, intensity) in world pixels."""
        run = self.run
        lights: list[tuple[float, float, float, float]] = []
        if not run.player.dead:
            lights.append((*run.player.center, PLAYER_LIGHT_RADIUS, 1.0))
        for projectile in run.projectiles.items:
            radius = projectile.form.light or 26.0
            lights.append((projectile.x, projectile.y, radius, 0.8 if projectile.form.light else 0.45))
        if not run.depth.final:
            strength = 0.7 if run.exit_open else 0.25
            lights.append((*run.level.exit, 48.0, strength))
        x0, y0 = self.camera[0] - 40, self.camera[1] - 40
        x1, y1 = x0 + VIEW_WIDTH + 80, y0 + VIEW_HEIGHT + 80
        for creature in run.enemies.creatures:
            if creature.spec.boss:
                beat = 0.35 + 0.25 * math.sin(creature.age * 5) ** 8
                lights.append((*creature.center, 110.0, beat))
            elif not creature.spec.prop:
                cx, cy = creature.center
                if x0 <= cx <= x1 and y0 <= cy <= y1:
                    lights.append((cx, cy, *CREATURE_GLOW))
        for item in run.pickups:
            if item.wand is not None and item.seen:
                lights.append((item.x, item.y - 3, 18.0, 0.35))
        return lights

    def _hud_state(self) -> HudState:
        run = self.run
        banner = run.depth.name_de if run.time_in_depth < BANNER_TIME else ""
        if banner and run.ng:
            banner = f"{banner} (Neues Spiel+ {run.ng})"
        if banner and run.parallel:
            side = "Ost" if run.parallel > 0 else "West"
            banner = f"{banner} – Parallelwelt {side} {abs(run.parallel)}"
        key = self._key_name("pickup")
        prompt = ""
        item = run.nearest_pickup()
        if item is not None and not run.player.dead:
            if item.perk is not None:
                prompt = f"{key}: Wählen – {item.label_de}"
            elif item.price and not run.can_afford(item):
                prompt = f"{item.label_de} – {run.price_of(item)} Blutperlen (zu wenig)"
            elif item.price:
                prompt = f"{key}: Kaufen – {item.label_de} – {run.price_of(item)} Blutperlen"
            else:
                prompt = f"{key}: Aufheben – {item.label_de}"
        elif run.near_exit() and not run.exit_open and run.depth.boss:
            prompt = "Der Durchgang ist verschlossen. Besiege den Wächter."
        elif run.near_secret():
            prompt = "Hinter der Wand pulsiert etwas."
        outcome = "true_victory" if run.true_ending else run.outcome
        pad = self.gamepad.state.connected
        outcome_keys = "A: Neuer Lauf | Start: Menü" if pad else "Enter: Neuer Lauf | ESC: Menü"
        if run.outcome == "victory":
            outcome_keys = f"{self._key_name('new_game_plus')}: Noch tiefer | {outcome_keys}"
        target = self._cursor_in_world()
        return HudState(
            player=run.player,
            inventory=run.inventory,
            depth_name=run.depth.name_de,
            depth_number=run.next_depth_number,
            depth_total=len(DEPTHS),
            fps=self.clock.get_fps(),
            sandbox=self.sandbox,
            banner=banner,
            prompt=prompt,
            boss=run.enemies.boss() if run.depth.boss else None,
            outcome=outcome,
            pearls=run.pearls,
            perks=tuple((PERK_BY_KEY[k].name_de, PERK_BY_KEY[k].color) for k in sorted(run.perks)),
            stats=self._stats_text(),
            flask=run.flask,
            flasks=run.flasks,
            flask_index=run.flask_index,
            pulse=math.sin(self.clock_time * HEARTBEAT_RATE * math.pi) ** 8,
            notice=self.notice if self.notice_time > 0 else "",
            sandbox_lines=(
                f"Pinsel: {mat.NAME_DE[PAINT_MATERIALS[self.paint_index]]} | Größe {self.brush}",
                f"Gottmodus: {'an' if run.god_mode else 'aus'} (G)",
                *SANDBOX_LINES,
            ),
            hover=None if self.editor.open or self.state != "playing" else self.hover,
            cursor=self._cursor_on_screen(target),
            outcome_keys=outcome_keys,
            log_path=str(self.log.path) if self.log.path else "",
            eyes=run.eyes,
        )

    def _key_name(self, action: str) -> str:
        """What triggers ``action`` on the device in use (keyboard or gamepad)."""
        if self.gamepad.state.connected:
            return self.bindings.describe_pad(action)
        return self.bindings.describe(action)

    def _run_summary(self) -> list[str]:
        """Lines for the pause screen: where you are and what you carry."""
        run = self.run
        perks = ", ".join(PERK_BY_KEY[key].name_de for key in sorted(run.perks)) or "keine"
        lines = [
            f"Tiefe {run.next_depth_number}/{len(DEPTHS)}: {run.depth.name_de}",
            self._stats_text(),
            f"Perks: {perks}",
            f"Uraugen: {run.eyes}/{len(DEPTHS)}   Blutperlen: {run.pearls}",
        ]
        if self.cheated:
            lines.append("Sandbox: zählt nicht für Statistik, Kodex und Spielstand.")
        if self.log.path:
            lines.append(f"Protokoll: {self.log.path.name}")
        return lines

    def _stats_text(self) -> str:
        stats = self.run.stats
        minutes, seconds = divmod(int(stats["time"]), 60)
        return (
            f"Tiefe {self.run.next_depth_number} | Getötet: {stats['kills']} | "
            f"Blutperlen gesammelt: {stats['pearls']} | Zeit: {minutes}:{seconds:02d}"
        )

    def _draw_entities(self, cam_x: int, cam_y: int) -> None:
        run = self.run
        player = run.player
        target = self._cursor_in_world()
        if not run.depth.final:
            draw_exit(self.canvas, run.level.exit, run.exit_open, run.time_in_depth, cam_x, cam_y)
        draw_pickups(self.canvas, run.pickups, cam_x, cam_y, run.known_blocks)
        draw_thrown_flasks(self.canvas, run.thrown, cam_x, cam_y)
        draw_chunks(self.canvas, run.chunks.items, cam_x, cam_y)
        if not player.dead:
            facing_right = target[0] >= player.center[0]
            if player.polymorphed > 0:  # a maggot instead of you
                frame = int(self.clock_time * 6) % 2
                sprite = self.creature_sprites[("made", frame, facing_right, False)]
                self.canvas.blit(sprite, (player.x - cam_x - 1, player.y + player.height - 6 - cam_y))
            else:
                sprite = self.sprite_right if facing_right else self.sprite_left
                self.canvas.blit(sprite, (player.x - cam_x, player.y - cam_y))
                sx, sy = run.shoulder((float(target[0]), float(target[1])))
                angle = math.atan2(target[1] - sy, target[0] - sx)
                draw_augmentation(self.canvas, (sx - cam_x, sy - cam_y), angle, run.inventory.wand)
        draw_creatures(self.canvas, self.creature_sprites, run.enemies.creatures, cam_x, cam_y)
        draw_droplets(self.canvas, run.droplets, cam_x, cam_y)
        for body in (player, *run.enemies.creatures):
            if not body.dead:
                draw_status(self.canvas, body, cam_x, cam_y, self.effects_rng)
        draw_projectiles(self.canvas, run.projectiles.items, cam_x, cam_y)
        if self.sandbox:
            pygame.draw.circle(self.canvas, (230, 220, 200), (target[0] - cam_x, target[1] - cam_y), self.brush, 1)
        elif self.state == "playing" and not self.editor.open:
            x, y = target[0] - cam_x, target[1] - cam_y
            color = (255, 210, 120) if self.hover is not None and self.hover.kind == "creature" else (230, 220, 200)
            for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
                self.canvas.fill(color, (x + dx, y + dy, 1, 1))

    # ------------------------------------------------------------------- loop

    def run_loop(self) -> None:
        try:
            while self.running:
                dt = min(self.clock.tick(FPS) / 1000.0, 0.1)
                self.handle_events()
                self.update(dt)
                self.draw()
        except Exception as error:  # write it into the run log, then crash as usual
            self.log.error(error)
            raise
        finally:
            self.log.write("beendet")
            self.log.close()
            records.save(self.records)  # Kodex finds since the last checkpoint
        pygame.quit()
        sys.exit(0)


def main() -> None:
    game = Game()
    game.run_loop()


if __name__ == "__main__":
    main()
