"""Game configuration and global constants."""

# Display settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Cloita"

# Virtual resolution: one world cell is one pixel; the picture is scaled to the
# window without distortion.
VIEW_WIDTH = 640
VIEW_HEIGHT = 360

# World and simulation
WORLD_WIDTH = 1280
WORLD_HEIGHT = 720
SIM_HZ = 60
MAX_SIM_STEPS_PER_FRAME = 3
SIM_MARGIN = 96  # cells simulated beyond the visible area on every side

# Sandbox brush
BRUSH_MIN = 1
BRUSH_MAX = 24
BRUSH_DEFAULT = 6

# Color palette (RGB)
COLOR_BACKGROUND = (8, 4, 6)
COLOR_PRIMARY = (180, 30, 40)
COLOR_TEXT = (214, 200, 182)
COLOR_ACCENT = (200, 28, 36)
