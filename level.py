
import pygame
import random
from pathlib import Path
from constants import ASSETS_DIR, FALLBACK_BACKGROUND_COLOR, OVERLAY_ALPHA, GROUND_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
from assets import get_texture
from enemy import Enemy
from levels import LEVELS, LevelMetadata, level_metadata

class LevelManager:

    def __init__(self, levels_data=None):
        self.levels_data = levels_data or LEVELS
        self.metadata = LevelMetadata(self.levels_data)
        self.completed = False
        self.index = 0
        self.total_presents = 0
        self.name = ''
        self.platforms = []
        self.presents = []
        self.powerups = []
        self.enemies = []
        self.ground = None
        self.goal = None
        self.player_start = (0, 0)
        self.background = None
        self.overlay = None
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.load_level(self.index)

    def load_level(self, index):
        if not 0 <= index < len(self.levels_data):
            raise IndexError(f'Level index {index} out of range')
        data = self.levels_data[index]
        self.index = index
        self.completed = False
        self.name = data.get('name', f'Level {index + 1}')
        self.width = data.get('width', SCREEN_WIDTH)
        self.height = data.get('height', SCREEN_HEIGHT)
        self.ground = pygame.Rect(0, self.height - GROUND_HEIGHT, self.width, GROUND_HEIGHT)
        self.platforms = [pygame.Rect(*p) for p in data['platforms']]
        self.player_start = tuple(data['player_start'])
        gx, gy, gw, gh = data['goal']
        self.goal = pygame.Rect(gx, gy, gw, gh)
        self.presents = []
        for p in data['presents']:
            rect = pygame.Rect(*p)
            texture = random.choice(self.metadata.get_present_textures())
            self.presents.append({'rect': rect, 'texture': texture})
        self.powerups = [{'rect': pygame.Rect(*p['rect']), 'type': p['type']} for p in data.get('powerups', [])]
        self.enemies = [Enemy(*e) for e in data.get('enemies', [])]
        self.total_presents = len(self.presents)
        self._load_background(index)
        self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, OVERLAY_ALPHA))

    def _load_background(self, level_index):

        bg_path = self.metadata.get_background_path(level_index)
        if bg_path and bg_path.exists():
            try:
                bg_img = pygame.image.load(str(bg_path)).convert()
                self.background = pygame.transform.scale(bg_img, (self.width, self.height))
            except Exception as e:
                print(f'Failed to load background {bg_path}: {e}')
                self._create_fallback_background()
        else:
            self._create_fallback_background()

    def _create_fallback_background(self):
        """Create a fallback background when image loading fails."""
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill(FALLBACK_BACKGROUND_COLOR)

    def next_level(self):

        if self.index + 1 < len(self.levels_data):
            self.index += 1
            self.load_level(self.index)
            return True
        return False

    def get_current_level_data(self):
        """Get the data dictionary for the current level."""
        return self.levels_data[self.index]

    def get_level_progress(self):

        collected_presents = self.total_presents - len(self.presents)
        return {'level_index': self.index, 'level_name': self.name, 'completed': self.completed, 'total_presents': self.total_presents, 'collected_presents': collected_presents, 'progress_percentage': collected_presents / self.total_presents * 100 if self.total_presents > 0 else 0}

    def reset_level(self):
        """Reset the current level to initial state."""
        self.load_level(self.index)
        self.completed = False

def create_platform(rect):

    if isinstance(rect, pygame.Rect):
        return rect.copy()
    return pygame.Rect(*rect)

def create_present(rect, texture_name=None):

    if isinstance(rect, pygame.Rect):
        present_rect = rect.copy()
    else:
        present_rect = pygame.Rect(*rect)
    if texture_name is None:
        texture_name = random.choice(level_metadata.get_present_textures())
    return {'rect': present_rect, 'texture': texture_name}

def create_powerup(rect, powerup_type):

    if isinstance(rect, pygame.Rect):
        powerup_rect = rect.copy()
    else:
        powerup_rect = pygame.Rect(*rect)
    return {'rect': powerup_rect, 'type': powerup_type}

def create_enemy(enemy_data):

    return Enemy(*enemy_data)

def load_background_for_level(level_index, width, height):

    bg_path = level_metadata.get_background_path(level_index)
    if bg_path and bg_path.exists():
        try:
            bg_img = pygame.image.load(str(bg_path)).convert()
            return pygame.transform.scale(bg_img, (width, height))
        except Exception as e:
            print(f'Failed to load background {bg_path}: {e}')
    surface = pygame.Surface((width, height))
    surface.fill(FALLBACK_BACKGROUND_COLOR)
    return surface

def create_overlay(width, height, alpha=OVERLAY_ALPHA):

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    return overlay

def check_level_completion(level_manager):

    collected_presents = level_manager.total_presents - len(level_manager.presents)
    return collected_presents >= level_manager.total_presents and level_manager.total_presents > 0

def get_level_completion_percentage(level_manager):

    if level_manager.total_presents == 0:
        return 100.0
    collected_presents = level_manager.total_presents - len(level_manager.presents)
    return collected_presents / level_manager.total_presents * 100

def can_advance_to_next_level(level_manager):

    return level_manager.index + 1 < len(level_manager.levels_data)
default_level_manager = LevelManager()
__all__ = ['LevelManager', 'create_platform', 'create_present', 'create_powerup', 'create_enemy', 'load_background_for_level', 'create_overlay', 'check_level_completion', 'get_level_completion_percentage', 'can_advance_to_next_level', 'default_level_manager', 'level_metadata', 'LEVELS']