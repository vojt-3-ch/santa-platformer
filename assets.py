"""
Asset management system for Santa Platformer game.
Handles texture loading, caching, and fallback generation for missing assets.
"""

import pygame
from pathlib import Path
from constants import ASSETS_DIR, FALLBACK_COLORS

# --- Texture cache for loaded assets ---
_texture_cache = {}

# --- Deferred loading system ---
_deferred_textures = {}  # Stores parameters for textures that need loading when display is ready
_display_initialized = False

def _is_display_initialized():
    """
    Check if pygame.display is initialized.

    Returns:
        bool: True if display is initialized, False otherwise
    """
    try:
        return pygame.display.get_init() and pygame.display.get_surface() is not None
    except:
        return False

def _load_deferred_textures():
    """
    Load all deferred textures now that display is initialized.
    This function is called when display becomes available.
    """
    global _display_initialized

    if not _deferred_textures or _display_initialized:
        return

    _display_initialized = True

    # Process all deferred texture requests
    for key, (name, size) in _deferred_textures.items():
        try:
            _load_texture_immediate(name, size)
        except Exception as e:
            print(f"Failed to load deferred texture {name}: {e}")

    # Clear deferred textures after processing
    _deferred_textures.clear()

def _load_texture_immediate(name, size):
    """
    Immediately load a texture (assumes display is initialized).

    Args:
        name (str): Name of the texture (without .png extension)
        size (tuple): (width, height) tuple for the texture size

    Returns:
        pygame.Surface: The loaded or generated texture surface
    """
    key = (name, size)
    path = ASSETS_DIR / f"{name}.png"
    w, h = size
    surf = None

    # Try to load the texture from file
    if path.exists():
        try:
            img = pygame.image.load(str(path)).convert_alpha()
            surf = pygame.transform.smoothscale(img, (w, h))
        except Exception as e:
            print("Failed to load", path, e)

    # Generate fallback texture if loading failed
    if surf is None:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = FALLBACK_COLORS.get(name, FALLBACK_COLORS.get('default', (120, 120, 120)))
        surf.fill(color)

        # Add decorative elements based on asset type
        if name == 'present':
            # Draw ribbon decorations
            pygame.draw.rect(surf, (180, 20, 20), (w//4, 0, w//2, h))         # ribbon vertical
            pygame.draw.rect(surf, (200, 40, 40), (0, h//3, w, h//6))        # ribbon horizontal
        elif name == 'player':
            # Draw faux beard
            pygame.draw.rect(surf, (255, 255, 255), (w//6, h//6, w//6, h//8))
        elif name == 'tree':
            # Draw tree shape
            pygame.draw.polygon(surf, (10, 80, 10), [(w//2, 0), (w, h), (0, h)])

    # Cache and return the texture
    _texture_cache[key] = surf
    return surf

def _create_placeholder_texture(size):
    """
    Create a placeholder texture when display is not initialized.

    Args:
        size (tuple): (width, height) tuple for the texture size

    Returns:
        pygame.Surface: A placeholder surface
    """
    w, h = size
    # Create a simple colored surface as placeholder
    surf = pygame.Surface((w, h))
    surf.fill((200, 200, 200))  # Light gray placeholder
    return surf

def get_texture(name, size):
    """
    Load and return a texture by name, with lazy loading and caching support.

    This function implements lazy loading to avoid pygame.display initialization issues.
    Textures are only loaded when pygame.display is initialized, otherwise a placeholder
    is returned and actual loading is deferred until display becomes available.

    Args:
        name (str): Name of the texture (without .png extension)
        size (tuple): (width, height) tuple for the texture size

    Returns:
        pygame.Surface: The loaded or generated texture surface (or placeholder if display not ready)
    """
    key = (name, size)

    # Check if texture is already cached and loaded
    if key in _texture_cache:
        return _texture_cache[key]

    # Check if display is initialized
    if _is_display_initialized():
        # Display is ready, load texture immediately
        return _load_texture_immediate(name, size)
    else:
        # Display not initialized, defer loading and return placeholder
        if key not in _deferred_textures:
            _deferred_textures[key] = (name, size)

        # Return a placeholder surface
        return _create_placeholder_texture(size)

def initialize_display():
    """
    Call this function when pygame.display is initialized to load any deferred textures.
    This should be called after pygame.display.set_mode() or similar initialization.
    """
    _load_deferred_textures()

def clear_texture_cache():
    """
    Clear the texture cache and deferred textures. Useful for memory management or when reloading assets.
    """
    global _texture_cache, _deferred_textures
    _texture_cache.clear()
    _deferred_textures.clear()

def get_cached_texture_count():
    """
    Get the number of cached textures for debugging purposes.

    Returns:
        int: Number of cached texture entries
    """
    return len(_texture_cache)

def get_deferred_texture_count():
    """
    Get the number of deferred textures waiting for display initialization.

    Returns:
        int: Number of deferred texture entries
    """
    return len(_deferred_textures)

def is_display_ready():
    """
    Check if the display system is ready for texture operations.

    Returns:
        bool: True if display is initialized and ready
    """
    return _display_initialized or _is_display_initialized()