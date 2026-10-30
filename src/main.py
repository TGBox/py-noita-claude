"""Game loop and entry point."""

from __future__ import annotations

import math
import random
import sys

import pygame

from src import materials as mat
from src.hud import Hud, HudState
from src.player import Player
from src.projectiles import Blast, ProjectileSystem
from src.rendering import (
    WorldRenderer,
    build_player_sprites,
    draw_augmentation,
    draw_projectiles,
)
from src.settings import (
    BRUSH_DEFAULT,
    BRUSH_MAX,
    BRUSH_MIN,
    COLOR_BACKGROUND,
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
from src.wand import PRESETS, Wand
from src.world import World
from src.worldgen import generate_world

SIM_DT = 1.0 / SIM_HZ
CAMERA_FOLLOW = 8.0  # 1/s, higher is snappier
SHAKE_DECAY = 18.0  # 1/s
BLAST_DAMAGE = 3.0  # damage per blast radius cell at point blank
BLAST_REACH = 6  # cells beyond the blast radius that still hurt
SHOULDER_OFFSET = (2.0, 1.0)  # arm root relative to the body centre (x towards the aim)
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
        self.world = World(WORLD_WIDTH, WORLD_HEIGHT)
        self.renderer = WorldRenderer(self.world, VIEW_WIDTH, VIEW_HEIGHT)
        self.sprite_right, self.sprite_left = build_player_sprites()
        self.player = Player(0, 0)
        self.wands = [Wand(spec) for spec in PRESETS]
        self.wand_index = 0
        self.projectiles = ProjectileSystem()
        self.camera = [0.0, 0.0]
        self.shake = 0.0
        self.paint_index = 0
        self.brush = BRUSH_DEFAULT
        self.show_help = True
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
        self.projectiles.clear()
        self.wands = [Wand(spec) for spec in PRESETS]
        self._snap_camera()

    @property
    def wand(self) -> Wand:
        return self.wands[self.wand_index]

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
        elif key == pygame.K_h:
            self.show_help = not self.show_help
        elif key == pygame.K_q:
            self.wand_index = (self.wand_index - 1) % len(self.wands)
        elif key == pygame.K_e:
            self.wand_index = (self.wand_index + 1) % len(self.wands)
        elif key in JUMP_KEYS:
            self.jump_queued = True
        elif key in PAINT_KEYS:
            self.paint_index = PAINT_KEYS.index(key)

    # ----------------------------------------------------------------- update

    def _cursor_in_world(self) -> tuple[int, int]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        view_x, view_y = self.viewport.to_virtual(mouse_x, mouse_y)
        return int(view_x + self.camera[0]), int(view_y + self.camera[1])

    def _shoulder(self) -> tuple[float, float]:
        cx, cy = self.player.center
        target_x, _ = self._cursor_in_world()
        side = 1 if target_x >= cx else -1
        return cx + SHOULDER_OFFSET[0] * side, cy + SHOULDER_OFFSET[1]

    def _aim_angle(self) -> float:
        target_x, target_y = self._cursor_in_world()
        sx, sy = self._shoulder()
        return math.atan2(target_y - sy, target_x - sx)

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        levitate = bool(keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE])
        self.player.update(self.world, dt, move, self.jump_queued, levitate)
        self.jump_queued = False

        target = self._cursor_in_world()
        left, middle, right = pygame.mouse.get_pressed()
        for wand in self.wands:
            wand.update(dt)
        if left and not self.player.dead:
            self._cast()
        if right:
            self.world.paint(*target, self.brush, PAINT_MATERIALS[self.paint_index])
        elif middle:
            self.world.paint(*target, self.brush, mat.AIR)

        self._step_simulation(dt)
        for blast in self.projectiles.update(self.world, dt, target):
            self._on_blast(blast)

        cx, cy = self.player.center
        follow = min(1.0, CAMERA_FOLLOW * dt)
        self.camera[0] += (cx - VIEW_WIDTH / 2 - self.camera[0]) * follow
        self.camera[1] += (cy - VIEW_HEIGHT / 2 - self.camera[1]) * follow
        self._clamp_camera()
        self.shake = max(0.0, self.shake - SHAKE_DECAY * dt)

    def _cast(self) -> None:
        shots = self.wand.cast()
        if not shots:
            return
        angle = self._aim_angle() + random.uniform(-1, 1) * self.wand.spec.spread
        sx, sy = self._shoulder()
        reach = 7 + len(self.wand.blocks) * 1.5  # spawn at the arm's tip
        self.projectiles.spawn(
            shots, sx + math.cos(angle) * reach, sy + math.sin(angle) * reach, angle
        )

    def _on_blast(self, blast: Blast) -> None:
        self.shake = min(6.0, self.shake + blast.radius / 3)
        cx, cy = self.player.center
        distance = math.hypot(cx - blast.x, cy - blast.y)
        reach = blast.radius + BLAST_REACH
        if distance < reach:
            self.player.hurt(BLAST_DAMAGE * blast.radius * (1 - distance / reach))

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
        jitter_x = random.uniform(-self.shake, self.shake)
        jitter_y = random.uniform(-self.shake, self.shake)
        cam_x = int(min(max(self.camera[0] + jitter_x, 0), WORLD_WIDTH - VIEW_WIDTH))
        cam_y = int(min(max(self.camera[1] + jitter_y, 0), WORLD_HEIGHT - VIEW_HEIGHT))
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
        self.hud.draw(
            self.screen,
            self.viewport,
            HudState(
                player=self.player,
                wands=self.wands,
                wand_index=self.wand_index,
                paint_name=mat.NAME_DE[PAINT_MATERIALS[self.paint_index]],
                paint_slot=(self.paint_index + 1) % 10,
                brush=self.brush,
                fps=self.clock.get_fps(),
                chunks=self.simulated_chunks,
                show_help=self.show_help,
            ),
        )
        pygame.display.flip()

    def _draw_entities(self, cam_x: int, cam_y: int) -> None:
        player = self.player
        target_x, target_y = self._cursor_in_world()
        if not player.dead:
            facing_right = target_x >= player.center[0]
            sprite = self.sprite_right if facing_right else self.sprite_left
            self.canvas.blit(sprite, (player.x - cam_x, player.y - cam_y))
            sx, sy = self._shoulder()
            draw_augmentation(self.canvas, (sx - cam_x, sy - cam_y), self._aim_angle(), self.wand)
        draw_projectiles(self.canvas, self.projectiles.items, cam_x, cam_y)
        pygame.draw.circle(
            self.canvas, (230, 220, 200), (target_x - cam_x, target_y - cam_y), self.brush, 1
        )

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
