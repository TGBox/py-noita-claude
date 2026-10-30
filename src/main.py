"""Game loop and entry point."""

from __future__ import annotations

import random
import sys

import pygame

from src import materials as mat
from src.player import MAX_ENERGY, MAX_HP, PLAYER_HEIGHT, PLAYER_WIDTH, Player
from src.rendering import WorldRenderer
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
# Keys 1-8 select what the right mouse button paints.
PAINT_MATERIALS = (
    mat.SAND,
    mat.WATER,
    mat.OIL,
    mat.STONE,
    mat.WOOD,
    mat.LAVA,
    mat.FIRE,
    mat.AIR,
)
JUMP_KEYS = (pygame.K_w, pygame.K_UP, pygame.K_SPACE)
BOLT_COLOR = (255, 240, 150)
ROBE_COLOR = (112, 62, 168)
SKIN_COLOR = (236, 196, 160)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(None, 36)
        self.info_font = pygame.font.SysFont(None, 24)

        self.viewport = Viewport(VIEW_WIDTH, VIEW_HEIGHT)
        self.canvas = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
        self.world = World(WORLD_WIDTH, WORLD_HEIGHT)
        self.renderer = WorldRenderer(self.world)
        self.player = Player(0, 0)
        self.wand = Wand()
        self.bolts: list[Bolt] = []
        self.camera = [0.0, 0.0]
        self.paint_index = 0
        self.brush = BRUSH_DEFAULT
        self.sim_accumulator = 0.0
        self.jump_queued = False
        self.spawn = (0, 0)
        self.new_world()

    # ------------------------------------------------------------------ state

    def new_world(self) -> None:
        """Generate a fresh level and put the player into it."""
        self.world.rng.seed(random.randrange(2**31))
        self.world.frame = 0
        self.spawn = generate_world(self.world)
        self.respawn()

    def respawn(self) -> None:
        self.player.reset(*self.spawn)
        self.bolts.clear()
        self.camera = [0.0, 0.0]
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
        elif pygame.K_1 <= key < pygame.K_1 + len(PAINT_MATERIALS):
            self.paint_index = key - pygame.K_1

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
        left, _middle, right = pygame.mouse.get_pressed()
        self.wand.update(dt)
        if left and not self.player.dead:
            bolt = self.wand.try_fire(self.player.center, (target_x, target_y))
            if bolt is not None:
                self.bolts.append(bolt)
        if right:
            self.world.paint(target_x, target_y, self.brush, PAINT_MATERIALS[self.paint_index])

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
        """Run the world at a fixed rate, independent of the frame rate."""
        self.sim_accumulator += dt
        steps = 0
        while self.sim_accumulator >= SIM_DT and steps < MAX_SIM_STEPS_PER_FRAME:
            self.world.step()
            self.sim_accumulator -= SIM_DT
            steps += 1
        if steps == MAX_SIM_STEPS_PER_FRAME:
            self.sim_accumulator = 0.0  # too slow: drop time instead of spiralling

    # ------------------------------------------------------------------- draw

    def draw(self) -> None:
        self.renderer.refresh(self.world)
        cam_x, cam_y = int(self.camera[0]), int(self.camera[1])
        self.canvas.blit(
            self.renderer.surface, (0, 0), pygame.Rect(cam_x, cam_y, VIEW_WIDTH, VIEW_HEIGHT)
        )
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
        body = pygame.Rect(player.x - cam_x, player.y - cam_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        pygame.draw.rect(self.canvas, ROBE_COLOR, body)
        pygame.draw.rect(self.canvas, SKIN_COLOR, (body.x + 1, body.y, 3, 3))
        for bolt in self.bolts:
            pygame.draw.rect(self.canvas, BOLT_COLOR, (int(bolt.x) - cam_x - 1, int(bolt.y) - cam_y - 1, 2, 2))
        target_x, target_y = self._cursor_in_world()
        pygame.draw.circle(
            self.canvas, (255, 255, 255), (target_x - cam_x, target_y - cam_y), self.brush, 1
        )

    def _draw_hud(self) -> None:
        left, top = self.viewport.offset_x + 12, self.viewport.offset_y + 10
        self._draw_bar(left, top, 160, 12, self.player.hp / MAX_HP, COLOR_ACCENT)
        self._draw_bar(left, top + 18, 160, 8, self.player.energy / MAX_ENERGY, (90, 200, 250))
        material = mat.NAME_DE[PAINT_MATERIALS[self.paint_index]]
        lines = (
            f"Pinsel: {material} ({self.paint_index + 1}) | Größe {self.brush} | "
            f"FPS {self.clock.get_fps():.0f}",
            "A/D: Laufen | W/Leertaste: Springen & Schweben | Linke Maus: Zauberstab",
            "Rechte Maus: Malen | 1-8: Material | Mausrad: Größe | R: Neustart | "
            "N: Neue Welt | F11 | ESC",
        )
        for index, text in enumerate(lines):
            surface = self.info_font.render(text, True, COLOR_TEXT)
            self.screen.blit(surface, (left, top + 36 + index * 18))
        if self.player.dead:
            text = self.font.render("Du bist gestorben - R zum Wiederbeleben", True, COLOR_ACCENT)
            rect = text.get_rect(center=self.screen.get_rect().center)
            self.screen.blit(text, rect)

    def _draw_bar(self, x: int, y: int, width: int, height: int, fraction: float, color: tuple[int, int, int]) -> None:
        fraction = min(max(fraction, 0.0), 1.0)
        pygame.draw.rect(self.screen, (40, 40, 52), (x, y, width, height))
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
