"""
Level management system for Santa Platformer game.

This module provides comprehensive level management functionality including:
- LevelManager class for multi-level support and progression
- Dynamic asset loading for backgrounds, platforms, enemies, power-ups
- Level state tracking including completion status and current level index
- Level progression logic and victory conditions
- Object creation functions for platforms, enemies, power-ups, and presents

The module integrates with:
- constants.py for game configuration
- assets.py for texture loading
- levels.py for level data structures
- enemy.py for Enemy class
"""

import pygame
import random
from pathlib import Path

# Import required modules
from constants import (
    ASSETS_DIR,
    FALLBACK_BACKGROUND_COLOR,
    OVERLAY_ALPHA,
    GROUND_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from assets import get_texture
from enemy import Enemy
from levels import LEVELS, LevelMetadata, level_metadata


class LevelManager:
    """
    Comprehensive level management system for Santa Platformer.

    Handles level loading, object creation, asset management, and progression logic.
    Provides a clean interface for level management and state tracking.
    """

    def __init__(self, levels_data=None):
        """
        Initialize the LevelManager with level data.

        Args:
            levels_data (list, optional): List of level data dictionaries.
                                        Defaults to LEVELS from levels.py
        """
        self.levels_data = levels_data or LEVELS
        self.metadata = LevelMetadata(self.levels_data)

        # Level state tracking
        self.completed = False
        self.index = 0
        self.total_presents = 0
        self.name = ""

        # Level objects
        self.platforms = []
        self.presents = []
        self.powerups = []
        self.enemies = []
        self.ground = None
        self.goal = None
        self.player_start = (0, 0)

        # Visual elements
        self.background = None
        self.overlay = None
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

        # Load initial level
        self.load_level(self.index)

    def load_level(self, index):
        """
        Load a level by index with comprehensive object creation.

        Args:
            index (int): Index of the level to load
        """
        if not 0 <= index < len(self.levels_data):
            raise IndexError(f"Level index {index} out of range")

        data = self.levels_data[index]
        self.index = index
        self.completed = False
        self.name = data.get('name', f"Level {index+1}")

        # Set level dimensions
        self.width = data.get('width', SCREEN_WIDTH)
        self.height = data.get('height', SCREEN_HEIGHT)

        # Create ground
        self.ground = pygame.Rect(0, self.height - GROUND_HEIGHT, self.width, GROUND_HEIGHT)

        # Create platforms
        self.platforms = [pygame.Rect(*p) for p in data['platforms']]

        # Create player start position
        self.player_start = tuple(data['player_start'])

        # Create goal
        gx, gy, gw, gh = data['goal']
        self.goal = pygame.Rect(gx, gy, gw, gh)

        # Create presents with random textures
        self.presents = []
        for p in data['presents']:
            rect = pygame.Rect(*p)
            texture = random.choice(self.metadata.get_present_textures())
            self.presents.append({"rect": rect, "texture": texture})

        # Create powerups
        self.powerups = [
            {'rect': pygame.Rect(*p['rect']), 'type': p['type']}
            for p in data.get('powerups', [])
        ]

        # Create enemies
        self.enemies = [Enemy(*e) for e in data.get('enemies', [])]

        # Set total presents count
        self.total_presents = len(self.presents)

        # Load background
        self._load_background(index)

        # Create overlay
        self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, OVERLAY_ALPHA))

    def _load_background(self, level_index):
        """
        Load background image with fallback support.

        Args:
            level_index (int): Index of the current level for background naming
        """
        # Try multiple background loading strategies
        bg_path = self.metadata.get_background_path(level_index)

        if bg_path and bg_path.exists():
            try:
                bg_img = pygame.image.load(str(bg_path)).convert()
                self.background = pygame.transform.scale(bg_img, (self.width, self.height))
            except Exception as e:
                print(f"Failed to load background {bg_path}: {e}")
                self._create_fallback_background()
        else:
            self._create_fallback_background()

    def _create_fallback_background(self):
        """Create a fallback background when image loading fails."""
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill(FALLBACK_BACKGROUND_COLOR)

    def next_level(self):
        """
        Progress to the next level.

        Returns:
            bool: True if successfully advanced, False if no more levels
        """
        if self.index + 1 < len(self.levels_data):
            self.index += 1
            self.load_level(self.index)
            return True
        return False  # No more levels

    def get_current_level_data(self):
        """Get the data dictionary for the current level."""
        return self.levels_data[self.index]

    def get_level_progress(self):
        """
        Get current level progress information.

        Returns:
            dict: Progress information including completion status and present count
        """
        collected_presents = self.total_presents - len(self.presents)
        return {
            'level_index': self.index,
            'level_name': self.name,
            'completed': self.completed,
            'total_presents': self.total_presents,
            'collected_presents': collected_presents,
            'progress_percentage': (collected_presents / self.total_presents * 100) if self.total_presents > 0 else 0
        }

    def reset_level(self):
        """Reset the current level to initial state."""
        self.load_level(self.index)
        self.completed = False


