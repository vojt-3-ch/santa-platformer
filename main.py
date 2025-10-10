#!/usr/bin/env python3
"""
Main entry point for Santa Platformer game.

This module serves as the main entry point for the game, providing proper
pygame initialization and game loop execution using the modular game architecture.

Usage:
    python main.py
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import pygame for initialization
import pygame

# Import all game modules
from constants import *
from assets import get_texture, initialize_display
from player import Player
from enemy import Enemy
from physics import *
from ui import *
from level import LevelManager, LEVELS
from levels import *
from game import Game


def main():
    """
    Main function to start the Santa Platformer game.

    This function handles pygame initialization, creates the game instance,
    and runs the main game loop with proper error handling and cleanup.
    """
    try:
        # Initialize pygame
        pygame.init()

        # Set up display
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Santa Platformer (Pygame)")

        # Initialize assets system now that display is ready
        initialize_display()

        # Create game instance
        game = Game(screen=screen, levels_data=LEVELS)

        # Run the game
        game.run()

    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure proper cleanup
        try:
            pygame.quit()
        except:
            pass


if __name__ == "__main__":
    main()