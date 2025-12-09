from constants import (
    GRAVITY,
    MAX_FALL,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)


def resolve_horizontal(player, platforms):
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
    if player.rect.left < 0:
        player.rect.left = 0
        player.x = player.rect.x
    elif player.rect.right > level_width:
        player.rect.right = level_width
        player.x = player.rect.x


def clamp_vertical(player, level_height):
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
    player.vy += GRAVITY
    if player.vy > MAX_FALL:
        player.vy = MAX_FALL


def update_player_position(player):
    player.x += player.vx
    player.y += player.vy


def check_platform_collision(player_rect, platforms):
    colliding_platforms = []
    for plat in platforms:
        if player_rect.colliderect(plat):
            colliding_platforms.append(plat)
    return colliding_platforms


def is_on_ground(player, platforms):
    # Create a test rectangle slightly below the player
    test_rect = player.rect.copy()
    test_rect.y += 1

    for plat in platforms:
        if test_rect.colliderect(plat):
            return True
    return False