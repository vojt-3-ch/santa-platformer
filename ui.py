"""
UI Module for Santa Platformer game.
Handles HUD display, message system, and user interface rendering.
"""

import pygame
from constants import *

# Initialize fonts
pygame.font.init()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 48)

# Message display system
message = ""
message_until = 0

def show_message(text, duration_ms=None):
    """
    Display a temporary message on screen.

    Args:
        text (str): Message text to display
        duration_ms (int, optional): Duration in milliseconds. If None, uses default timing.
    """
    global message, message_until

    if duration_ms is None:
        # Auto-determine duration based on message type
        if "Game Over" in text:
            duration_ms = MESSAGE_DURATION_GAME_OVER
        elif "Powerup:" in text:
            duration_ms = MESSAGE_DURATION_MEDIUM
        elif "Present collected" in text or "lost a life" in text:
            duration_ms = MESSAGE_DURATION_SHORT
        elif "Collect all presents" in text:
            duration_ms = MESSAGE_DURATION_LONG
        elif "Level Complete" in text:
            duration_ms = MESSAGE_DURATION_MEDIUM
        else:
            duration_ms = MESSAGE_DURATION_SHORT

    message = text
    message_until = pygame.time.get_ticks() + duration_ms

def draw_hud(screen, lives, level_index, level_name, score, total_presents, player, screen_width):
    """
    Draw the Heads-Up Display showing game information.

    Args:
        screen: Pygame screen surface
        lives (int): Current number of lives
        level_index (int): Current level index (0-based)
        level_name (str): Name of current level
        score (int): Current score (presents collected)
        total_presents (int): Total presents in level
        player: Player object with power-up timers
        screen_width (int): Width of the screen for positioning
    """
    # Lives, Level, Score
    lives_surf = font.render(f"Lives: {lives}", True, COLOR_WHITE)
    level_surf = font.render(f"Level: {level_index+1} - {level_name}", True, COLOR_WHITE)
    score_surf = font.render(f"Presents: {score}/{total_presents}", True, COLOR_WHITE)

    screen.blit(lives_surf, (HUD_MARGIN, HUD_MARGIN))
    screen.blit(level_surf, (HUD_MARGIN, HUD_MARGIN + HUD_LINE_HEIGHT))
    screen.blit(score_surf, (HUD_MARGIN, HUD_MARGIN + HUD_LINE_HEIGHT * 2))

    # Active powerups + timers
    now = pygame.time.get_ticks()
    x = screen_width - HUD_MARGIN
    y = HUD_MARGIN

    for ptype in ['double_jump', 'speed_boost', 'invincibility']:
        end = player.power_until[ptype]
        if end > now:
            remain_s = (end - now) // 1000 + 1
            text = f"{ptype.replace('_', ' ').title()} {remain_s}s"
            surf = font.render(text, True, COLOR_WHITE)
            rect = surf.get_rect(topright=(x, y))
            screen.blit(surf, rect)
            y += HUD_LINE_HEIGHT

def draw_message(screen, screen_width):
    """
    Draw the current message if one is active.

    Args:
        screen: Pygame screen surface
        screen_width (int): Width of the screen for centering
    """
    global message, message_until

    now = pygame.time.get_ticks()
    if message and now < message_until:
        m_surf = font.render(message, True, COLOR_WHITE)
        screen.blit(m_surf, (screen_width//2 - m_surf.get_width()//2, HUD_MARGIN))

def draw_game_over(screen, screen_width, screen_height):
    """
    Draw the game over/victory screen.

    Args:
        screen: Pygame screen surface
        screen_width (int): Width of the screen
        screen_height (int): Height of the screen
    """
    screen.fill(GAME_OVER_BACKGROUND_COLOR)
    text = big_font.render("You saved Christmas! 🎅🎉", True, COLOR_WHITE)
    screen.blit(text, (screen_width//2 - text.get_width()//2,
                      screen_height//2 - text.get_height()//2))

def is_message_active():
    """
    Check if a message is currently being displayed.

    Returns:
        bool: True if message is active, False otherwise
    """
    global message, message_until
    now = pygame.time.get_ticks()
    return message and now < message_until

def get_remaining_message_time():
    """
    Get the remaining time for the current message in milliseconds.

    Returns:
        int: Remaining time in milliseconds, 0 if no message active
    """
    global message_until
    now = pygame.time.get_ticks()
    if now < message_until:
        return message_until - now
    return 0

def clear_message():
    """
    Clear the current message immediately.
    """
    global message, message_until
    message = ""
    message_until = 0