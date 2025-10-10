"""
Player module for Santa Platformer game.
Contains the Player class with physics, animation, power-ups, and state management.
"""

import pygame
from constants import (
    GRAVITY, MAX_FALL, BASE_SPEED, BASE_JUMP,
    PLAYER_WIDTH, PLAYER_HEIGHT, SPEED_BOOST_MULTIPLIER,
    RESPAWN_INVINCIBILITY_DURATION, HIT_INVINCIBILITY_FLICKER
)
from assets import get_texture


class Player:
    """
    Player character class with physics, animation, and power-up management.

    Handles:
    - Physics properties (position, velocity, gravity, jumping)
    - Animation system (idle and walking frames with timing)
    - Power-up management (speed boost, double jump, invincibility)
    - State management (facing direction, jump counts, invincibility)
    """

    def __init__(self, start_x, start_y):
        """
        Initialize the player character.

        Args:
            start_x (int): Starting X position
            start_y (int): Starting Y position
        """
        self.w, self.h = PLAYER_WIDTH, PLAYER_HEIGHT
        self.rect = pygame.Rect(start_x, start_y, self.w, self.h)
        self.x = float(start_x)
        self.y = float(start_y)
        self.vx = 0
        self.vy = 0
        self.base_speed = BASE_SPEED
        self.speed = self.base_speed
        self.jump_strength = BASE_JUMP
        self.max_jumps = 1
        self.jumps_remaining = self.max_jumps
        self.facing_right = True

        # Power-up timers (in milliseconds)
        self.power_until = {
            'speed_boost': 0,
            'double_jump': 0,
            'invincibility': 0
        }
        self.hit_invincible_until = 0

        # Animation system
        self.idle_frame = get_texture("player", (self.w, self.h))
        self.walk_frames = [
            get_texture("player1", (self.w, self.h)),
            get_texture("player2", (self.w, self.h))
        ]
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200  # ms per frame

    def update_animation(self, dt_ms):
        """
        Update player animation based on movement state.

        Args:
            dt_ms (int): Delta time in milliseconds
        """
        if self.vx != 0:  # Moving
            self.animation_timer += dt_ms
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
        else:
            self.current_frame = 0  # Reset walk animation when idle

    def get_current_frame(self):
        """
        Get the current animation frame, flipped if facing left.

        Returns:
            pygame.Surface: Current animation frame
        """
        if self.vx != 0:  # Moving
            frame = self.walk_frames[self.current_frame]
        else:  # Idle
            frame = self.idle_frame

        # Flip horizontally if facing left
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        return frame

    def is_invincible(self, now_ms):
        """
        Check if player is currently invincible.

        Args:
            now_ms (int): Current time in milliseconds

        Returns:
            bool: True if invincible, False otherwise
        """
        return (now_ms < self.power_until['invincibility'] or
                now_ms < self.hit_invincible_until)

    def update_powerups(self, now_ms):
        """
        Update power-up effects based on current time.

        Args:
            now_ms (int): Current time in milliseconds
        """
        # Speed boost effect
        if now_ms < self.power_until['speed_boost']:
            self.speed = self.base_speed * SPEED_BOOST_MULTIPLIER
        else:
            self.speed = self.base_speed

        # Double jump effect
        if now_ms < self.power_until['double_jump']:
            self.max_jumps = 2
        else:
            self.max_jumps = 1

        # Reset jumps when landing handled elsewhere
        # Invincibility handled in is_invincible()

    def apply_powerup(self, ptype, duration_ms, now_ms):
        """
        Apply a power-up effect to the player.

        Args:
            ptype (str): Type of power-up ('speed_boost', 'double_jump', 'invincibility')
            duration_ms (int): Duration in milliseconds
            now_ms (int): Current time in milliseconds
        """
        self.power_until[ptype] = now_ms + duration_ms
        # If double jump power gained, immediately refill jumps so player can use it right away
        if ptype == 'double_jump':
            self.jumps_remaining = self.max_jumps if now_ms < self.power_until['double_jump'] else self.jumps_remaining

    def respawn(self, start_x, start_y):
        """
        Respawn player at the given position.

        Args:
            start_x (int): Respawn X position
            start_y (int): Respawn Y position
        """
        self.x = float(start_x)
        self.y = float(start_y)
        self.rect.topleft = (start_x, start_y)
        self.vx = 0
        self.vy = 0
        # Give a short invincible window after respawn
        self.hit_invincible_until = pygame.time.get_ticks() + RESPAWN_INVINCIBILITY_DURATION

    def set_movement(self, direction, move):
        """
        Set player movement direction and facing.

        Args:
            direction (str): 'left' or 'right'
            move (bool): True if moving in that direction
        """
        if direction == 'left':
            self.vx = -self.speed if move else 0
            if move:
                self.facing_right = False
        elif direction == 'right':
            self.vx = self.speed if move else 0
            if move:
                self.facing_right = True

    def jump(self):
        """
        Make the player jump if jumps are available.

        Returns:
            bool: True if jump was performed, False if no jumps remaining
        """
        if self.jumps_remaining > 0:
            self.vy = self.jump_strength
            self.jumps_remaining -= 1
            return True
        return False

    def apply_physics(self):
        """
        Apply gravity and update position.
        """
        # Apply gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Keep rect synchronized
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def resolve_horizontal_collisions(self, platforms):
        """
        Resolve horizontal collisions with platforms.

        Args:
            platforms (list): List of platform rectangles
        """
        self.rect.x = int(self.x)
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vx > 0:
                    self.rect.right = plat.left
                elif self.vx < 0:
                    self.rect.left = plat.right
                self.x = self.rect.x

    def resolve_vertical_collisions(self, platforms):
        """
        Resolve vertical collisions with platforms.

        Args:
            platforms (list): List of platform rectangles

        Returns:
            bool: True if player is on ground, False otherwise
        """
        self.rect.y = int(self.y)
        on_ground = False

        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vy > 0:
                    # Falling -> land on top
                    self.rect.bottom = plat.top
                    self.vy = 0
                    self.y = self.rect.y
                    on_ground = True
                    # Refill jumps when landing
                    self.jumps_remaining = self.max_jumps
                elif self.vy < 0:
                    # Hit bottom of platform
                    self.rect.top = plat.bottom
                    self.vy = 0
                    self.y = self.rect.y

        return on_ground

    def clamp_to_level_bounds(self, level_width, level_height):
        """
        Clamp player position to level boundaries.

        Args:
            level_width (int): Level width in pixels
            level_height (int): Level height in pixels
        """
        # Horizontal bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.x
        if self.rect.right > level_width:
            self.rect.right = level_width
            self.x = self.rect.x

        # Vertical bounds
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.y
        if self.rect.bottom > level_height:
            self.rect.bottom = level_height
            self.y = self.rect.y
            self.vy = 0
            self.jumps_remaining = self.max_jumps

    def check_enemy_collision(self, enemies):
        """
        Check for collisions with enemies.

        Args:
            enemies (list): List of enemy objects with rect attribute

        Returns:
            object: First colliding enemy or None if no collision
        """
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                return enemy
        return None

    def check_present_collision(self, presents):
        """
        Check for collisions with presents and collect them.

        Args:
            presents (list): List of present objects with rect attribute

        Returns:
            list: List of collected presents
        """
        collected = []
        for present in presents[:]:
            if self.rect.colliderect(present["rect"]):
                collected.append(present)
        return collected

    def check_powerup_collision(self, powerups):
        """
        Check for collisions with power-ups and collect them.

        Args:
            powerups (list): List of power-up objects with rect and type attributes

        Returns:
            list: List of collected power-ups
        """
        collected = []
        for powerup in powerups[:]:
            if self.rect.colliderect(powerup['rect']):
                collected.append(powerup)
        return collected

    def check_goal_collision(self, goal_rect):
        """
        Check for collision with goal.

        Args:
            goal_rect (pygame.Rect): Goal rectangle

        Returns:
            bool: True if colliding with goal, False otherwise
        """
        return self.rect.colliderect(goal_rect)

    def draw(self, screen, camera_x, camera_y, now_ms):
        """
        Draw the player on screen with invincibility flicker effect.

        Args:
            screen (pygame.Surface): Screen surface to draw on
            camera_x (int): Camera X offset
            camera_y (int): Camera Y offset
            now_ms (int): Current time in milliseconds for flicker effect
        """
        # Update animation
        dt_ms = 16  # Approximate frame time (assuming 60 FPS)
        self.update_animation(dt_ms)

        # Get current frame
        surf_player = self.get_current_frame()

        # Invincibility flicker effect
        if not (self.is_invincible(now_ms) and (now_ms // HIT_INVINCIBILITY_FLICKER) % 2 == 0):
            screen.blit(surf_player, (self.rect.x - camera_x, self.rect.y - camera_y))