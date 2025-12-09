
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pygame
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

    try:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Santa Platformer (Pygame)')
        initialize_display()
        game = Game(screen=screen, levels_data=LEVELS)
        game.run()
    except KeyboardInterrupt:
        print('\nGame interrupted by user')
    except Exception as e:
        print(f'Error running game: {e}')
        import traceback
        traceback.print_exc()
    finally:
        try:
            pygame.quit()
        except:
            pass
if __name__ == '__main__':
    main()