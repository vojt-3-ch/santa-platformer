"""
Level definitions and configurations for Santa Platformer game.

This module contains all level data structures, platform layouts, enemy placements,
power-up locations, present placements, and level metadata. It's designed to be
easily extensible for adding new levels and provides clean data structures for
use by the level management system.

Import necessary constants from constants.py for consistency across the game.
"""

from pathlib import Path
from constants import (
    # Asset paths
    ASSETS_DIR,
    # Fallback colors
    FALLBACK_BACKGROUND_COLOR,
    OVERLAY_ALPHA,
    # Ground properties
    GROUND_HEIGHT,
)


# =============================================================================
# LEVEL DATA STRUCTURES
# =============================================================================

def create_level_data(
    name,
    width,
    height,
    player_start,
    goal,
    platforms,
    presents,
    enemies=None,
    powerups=None,
    background_name=None
):
    """
    Helper function to create a level data dictionary with consistent structure.

    Args:
        name (str): Display name for the level
        width (int): Level width in pixels
        height (int): Level height in pixels
        player_start (tuple): (x, y) starting position for player
        goal (tuple): (x, y, width, height) goal/tree position and size
        platforms (list): List of (x, y, width, height) platform rectangles
        presents (list): List of (x, y, width, height) present positions
        enemies (list, optional): List of enemy data tuples
        powerups (list, optional): List of powerup dictionaries
        background_name (str, optional): Background image filename (without extension)

    Returns:
        dict: Complete level data dictionary
    """
    return {
        "name": name,
        "width": width,
        "height": height,
        "player_start": player_start,
        "goal": goal,
        "platforms": platforms,
        "presents": presents,
        "enemies": enemies or [],
        "powerups": powerups or [],
        "background_name": background_name,
        "ground": (0, height - GROUND_HEIGHT, width, GROUND_HEIGHT),
    }


# =============================================================================
# LEVEL DEFINITIONS
# =============================================================================

LEVELS = [
    create_level_data(
        name="Snowy Village",
        width=1600,
        height=600,
        player_start=(80, 480),
        goal=(1500, 480, 60, 80),  # tree position and size
        platforms=[
            (200, 430, 160, 20),
            (420, 330, 160, 20),
            (700, 460, 200, 20),
            (1100, 380, 200, 20),
            (1350, 300, 180, 20),
        ],
        presents=[
            (220, 400, 30, 30),
            (460, 300, 30, 30),
            (760, 430, 30, 30),
            (1120, 350, 30, 30),
            (1370, 270, 30, 30),
        ],
        enemies=[
            # x, y, w, h, patrol_min_x, patrol_max_x, speed
            (600, 520, 40, 40, 500, 740, 2),
            (1300, 340, 40, 40, 1250, 1450, 1.5),
        ],
        powerups=[
            {"rect": (520, 480, 24, 24), "type": "double_jump"},
            {"rect": (900, 420, 24, 24), "type": "speed_boost"},
        ],
        background_name="bckg1"
    ),

    create_level_data(
        name="Icicle Climb",
        width=1200,
        height=800,
        player_start=(60, 700),
        goal=(1100, 700, 60, 80),
        platforms=[
            (150, 640, 130, 20),
            (320, 520, 130, 20),
            (510, 400, 130, 20),
            (720, 280, 130, 20),
            (920, 160, 130, 20),
        ],
        presents=[
            (170, 510, 30, 30),
            (340, 490, 30, 30),
            (530, 370, 30, 30),
            (740, 250, 30, 30),
            (940, 130, 30, 30),
        ],
        enemies=[
            (400, 720, 40, 40, 300, 520, 2.2),
            (800, 720, 40, 40, 760, 980, 1.7),
        ],
        powerups=[
            {"rect": (600, 360, 24, 24), "type": "invincibility"},
        ],
        background_name="bckg2"
    )
]


# =============================================================================
# LEVEL METADATA AND CONFIGURATION
# =============================================================================

