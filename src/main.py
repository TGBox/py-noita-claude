"""Game loop and entry point."""

from __future__ import annotations

import math
import random
import sys

import pygame

from src import materials as mat
from src.player import MAX_ENERGY, MAX_HP, Player
from src.rendering import WorldRenderer, build_player_sprites
from src.settings import (
    BRUSH_DEFAULT,
    BRUSH_MAX,
    BRUSH_MIN,
    COLOR_ACCENT,
    COLOR_BACKGROUND,
    COLOR_TEXT,
    FPS,
    MAX_SIM_STEPS_PER_FRAME,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SIM_HZ,
    SIM_MARGIN,
    TITLE,
    VIEW_HEIGHT,
    VIEW_WIDTH,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from src.viewport import Viewport
from src.wand import Bolt, Wand
from src.world import World
from src.worldgen import generate_world

SIM_DT = 1.0 / SIM_HZ
CAMERA_FOLLOW = 8.0  # 1/s, higher is snappier
# Keys 1-9 and 0 select what the right mouse button paints.
PAINT_MATERIALS = (
    mat.BONE_DUST,
    mat.BLOOD,
    mat.TALLOW,
    mat.ACID,
    mat.FLESH,
    mat.BONE,
    mat.SINEW,
    mat.FIRE,
    mat.GROWTH,
    mat.SPORES,
)
PAINT_KEYS = (
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
)  # fmt: skip
JUMP_KEYS = (pygame.K_w, pygame.K_UP, pygame.K_SPACE)
BOLT_COLOR = (255, 226, 170)
WAND_COLOR = (176, 160, 130)
WAND_LENGTH = 9


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(None, 40)
        self.info_font = pygame.font.SysFont(None, 22)

        self.viewport = Viewport(VIEW_WIDTH, VIEW_HEIGHT)
        self.canvas = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
        self.world = World(WORLD_WIDTH, WORLD_HEIGHT)
        self.renderer = WorldRenderer(self.world, VIEW_WIDTH, VIEW_HEIGHT)
        self.sprite_right, self.sprite_left = build_player_sprites()
        self.player = Player(0, 0)
        self.wand = Wand()
        self.bolts: list[Bolt] = []
        self.camera = [0.0, 0.0]
        self.paint_index = 0
        self.brush = BRUSH_DEFAULT
        self.sim_accumulator = 0.0
        self.simulated_chunks = 0
        self.jump_queued = False
        self.spawn = (0, 0)
        self.new_world()

    # ------------------------------------------------------------------ state

    def new_world(self) -> None:
        """Generate a fresh level and put the player into it."""
        self.world.reseed(random.randrange(2**31))
        self.world.frame = 0
        self.spawn = generate_world(self.world)
        self.respawn()

    def respawn(self) -> None:
        self.player.reset(*self.spawn)
        self.bolts.clear()
        self._snap_camera()

    def _snap_camera(self) -> None:
        cx, cy = self.player.center
        self.camera = [cx - VIEW_WIDTH / 2, cy - VIEW_HEIGHT / 2]
        self._clamp_camera()

    def _clamp_camera(self) -> None:
        self.camera[0] = min(max(self.camera[0], 0.0), WORLD_WIDTH - VIEW_WIDTH)
        self.camera[1] = min(max(self.camera[1], 0.0), WORLD_HEIGHT - VIEW_HEIGHT)

    def toggle_fullscreen(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
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
            elif event.type == pygame.KEYDOWN:
                self._on_key(event.key)
            elif event.type == pygame.MOUSEWHEEL:
                self.brush = min(max(self.brush + event.y, BRUSH_MIN), BRUSH_MAX)

    def _on_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_F11:
            self.toggle_fullscreen()
        elif key == pygame.K_r:
            self.respawn()
        elif key == pygame.K_n:
            self.new_world()
        elif key in JUMP_KEYS:
            self.jump_queued = True
        elif key in PAINT_KEYS:
            self.paint_index = PAINT_KEYS.index(key)

    # ----------------------------------------------------------------- update

    def _cursor_in_world(self) -> tuple[int, int]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        view_x, view_y = self.viewport.to_virtual(mouse_x, mouse_y)
        return int(view_x + self.camera[0]), int(view_y + self.camera[1])

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        levitate = bool(keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE])
        self.player.update(self.world, dt, move, self.jump_queued, levitate)
        self.jump_queued = False

        target_x, target_y = self._cursor_in_world()
        left, middle, right = pygame.mouse.get_pressed()
        self.wand.update(dt)
        if left and not self.player.dead:
            bolt = self.wand.try_fire(self.player.center, (target_x, target_y))
            if bolt is not None:
                self.bolts.append(bolt)
        if right:
            self.world.paint(target_x, target_y, self.brush, PAINT_MATERIALS[self.paint_index])
        elif middle:
            self.world.paint(target_x, target_y, self.brush, mat.AIR)

        self._step_simulation(dt)
        for bolt in self.bolts:
            bolt.update(self.world, dt)
        self.bolts = [bolt for bolt in self.bolts if bolt.alive]

        cx, cy = self.player.center
        follow = min(1.0, CAMERA_FOLLOW * dt)
        self.camera[0] += (cx - VIEW_WIDTH / 2 - self.camera[0]) * follow
        self.camera[1] += (cy - VIEW_HEIGHT / 2 - self.camera[1]) * follow
        self._clamp_camera()

    def _step_simulation(self, dt: float) -> None:
        """Run the world at a fixed rate near the camera, independent of the frame rate."""
        x0, y0 = int(self.camera[0]) - SIM_MARGIN, int(self.camera[1]) - SIM_MARGIN
        area = (x0, y0, x0 + VIEW_WIDTH + 2 * SIM_MARGIN, y0 + VIEW_HEIGHT + 2 * SIM_MARGIN)
        self.sim_accumulator += dt
        steps = 0
        while self.sim_accumulator >= SIM_DT and steps < MAX_SIM_STEPS_PER_FRAME:
            self.simulated_chunks = self.world.step(area)
            self.sim_accumulator -= SIM_DT
            steps += 1
        if steps == MAX_SIM_STEPS_PER_FRAME:
            self.sim_accumulator = 0.0  # too slow: drop time instead of spiralling

    # ------------------------------------------------------------------- draw

    def draw(self) -> None:
        cam_x, cam_y = int(self.camera[0]), int(self.camera[1])
        self.renderer.refresh(self.world, cam_x, cam_y)
        self.canvas.blit(self.renderer.surface, (0, 0))
        self._draw_entities(cam_x, cam_y)

        self.screen = pygame.display.get_surface()
        self.viewport.resize(*self.screen.get_size())
        self.screen.fill(COLOR_BACKGROUND)
        scaled = pygame.transform.scale(
            self.canvas, (self.viewport.target_width, self.viewport.target_height)
        )
        self.screen.blit(scaled, (self.viewport.offset_x, self.viewport.offset_y))
        self._draw_hud()
        pygame.display.flip()

    def _draw_entities(self, cam_x: int, cam_y: int) -> None:
        player = self.player
        target_x, target_y = self._cursor_in_world()
        hand_x, hand_y = player.center
        facing_right = target_x >= hand_x
        sprite = self.sprite_right if facing_right else self.sprite_left
        if not player.dead:
            self.canvas.blit(sprite, (player.x - cam_x, player.y - cam_y))
            angle = math.atan2(target_y - hand_y, target_x - hand_x)
            start = (hand_x - cam_x, hand_y - cam_y + 1)
            tip = (
                start[0] + math.cos(angle) * WAND_LENGTH,
                start[1] + math.sin(angle) * WAND_LENGTH,
            )
            pygame.draw.line(self.canvas, WAND_COLOR, start, tip)
        for bolt in self.bolts:
            x, y = int(bolt.x) - cam_x, int(bolt.y) - cam_y
            pygame.draw.rect(self.canvas, BOLT_COLOR, (x - 1, y - 1, 3, 3))
        pygame.draw.circle(
            self.canvas, (230, 220, 200), (target_x - cam_x, target_y - cam_y), self.brush, 1
        )

    def _draw_hud(self) -> None:
        left, top = self.viewport.offset_x + 14, self.viewport.offset_y + 12
        self._draw_bar(left, top, 180, 12, self.player.hp / MAX_HP, COLOR_ACCENT)
        self._draw_bar(left, top + 18, 180, 7, self.player.energy / MAX_ENERGY, (176, 160, 130))
        material = mat.NAME_DE[PAINT_MATERIALS[self.paint_index]]
        slot = (self.paint_index + 1) % 10
        lines = (
            f"Pinsel: {material} ({slot}) | Größe {self.brush} | "
            f"FPS {self.clock.get_fps():.0f} | aktive Chunks {self.simulated_chunks}",
            "A/D: Laufen | W/Leertaste: Springen, halten zum Schweben | Linke Maus: Zauberstab",
            "Rechte Maus: Malen | Mittlere Maus: Radieren | 1-0: Material | Mausrad: Größe",
            "R: Wiederbeleben | N: Neue Welt | F11: Vollbild | ESC: Beenden",
        )
        for index, text in enumerate(lines):
            surface = self.info_font.render(text, True, COLOR_TEXT)
            self.screen.blit(surface, (left, top + 34 + index * 18))
        if self.player.dead:
            text = self.font.render("Du bist gestorben - R zum Wiederbeleben", True, COLOR_ACCENT)
            rect = text.get_rect(center=self.screen.get_rect().center)
            self.screen.blit(text, rect)

    def _draw_bar(
        self, x: int, y: int, width: int, height: int, fraction: float, color: tuple[int, int, int]
    ) -> None:
        fraction = min(max(fraction, 0.0), 1.0)
        pygame.draw.rect(self.screen, (34, 22, 26), (x, y, width, height))
        pygame.draw.rect(self.screen, color, (x, y, int(width * fraction), height))

    # ------------------------------------------------------------------- loop

    def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.1)
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit(0)


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
