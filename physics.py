"""
Physics and collision detection module for Santa Platformer game.
This module handles all collision detection, physics calculations, and boundary management.
"""

from constants import (
    GRAVITY,
    MAX_FALL,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)


def resolve_horizontal(player, platforms):
    """
    Resolve horizontal collisions between player and platforms.

    Args:
        player: Player object with rect, x, vx attributes
        platforms: List of platform rectangles to check collisions against

    This function modifies the player's position and velocity in-place.
    """
    player.rect.x = int(player.x)
    for plat in platforms:
        if player.rect.colliderect(plat):
            if player.vx > 0:
                # Moving right -> hit left side of platform
                player.rect.right = plat.left
            elif player.vx < 0:
                # Moving left -> hit right side of platform
                player.rect.left = plat.right
            player.x = player.rect.x


def resolve_vertical(player, platforms):
    """
    Resolve vertical collisions between player and platforms.

    Args:
        player: Player object with rect, y, vy attributes
        platforms: List of platform rectangles to check collisions against

    Returns:
        bool: True if player is on ground, False otherwise

    This function modifies the player's position and velocity in-place,
    and refills jumps when landing on platforms.
    """
    player.rect.y = int(player.y)
    on_ground = False

    for plat in platforms:
        if player.rect.colliderect(plat):
            if player.vy > 0:
                # Falling down -> land on top of platform
                player.rect.bottom = plat.top
                player.vy = 0
                player.y = player.rect.y
                on_ground = True
                # Refill jumps when landing
                player.jumps_remaining = player.max_jumps
            elif player.vy < 0:
                # Moving up -> hit bottom of platform (ceiling collision)
                player.rect.top = plat.bottom
                player.vy = 0
                player.y = player.rect.y

    return on_ground


def clamp_horizontal(player, level_width):
    """
    Clamp player horizontally within level bounds.

    Args:
        player: Player object with rect and x attributes
        level_width: Width of the level in pixels

    This function modifies the player's position in-place.
    """
    if player.rect.left < 0:
        player.rect.left = 0
        player.x = player.rect.x
    elif player.rect.right > level_width:
        player.rect.right = level_width
        player.x = player.rect.x


def clamp_vertical(player, level_height):
    """
    Clamp player vertically within level bounds and handle bottom collision.

    Args:
        player: Player object with rect, y, vy attributes
        level_height: Height of the level in pixels

    This function modifies the player's position and velocity in-place,
    and refills jumps when hitting the bottom boundary.
    """
    if player.rect.top < 0:
        # Hit top boundary (ceiling)
        player.rect.top = 0
        player.y = player.rect.y
        player.vy = 0  # Stop upward movement
    elif player.rect.bottom > level_height:
        # Hit bottom boundary (floor)
        player.rect.bottom = level_height
        player.y = player.rect.y
        player.vy = 0
        # Refill jumps when hitting bottom
        player.jumps_remaining = player.max_jumps


def apply_gravity(player):
    """
    Apply gravity to the player.

    Args:
        player: Player object with vy attribute

    This function modifies the player's velocity in-place.
    """
    player.vy += GRAVITY
    if player.vy > MAX_FALL:
        player.vy = MAX_FALL


def update_player_position(player):
    """
    Update player position based on current velocity.

    Args:
        player: Player object with x, y, vx, vy attributes

    This function modifies the player's position in-place.
    """
    player.x += player.vx
    player.y += player.vy


def check_platform_collision(player_rect, platforms):
    """
    Check if a rectangle collides with any platform.

    Args:
        player_rect: Rectangle to check collisions for
        platforms: List of platform rectangles

    Returns:
        list: List of platforms that collide with player_rect
    """
    colliding_platforms = []
    for plat in platforms:
        if player_rect.colliderect(plat):
            colliding_platforms.append(plat)
    return colliding_platforms


def is_on_ground(player, platforms):
    """
    Check if player is standing on any platform.

    Args:
        player: Player object with rect attribute
        platforms: List of platform rectangles

    Returns:
        bool: True if player is on ground, False otherwise
    """
    # Create a test rectangle slightly below the player
    test_rect = player.rect.copy()
    test_rect.y += 1

    for plat in platforms:
        if test_rect.colliderect(plat):
            return True
    return False