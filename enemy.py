"""
Enemy module for Santa Platformer game.
Contains the Enemy class with patrol AI functionality and direction tracking.
"""

import pygame
from assets import get_texture


class Enemy:
    """
    Enemy class with patrol AI system and direction tracking.

    Features:
    - Patrol AI movement between defined boundaries
    - Direction tracking for proper sprite flipping
    - Speed variation support for different enemy types
    - Boundary-based movement system with automatic direction reversal
    """

    def __init__(self, x, y, w, h, patrol_min_x, patrol_max_x, speed=2):
        """
        Initialize enemy with patrol boundaries and movement speed.

        Args:
            x (int): Initial x position
            y (int): Initial y position
            w (int): Width of enemy
            h (int): Height of enemy
            patrol_min_x (int): Left boundary for patrol movement
            patrol_max_x (int): Right boundary for patrol movement
            speed (float): Movement speed (default: 2)
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.vx = speed
        self.patrol_min = patrol_min_x
        self.patrol_max = patrol_max_x
        self.speed = speed
        self.facing_right = True
        self.texture = get_texture('enemy', (w, h))


    def update(self):
        """
        Update enemy position and handle patrol AI movement.

        This method handles:
        - Horizontal movement within patrol boundaries
        - Automatic direction reversal at boundaries
        - Direction tracking for sprite flipping
        """
        self.rect.x += self.vx

        # Check left boundary
        if self.rect.x < self.patrol_min:
            self.rect.x = self.patrol_min
            self.vx = abs(self.speed)
            self.facing_right = True
        # Check right boundary
        elif self.rect.x > self.patrol_max:
            self.rect.x = self.patrol_max
            self.vx = -abs(self.speed)
            self.facing_right = False