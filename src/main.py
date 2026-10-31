"""Game loop and entry point: input, camera and drawing around a ``Run``."""

from __future__ import annotations

import math
import random
import sys

import pygame

from src import materials as mat
from src import options as settings_store
from src import records
from src.audio import Audio
from src.depths import DEPTHS
from src.editor import WandEditor
from src.enemies import SPECIES
from src.floaters import FloatingNumbers
from src.hud import Hud, HudState
from src.menus import Menus, title_lines
from src.perks import PERK_BY_KEY
from src.projectiles import Blast
from src.rendering import (
    WorldRenderer,
    build_creature_sprites,
    build_player_sprites,
    draw_augmentation,
    draw_chunks,
    draw_creatures,
    draw_exit,
    draw_pickups,
    draw_projectiles,
    draw_status,
    draw_thrown_flasks,
)
from src.run import Controls, Run
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
from src.spells import CATALOG
from src.viewport import Viewport

CAMERA_FOLLOW = 8.0  # 1/s, higher is snappier
LOOK_AHEAD = 0.22  # share of the cursor offset the camera leans towards
HEARTBEAT_RATE = 1.5  # beats per second while close to death
SIGHT_INTERVAL = 0.1  # seconds between line-of-sight updates
HELP_TIME = 25.0  # the control hints fade out after this long in a run
NOTICE_TIME = 3.0  # seconds a "Neu im Kodex" note stays
FADE_TIME = 0.7  # seconds of the fade-in after descending
SHAKE_DECAY = 18.0  # 1/s
BANNER_TIME = 3.0  # seconds the depth name is shown
PLAYER_LIGHT_RADIUS = 150.0
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
    mat.SPORES,
)
NUMBER_KEYS = (
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
)  # fmt: skip
JUMP_KEYS = (pygame.K_w, pygame.K_UP, pygame.K_SPACE)


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
        self.state = "title"  # "title", "playing" or "paused"
        self.records = records.load()
        self.options = settings_store.load()
        self.options_index = 0
        self.options_return = "title"
        self.saved_run = records.load_run()
        self.saved_checkpoint: object = None  # the checkpoint last written to disk
        self.floaters = FloatingNumbers()
        self.fade = 0.0
        self.sight_timer = 0.0
        self.help_pinned = False
        self.visible: set[int] = set()
        self.heartbeat = 0.0
        self.last_cam = (0, 0)
        self.notice = ""
        self.notice_time = 0.0
        self.run_recorded = False
        self.cheated = False  # sandbox used this run: it does not count for the records
        self.clock_time = 0.0
        self.run = Run(random.randrange(2**31))
        self.renderer = WorldRenderer(self.run.world, VIEW_WIDTH, VIEW_HEIGHT)
        self.sprite_right, self.sprite_left = build_player_sprites()
        self.creature_sprites = build_creature_sprites()
        self.camera = [0.0, 0.0]
        self.shake = 0.0
        self.sandbox = False
        self.paint_index = 0
        self.brush = BRUSH_DEFAULT
        self.show_help = True
        self.lighting = True
        self.effects_rng = random.Random()
        self.jump_queued = False
        self.pickup_queued = False
        self.drink_queued = False
        self.throw_queued = False
        self.kick_queued = False
        self.shown_depth = -1
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
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
            )

    # ----------------------------------------------------------------- events

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.state != "playing":
                if event.type == pygame.KEYDOWN:
                    self._on_menu_key(event.key)
            elif self.editor.open:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                    self.editor.toggle()
                else:
                    self.editor.handle_event(event, self.run.inventory)
            elif event.type == pygame.KEYDOWN:
                self._on_key(event.key)
            elif event.type == pygame.MOUSEWHEEL:
                if self.sandbox:
                    self.brush = min(max(self.brush + event.y, BRUSH_MIN), BRUSH_MAX)
                else:
                    self.run.inventory.cycle(-event.y)

    def _on_menu_key(self, key: int) -> None:
        if key == pygame.K_F11:
            self.toggle_fullscreen()
        elif self.state == "options":
            self._on_options_key(key)
        elif key == pygame.K_o and self.state in ("title", "paused"):
            self.options_return, self.state, self.options_index = self.state, "options", 0
        elif self.state == "title":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_run()
            elif key == pygame.K_f and self.saved_run is not None:
                self._continue_run()
            elif key == pygame.K_k:
                self.state = "codex"
            elif key == pygame.K_ESCAPE:
                self.running = False
        elif self.state == "codex":
            if key in (pygame.K_ESCAPE, pygame.K_k):
                self.state = "title"
        elif self.state == "paused":
            if key == pygame.K_ESCAPE:
                self.state = "playing"
            elif key == pygame.K_r:
                self._start_run()
            elif key == pygame.K_t:
                self.state = "title"
            elif key == pygame.K_q:
                self.running = False

    def _on_options_key(self, key: int) -> None:
        entries = settings_store.Options.ENTRIES
        if key in (pygame.K_UP, pygame.K_w):
            self.options_index = (self.options_index - 1) % len(entries)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.options_index = (self.options_index + 1) % len(entries)
        elif key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN):
            step = -1 if key in (pygame.K_LEFT, pygame.K_a) else 1
            self.options.change(entries[self.options_index][0], step)
            self._apply_options()
        elif key in (pygame.K_ESCAPE, pygame.K_o):
            settings_store.save(self.options)
            self.state = self.options_return

    def _start_run(self) -> None:
        records.delete_run()  # a new run replaces the saved one
        self.saved_run = None
        self.run.favoured_blocks, self.run.start_pearls = self.records.unlocks()
        self.run.new_run()
        self._begin()

    def _continue_run(self) -> None:
        try:
            self.run.restore(self.saved_run)
        except ValueError:  # from an older, incompatible version: start fresh instead
            self._start_run()
            return
        self.saved_checkpoint = self.run.checkpoint
        self._begin()

    def _begin(self) -> None:
        self._snap_camera()
        self.sandbox = False
        self.cheated = False
        self.run_recorded = False
        self.state = "playing"

    def _record_run(self) -> None:
        """Store a finished run in the persistent records (once per run)."""
        if self.run_recorded or not self.run.outcome:
            return
        self.run_recorded = True
        records.delete_run()  # the run is over: nothing to continue
        self.saved_run = None
        if self.cheated:
            return
        stats = self.run.stats
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

    def _on_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.state = "paused"
        elif key == pygame.K_F11:
            self.toggle_fullscreen()
        elif key == pygame.K_F1:
            self.sandbox = not self.sandbox
            self.cheated = self.cheated or self.sandbox
        elif key == pygame.K_TAB:
            if self.run.can_edit_wands or self.sandbox:
                self.editor.toggle()
            else:
                self.notice, self.notice_time = "Umbauen geht nur im Sanktum.", NOTICE_TIME
        elif key == pygame.K_r:
            self._start_run()
            self._snap_camera()
        elif key == pygame.K_n and self.run.outcome == "victory":
            self.run.new_game_plus()
            self.run_recorded = False  # the next loop is recorded again
            self._snap_camera()
            self.fade = 1.0
        elif key == pygame.K_h:
            shown = self._help_visible()
            self.show_help = not shown
            self.help_pinned = not shown  # shown on request: keep it until H again
        elif key == pygame.K_l:
            self.lighting = self.options.lighting = not self.lighting
        elif key == pygame.K_m:
            self.audio.toggle_mute()
        elif key == pygame.K_e:
            self.pickup_queued = True
        elif key == pygame.K_f:
            self.drink_queued = True
        elif key == pygame.K_t:
            self.throw_queued = True
        elif key == pygame.K_q:
            self.kick_queued = True
        elif key in JUMP_KEYS:
            self.jump_queued = True
        elif key in NUMBER_KEYS:
            number = NUMBER_KEYS.index(key)
            if self.sandbox:
                self.paint_index = number
            else:
                self.run.inventory.select(number)
        elif key == pygame.K_n and self.sandbox:
            self.run.enter_depth(self.run.depth_index)
            self._snap_camera()

    # ----------------------------------------------------------------- update

    def _cursor_in_world(self) -> tuple[int, int]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        view_x, view_y = self.viewport.to_virtual(mouse_x, mouse_y)
        return int(view_x + self.camera[0]), int(view_y + self.camera[1])

    def _sim_area(self) -> tuple[int, int, int, int]:
        x0, y0 = int(self.camera[0]) - SIM_MARGIN, int(self.camera[1]) - SIM_MARGIN
        return (x0, y0, x0 + VIEW_WIDTH + 2 * SIM_MARGIN, y0 + VIEW_HEIGHT + 2 * SIM_MARGIN)

    def update(self, dt: float) -> None:
        self.clock_time += dt
        if self.state in ("title", "codex") or (self.state == "options" and self.options_return == "title"):
            self.audio.play_music("sanktum")
        else:
            self.audio.play_music("sanktum" if self.run.in_sanctum else self.run.depth.key)
        if self.editor.open or self.state != "playing":
            return  # menus and the editor pause the game
        keys = pygame.key.get_pressed()
        left, middle, right = pygame.mouse.get_pressed()
        target = self._cursor_in_world()
        controls = Controls(
            move=int(keys[pygame.K_d] or keys[pygame.K_RIGHT])
            - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            jump=self.jump_queued,
            levitate=bool(keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]),
            cast=bool(left),
            aim=(float(target[0]), float(target[1])),
            pickup=self.pickup_queued,
            pour=bool(right) and not self.sandbox,
            absorb=bool(keys[pygame.K_g]),
            drink=self.drink_queued,
            throw=self.throw_queued,
            kick=self.kick_queued,
        )
        self.jump_queued = self.pickup_queued = self.drink_queued = self.throw_queued = False
        self.kick_queued = False
        if self.sandbox and right:
            self.run.world.paint(*target, self.brush, PAINT_MATERIALS[self.paint_index])
        elif self.sandbox and middle:
            self.run.world.paint(*target, self.brush, mat.AIR)

        depth_before, sanctum_before = self.run.depth_index, self.run.in_sanctum
        for blast in self.run.update(dt, controls, self._sim_area()):
            self._on_blast(blast)
        for event in self.run.events:
            self.audio.play(event)
        self._note_discoveries()
        self._show_messages()
        player = self.run.player
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
        self._save_checkpoint()
        self._record_run()
        self.notice_time = max(0.0, self.notice_time - dt)
        if self.run.depth_index != depth_before or self.run.in_sanctum != sanctum_before:
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
        scaled = pygame.transform.scale(
            self.canvas, (self.viewport.target_width, self.viewport.target_height)
        )
        self.screen.blit(scaled, (self.viewport.offset_x, self.viewport.offset_y))
        if self.fade > 0:
            veil = pygame.Surface(scaled.get_size())
            veil.set_alpha(int(255 * self.fade))
            self.screen.blit(veil, (self.viewport.offset_x, self.viewport.offset_y))
        if self.state == "title":
            pulse = 0.5 + 0.5 * math.sin(self.clock_time * 3) ** 8
            saved = self.saved_run.get("depth_index") if self.saved_run else None
            lines = title_lines(saved + 2 if isinstance(saved, int) else None)
            self.menus.draw_title(self.screen, pulse, self.records.lines_de(), lines)
        elif self.state == "codex":
            self.menus.draw_codex(self.screen, self.records)
        elif self.state == "options":
            self.menus.draw_options(self.screen, self.options, self.options_index)
        else:
            if self.options.damage_numbers:
                self.hud.draw_floaters(self.screen, self.viewport, self.floaters.items, self.last_cam)
            self.hud.draw(self.screen, self.viewport, self._hud_state())
            if self.editor.open:
                self.editor.draw(self.screen, self.run.inventory)
            if self.state == "paused":
                self.menus.draw_pause(self.screen, self._run_summary())
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
        for creature in run.enemies.creatures:
            if creature.spec.boss:
                beat = 0.35 + 0.25 * math.sin(creature.age * 5) ** 8
                lights.append((*creature.center, 110.0, beat))
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
        prompt = ""
        item = run.nearest_pickup()
        if item is not None and not run.player.dead:
            if item.perk is not None:
                prompt = f"E: Wählen - {item.label_de}"
            elif item.price and not run.can_afford(item):
                prompt = f"{item.label_de} - {run.price_of(item)} Blutperlen (zu wenig)"
            elif item.price:
                prompt = f"E: Kaufen - {item.label_de} - {run.price_of(item)} Blutperlen"
            else:
                prompt = f"E: Aufheben - {item.label_de}"
        elif run.near_exit() and not run.exit_open and run.depth.boss:
            prompt = "Der Durchgang ist verschlossen. Besiege den Wächter."
        elif run.near_secret():
            prompt = "Hinter der Wand pulsiert etwas."
        return HudState(
            player=run.player,
            inventory=run.inventory,
            depth_name=run.depth.name_de,
            depth_number=run.next_depth_number,
            depth_total=len(DEPTHS),
            fps=self.clock.get_fps(),
            chunks=run.simulated_chunks,
            show_help=self._help_visible(),
            sandbox=self.sandbox,
            paint_name=mat.NAME_DE[PAINT_MATERIALS[self.paint_index]],
            paint_slot=(self.paint_index + 1) % 10,
            brush=self.brush,
            banner=banner,
            prompt=prompt,
            boss=run.enemies.boss() if run.depth.boss else None,
            outcome="true_victory" if run.true_ending else run.outcome,
            pearls=run.pearls,
            perks=tuple(PERK_BY_KEY[key].name_de for key in sorted(run.perks)),
            stats=self._stats_text(),
            flask=run.flask,
            pulse=math.sin(self.clock_time * HEARTBEAT_RATE * math.pi) ** 8,
            notice=self.notice if self.notice_time > 0 else "",
        )

    def _help_visible(self) -> bool:
        """Control hints: shown at the start of a run, then out of the way (H brings them back)."""
        return self.show_help and (self.help_pinned or self.run.stats["time"] < HELP_TIME)

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
            lines.append("Sandbox benutzt: dieser Lauf zählt nicht für Statistik und Kodex.")
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
        draw_pickups(self.canvas, run.pickups, cam_x, cam_y)
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
        draw_creatures(
            self.canvas, self.creature_sprites, run.enemies.creatures, cam_x, cam_y,
            None if self.sandbox else self.visible,
        )  # fmt: skip
        for body in (player, *run.enemies.creatures):
            if not body.dead:
                draw_status(self.canvas, body, cam_x, cam_y, self.effects_rng)
        draw_projectiles(self.canvas, run.projectiles.items, cam_x, cam_y)
        if self.sandbox:
            pygame.draw.circle(
                self.canvas, (230, 220, 200), (target[0] - cam_x, target[1] - cam_y), self.brush, 1
            )
        else:
            x, y = target[0] - cam_x, target[1] - cam_y
            for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
                self.canvas.fill((230, 220, 200), (x + dx, y + dy, 1, 1))

    # ------------------------------------------------------------------- loop

    def run_loop(self) -> None:
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.1)
            self.handle_events()
            self.update(dt)
            self.draw()

        records.save(self.records)  # Kodex finds since the last checkpoint
        pygame.quit()
        sys.exit(0)


def main() -> None:
    game = Game()
    game.run_loop()


if __name__ == "__main__":
    main()
