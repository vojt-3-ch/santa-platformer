"""
Constants and configuration values for Santa Platformer game.
This module centralizes all magic numbers and configuration values for easy maintenance.
"""

from pathlib import Path

# =============================================================================
# DISPLAY CONSTANTS
# =============================================================================

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Game performance
FPS = 60

# =============================================================================
# PLAYER CONSTANTS
# =============================================================================

# Player physics
GRAVITY = 0.6          # px/frame^2 - Controls downward acceleration
MAX_FALL = 15          # Terminal velocity - Maximum falling speed
BASE_SPEED = 5         # px/frame - Normal movement speed
BASE_JUMP = -13        # px/frame - Jump strength (negative = upward)

# Player dimensions
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

# Player starting state
STARTING_LIVES = 3

# =============================================================================
# GAME MECHANICS
# =============================================================================

# Lives system
MAX_LIVES = 3

# Level system
LEVEL_COUNT = 2  # Total number of levels in the game

# =============================================================================
# ANIMATION TIMINGS
# =============================================================================

# Animation frame duration in milliseconds
IDLE_FRAME_DURATION = 200  # ms per idle frame (not directly used but for reference)
WALK_FRAME_DURATION = 200  # ms per walk frame

# =============================================================================
# POWER-UP DURATIONS (in milliseconds)
# =============================================================================

DOUBLE_JUMP_DURATION = 15000   # 15 seconds
SPEED_BOOST_DURATION = 8000    # 8 seconds
INVINCIBILITY_DURATION = 6000  # 6 seconds

# Power-up effects
SPEED_BOOST_MULTIPLIER = 1.8   # Speed multiplier during speed boost

# =============================================================================
# INVINCIBILITY TIMINGS (in milliseconds)
# =============================================================================

RESPAWN_INVINCIBILITY_DURATION = 1200  # Brief invincibility after respawn
HIT_INVINCIBILITY_FLICKER = 150        # Flicker interval for invincibility effect

# =============================================================================
# MESSAGE DISPLAY TIMINGS (in milliseconds)
# =============================================================================

MESSAGE_DURATION_SHORT = 900      # Short messages (present collected, lost life)
MESSAGE_DURATION_MEDIUM = 1100    # Medium messages (powerup notifications)
MESSAGE_DURATION_LONG = 1300      # Long messages (collect all presents warning)
MESSAGE_DURATION_GAME_OVER = 2000 # Game over message
LEVEL_COMPLETE_DELAY = 3000       # Delay before advancing to next level

# =============================================================================
# UI/HUD CONSTANTS
# =============================================================================

# HUD positioning and spacing
HUD_MARGIN = 10
HUD_LINE_HEIGHT = 24
HUD_TEXT_SIZE = 22

# =============================================================================
# LEVEL/GAME WORLD CONSTANTS
# =============================================================================

# Ground properties
GROUND_HEIGHT = 40

# Camera behavior
CAMERA_DEADZONE = 0  # Currently no deadzone, camera follows immediately

# =============================================================================
# ASSET PATHS
# =============================================================================

# Directory containing game assets (images, sounds, etc.)
ASSETS_DIR = Path("assets")

# =============================================================================
# FALLBACK COLORS (used when texture loading fails)
# =============================================================================

# RGB color values for procedural texture generation
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (200, 40, 40)
COLOR_GREEN = (20, 120, 20)
COLOR_BROWN = (139, 69, 19)      # Platform color
COLOR_GOLD = (255, 215, 0)       # Present color
COLOR_SNOW_WHITE = (245, 245, 245)  # Enemy color
COLOR_PURPLE = (150, 50, 200)    # Double jump power-up
COLOR_BLUE = (50, 120, 255)      # Speed boost power-up
COLOR_YELLOW = (255, 200, 60)    # Invincibility power-up
COLOR_GRAY = (120, 120, 120)     # Default fallback color

# Color mapping for texture generation
FALLBACK_COLORS = {
    'player': COLOR_RED,
    'platform': COLOR_BROWN,
    'present': COLOR_GOLD,
    'enemy': COLOR_SNOW_WHITE,
    'tree': COLOR_GREEN,
    'double_jump': COLOR_PURPLE,
    'speed_boost': COLOR_BLUE,
    'invincibility': COLOR_YELLOW,
}

# =============================================================================
# BACKGROUND COLORS
# =============================================================================

# Fallback background colors when background image fails to load
FALLBACK_BACKGROUND_COLOR = (50, 50, 100)  # Dark blue-gray
GAME_OVER_BACKGROUND_COLOR = (10, 10, 40)  # Darker blue for game over
FALLBACK_SCREEN_COLOR = (24, 36, 60)      # Dark blue for main game area

# =============================================================================
# OVERLAY CONSTANTS
# =============================================================================

# Semi-transparent overlay for depth effect
OVERLAY_ALPHA = 120  # Alpha value for dark overlay (0-255)