class LevelMetadata:
    """Container for level metadata and helper functions."""

    def __init__(self, levels_data):
        self.levels_data = levels_data
        self.total_levels = len(levels_data)

    def get_level(self, index):
        """Get level data by index with bounds checking."""
        if 0 <= index < self.total_levels:
            return self.levels_data[index]
        raise IndexError(f"Level index {index} out of range (0-{self.total_levels-1})")

    def get_level_by_name(self, name):
        """Get level data by name."""
        for level in self.levels_data:
            if level["name"] == name:
                return level
        raise ValueError(f"Level '{name}' not found")

    def get_background_path(self, level_index):
        """Get the background image path for a level."""
        level = self.get_level(level_index)
        bg_name = level.get("background_name")
        if bg_name:
            return ASSETS_DIR / f"{bg_name}.png"
        return None

    def get_present_textures(self):
        """Get list of available present textures."""
        return ["present", "present1", "present2", "present3"]

    def get_powerup_types(self):
        """Get list of available powerup types."""
        return ["double_jump", "speed_boost", "invincibility"]

    def get_powerup_durations(self):
        """Get default durations for powerups in milliseconds."""
        return {
            "double_jump": 15000,    # 15 seconds
            "speed_boost": 8000,     # 8 seconds
            "invincibility": 6000    # 6 seconds
        }


# =============================================================================
# LEVEL VALIDATION AND UTILITIES
# =============================================================================

def validate_level_data(level_data):
    """
    Validate that level data has all required fields and correct structure.

    Args:
        level_data (dict): Level data dictionary to validate

    Returns:
        bool: True if valid, False otherwise

    Raises:
        ValueError: If required fields are missing or invalid
    """
    required_fields = [
        "name", "width", "height", "player_start", "goal",
        "platforms", "presents", "enemies", "powerups"
    ]

    for field in required_fields:
        if field not in level_data:
            raise ValueError(f"Missing required field: {field}")

    # Validate field types and structures
    if not isinstance(level_data["name"], str):
        raise ValueError("Level name must be a string")

    if not isinstance(level_data["width"], int) or level_data["width"] <= 0:
        raise ValueError("Level width must be a positive integer")

    if not isinstance(level_data["height"], int) or level_data["height"] <= 0:
        raise ValueError("Level height must be a positive integer")

    if not isinstance(level_data["player_start"], (tuple, list)) or len(level_data["player_start"]) != 2:
        raise ValueError("Player start must be a tuple/list of (x, y)")

    if not isinstance(level_data["goal"], (tuple, list)) or len(level_data["goal"]) != 4:
        raise ValueError("Goal must be a tuple/list of (x, y, width, height)")

    if not isinstance(level_data["platforms"], (tuple, list)):
        raise ValueError("Platforms must be a tuple/list")

    if not isinstance(level_data["presents"], (tuple, list)):
        raise ValueError("Presents must be a tuple/list")

    if not isinstance(level_data["enemies"], (tuple, list)):
        raise ValueError("Enemies must be a tuple/list")

    if not isinstance(level_data["powerups"], (tuple, list)):
        raise ValueError("Powerups must be a tuple/list")

    return True


def create_empty_level(name="New Level", width=800, height=600):
    """
    Create a template for a new level with default values.

    Args:
        name (str): Name for the new level
        width (int): Level width in pixels
        height (int): Level height in pixels

    Returns:
        dict: Empty level template
    """
    return create_level_data(
        name=name,
        width=width,
        height=height,
        player_start=(50, height - 100),  # Start near left edge, above ground
        goal=(width - 100, height - 100, 60, 80),  # Goal near right edge
        platforms=[
            # Add default platforms here
            (200, height - 150, 150, 20),
            (400, height - 250, 150, 20),
            (600, height - 200, 150, 20),
        ],
        presents=[
            # Add default present positions here
            (220, height - 180, 30, 30),
            (420, height - 280, 30, 30),
            (620, height - 230, 30, 30),
        ],
        enemies=[
            # Add default enemies here (x, y, w, h, patrol_min_x, patrol_max_x, speed)
            # (300, height - 100, 40, 40, 250, 450, 2),
        ],
        powerups=[
            # Add default powerups here
            # {"rect": (350, height - 200, 24, 24), "type": "double_jump"},
        ]
    )


# =============================================================================
# INITIALIZATION
# =============================================================================

# Create level metadata instance for easy access to level utilities
level_metadata = LevelMetadata(LEVELS)

# Validate all levels on module import
for i, level in enumerate(LEVELS):
    try:
        validate_level_data(level)
    except ValueError as e:
        print(f"Warning: Level {i} ({level.get('name', 'Unknown')}) has invalid data: {e}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "LEVELS",
    "LevelMetadata",
    "level_metadata",
    "create_level_data",
    "validate_level_data",
    "create_empty_level",
]