import pygame
from constants import *
pygame.font.init()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 48)
message = ''
message_until = 0

def show_message(text, duration_ms=None):
    global message, message_until
    if duration_ms is None:
        if 'Game Over' in text:
            duration_ms = MESSAGE_DURATION_GAME_OVER
        elif 'Powerup:' in text:
            duration_ms = MESSAGE_DURATION_MEDIUM
        elif 'Present collected' in text or 'lost a life' in text:
            duration_ms = MESSAGE_DURATION_SHORT
        elif 'Collect all presents' in text:
            duration_ms = MESSAGE_DURATION_LONG
        elif 'Level Complete' in text:
            duration_ms = MESSAGE_DURATION_MEDIUM
        else:
            duration_ms = MESSAGE_DURATION_SHORT
    message = text
    message_until = pygame.time.get_ticks() + duration_ms

def draw_hud(screen, lives, level_index, level_name, score, total_presents, player, screen_width):
    lives_surf = font.render(f'Lives: {lives}', True, COLOR_WHITE)
    level_surf = font.render(f'Level: {level_index + 1} - {level_name}', True, COLOR_WHITE)
    score_surf = font.render(f'Presents: {score}/{total_presents}', True, COLOR_WHITE)
    screen.blit(lives_surf, (HUD_MARGIN, HUD_MARGIN))
    screen.blit(level_surf, (HUD_MARGIN, HUD_MARGIN + HUD_LINE_HEIGHT))
    screen.blit(score_surf, (HUD_MARGIN, HUD_MARGIN + HUD_LINE_HEIGHT * 2))
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
    global message, message_until
    now = pygame.time.get_ticks()
    if message and now < message_until:
        m_surf = font.render(message, True, COLOR_WHITE)
        screen.blit(m_surf, (screen_width // 2 - m_surf.get_width() // 2, HUD_MARGIN))

def draw_game_over(screen, screen_width, screen_height):
    screen.fill(GAME_OVER_BACKGROUND_COLOR)
    text = big_font.render('You saved Christmas!', True, COLOR_WHITE)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))

def is_message_active():
    global message, message_until
    now = pygame.time.get_ticks()
    return message and now < message_until

def get_remaining_message_time():
    global message_until
    now = pygame.time.get_ticks()
    if now < message_until:
        return message_until - now
    return 0

def clear_message():
    global message, message_until
    message = ''
    message_until = 0