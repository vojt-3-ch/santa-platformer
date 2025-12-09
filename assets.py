import pygame
from pathlib import Path
from constants import ASSETS_DIR, FALLBACK_COLORS
_texture_cache = {}

_deferred_textures = {}
_display_initialized = False

def _is_display_initialized():
    try:
        return pygame.display.get_init() and pygame.display.get_surface() is not None
    except:
        return False

def _load_deferred_textures():
    global _display_initialized

    if not _deferred_textures or _display_initialized:
        return

    _display_initialized = True

    for key, (name, size) in _deferred_textures.items():
        try:
            _load_texture_immediate(name, size)
        except Exception as e:
            print(f"Failed to load deferred texture {name}: {e}")

    _deferred_textures.clear()

def _load_texture_immediate(name, size):
    key = (name, size)
    path = ASSETS_DIR / f"{name}.png"
    w, h = size
    surf = None

    if path.exists():
        try:
            img = pygame.image.load(str(path)).convert_alpha()
            surf = pygame.transform.smoothscale(img, (w, h))
        except Exception as e:
            print("Failed to load", path, e)

    if surf is None:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = FALLBACK_COLORS.get(name, FALLBACK_COLORS.get('default', (120, 120, 120)))
        surf.fill(color)

        if name == 'present':
            pygame.draw.rect(surf, (180, 20, 20), (w//4, 0, w//2, h))
            pygame.draw.rect(surf, (200, 40, 40), (0, h//3, w, h//6))
        elif name == 'player':
            pygame.draw.rect(surf, (255, 255, 255), (w//6, h//6, w//6, h//8))
        elif name == 'tree':
            pygame.draw.polygon(surf, (10, 80, 10), [(w//2, 0), (w, h), (0, h)])

    _texture_cache[key] = surf
    return surf

def _create_placeholder_texture(size):
    w, h = size
    surf = pygame.Surface((w, h))
    surf.fill((200, 200, 200))
    return surf

def get_texture(name, size):
    key = (name, size)

    if key in _texture_cache:
        return _texture_cache[key]

    if _is_display_initialized():
        return _load_texture_immediate(name, size)
    else:
        if key not in _deferred_textures:
            _deferred_textures[key] = (name, size)

        return _create_placeholder_texture(size)

def initialize_display():
    _load_deferred_textures()

def clear_texture_cache():
    global _texture_cache, _deferred_textures
    _texture_cache.clear()
    _deferred_textures.clear()

def get_cached_texture_count():
    return len(_texture_cache)

def get_deferred_texture_count():
    return len(_deferred_textures)

def is_display_ready():
    return _display_initialized or _is_display_initialized()