# =============================================================================
# OBJECT CREATION FUNCTIONS
# =============================================================================

def create_platform(rect):
    """
    Create a platform object from rectangle data.

    Args:
        rect (tuple or pygame.Rect): Platform rectangle (x, y, width, height)

    Returns:
        pygame.Rect: Platform rectangle object
    """
    if isinstance(rect, pygame.Rect):
        return rect.copy()
    return pygame.Rect(*rect)


def create_present(rect, texture_name=None):
    """
    Create a present object with texture information.

    Args:
        rect (tuple or pygame.Rect): Present rectangle (x, y, width, height)
        texture_name (str, optional): Name of texture to use. Random if not specified.

    Returns:
        dict: Present object with rect and texture information
    """
    if isinstance(rect, pygame.Rect):
        present_rect = rect.copy()
    else:
        present_rect = pygame.Rect(*rect)

    if texture_name is None:
        texture_name = random.choice(level_metadata.get_present_textures())

    return {
        "rect": present_rect,
        "texture": texture_name
    }


def create_powerup(rect, powerup_type):
    """
    Create a powerup object.

    Args:
        rect (tuple or pygame.Rect): Powerup rectangle (x, y, width, height)
        powerup_type (str): Type of powerup ('double_jump', 'speed_boost', 'invincibility')

    Returns:
        dict: Powerup object with rect and type information
    """
    if isinstance(rect, pygame.Rect):
        powerup_rect = rect.copy()
    else:
        powerup_rect = pygame.Rect(*rect)

    return {
        'rect': powerup_rect,
        'type': powerup_type
    }


def create_enemy(enemy_data):
    """
    Create an Enemy object from enemy data.

    Args:
        enemy_data (tuple): Enemy data (x, y, w, h, patrol_min_x, patrol_max_x, speed)

    Returns:
        Enemy: Configured Enemy instance
    """
    return Enemy(*enemy_data)


# =============================================================================
# ASSET LOADING FUNCTIONS
# =============================================================================

def load_background_for_level(level_index, width, height):
    """
    Load background image for a specific level with fallback.

    Args:
        level_index (int): Index of the level
        width (int): Target width for the background
        height (int): Target height for the background

    Returns:
        pygame.Surface: Background surface
    """
    bg_path = level_metadata.get_background_path(level_index)

    if bg_path and bg_path.exists():
        try:
            bg_img = pygame.image.load(str(bg_path)).convert()
            return pygame.transform.scale(bg_img, (width, height))
        except Exception as e:
            print(f"Failed to load background {bg_path}: {e}")

    # Fallback background
    surface = pygame.Surface((width, height))
    surface.fill(FALLBACK_BACKGROUND_COLOR)
    return surface


def create_overlay(width, height, alpha=OVERLAY_ALPHA):
    """
    Create a semi-transparent overlay for visual depth.

    Args:
        width (int): Overlay width
        height (int): Overlay height
        alpha (int): Alpha transparency value (0-255)

    Returns:
        pygame.Surface: Overlay surface with transparency
    """
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    return overlay


# =============================================================================
# LEVEL STATE AND PROGRESSION UTILITIES
# =============================================================================

def check_level_completion(level_manager):
    """
    Check if the current level is completed.

    Args:
        level_manager (LevelManager): The level manager instance

    Returns:
        bool: True if level is completed, False otherwise
    """
    collected_presents = level_manager.total_presents - len(level_manager.presents)
    return collected_presents >= level_manager.total_presents and level_manager.total_presents > 0


def get_level_completion_percentage(level_manager):
    """
    Get the completion percentage for the current level.

    Args:
        level_manager (LevelManager): The level manager instance

    Returns:
        float: Completion percentage (0-100)
    """
    if level_manager.total_presents == 0:
        return 100.0

    collected_presents = level_manager.total_presents - len(level_manager.presents)
    return (collected_presents / level_manager.total_presents) * 100


def can_advance_to_next_level(level_manager):
    """
    Check if the player can advance to the next level.

    Args:
        level_manager (LevelManager): The level manager instance

    Returns:
        bool: True if advancement is possible, False otherwise
    """
    return (level_manager.index + 1) < len(level_manager.levels_data)


# =============================================================================
# INITIALIZATION
# =============================================================================

# Create a default level manager instance for easy importing
default_level_manager = LevelManager()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main classes
    'LevelManager',

    # Factory functions
    'create_platform',
    'create_present',
    'create_powerup',
    'create_enemy',

    # Asset loading functions
    'load_background_for_level',
    'create_overlay',

    # Utility functions
    'check_level_completion',
    'get_level_completion_percentage',
    'can_advance_to_next_level',

    # Instances
    'default_level_manager',
    'level_metadata',

    # Data
    'LEVELS',
]