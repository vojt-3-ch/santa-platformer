
import pygame
import random
from constants import *
from assets import get_texture
from player import Player
from enemy import Enemy
from physics import *
from ui import *
from level import LevelManager, LEVELS

class Game:
    

    def __init__(self, screen=None, levels_data=None):

        if not pygame.get_init():
            pygame.init()
        self.screen = screen or pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Santa Platformer (Pygame)')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 48)
        self.level_manager = LevelManager(levels_data)
        self.player = Player(*self.level_manager.player_start)
        self.lives = STARTING_LIVES
        self.score = 0
        self.level_complete_time = None
        self.camera_x = 0
        self.camera_y = 0
        self.running = False
        self.dt_ms = 0
        self.now = 0

    def handle_events(self):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key in (pygame.K_UP, pygame.K_SPACE, pygame.K_w):
                    if self.player.jumps_remaining > 0:
                        self.player.vy = self.player.jump_strength
                        self.player.jumps_remaining -= 1
        return True

    def handle_input(self):
        """Handle continuous keyboard input for player movement."""
        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
            self.player.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed
            self.player.facing_right = True

    def update_physics(self):
        """Update all physics including player movement, collisions, and boundaries."""
        self.player.vy += GRAVITY
        if self.player.vy > MAX_FALL:
            self.player.vy = MAX_FALL
        self.player.x += self.player.vx
        all_platforms = [self.level_manager.ground] + self.level_manager.platforms
        self.player.resolve_horizontal_collisions(all_platforms)
        if self.player.rect.left < 0:
            self.player.rect.left = 0
            self.player.x = self.player.rect.x
        if self.player.rect.right > self.level_manager.width:
            self.player.rect.right = self.level_manager.width
            self.player.x = self.player.rect.x
        self.player.y += self.player.vy
        on_ground = self.player.resolve_vertical_collisions(all_platforms)
        if self.player.rect.top < 0:
            self.player.rect.top = 0
            self.player.y = self.player.rect.y
        if self.player.rect.bottom > self.level_manager.height:
            self.player.rect.bottom = self.level_manager.height
            self.player.y = self.player.rect.y
            self.player.vy = 0
            self.player.jumps_remaining = self.player.max_jumps
        self.player.rect.x = int(self.player.x)
        self.player.rect.y = int(self.player.y)
        self.update_camera()
        for enemy in self.level_manager.enemies:
            enemy.update()

    def update_camera(self):
        """Update camera position to follow the player."""
        self.camera_x = int(self.player.rect.centerx - SCREEN_WIDTH // 2)
        self.camera_y = int(self.player.rect.centery - SCREEN_HEIGHT // 2)
        self.camera_x = max(0, min(self.level_manager.width - SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0, min(self.level_manager.height - SCREEN_HEIGHT, self.camera_y))

    def check_collisions(self):
        """Check and handle all collision types (presents, powerups, enemies, goal)."""
        collected_presents = self.player.check_present_collision(self.level_manager.presents)
        for present in collected_presents:
            if present in self.level_manager.presents:
                self.level_manager.presents.remove(present)
                self.score += 1
                show_message('Present collected!', MESSAGE_DURATION_SHORT)
        collected_powerups = self.player.check_powerup_collision(self.level_manager.powerups)
        for powerup in collected_powerups:
            if powerup in self.level_manager.powerups:
                ptype = powerup['type']
                durations = {'double_jump': DOUBLE_JUMP_DURATION, 'speed_boost': SPEED_BOOST_DURATION, 'invincibility': INVINCIBILITY_DURATION}
                self.player.apply_powerup(ptype, durations[ptype], self.now)
                self.level_manager.powerups.remove(powerup)
                show_message(f'Powerup: {ptype}', MESSAGE_DURATION_MEDIUM)
        collided_enemy = self.player.check_enemy_collision(self.level_manager.enemies)
        if collided_enemy:
            if not self.player.is_invincible(self.now):
                self.handle_enemy_collision()
        if self.player.check_goal_collision(self.level_manager.goal):
            self.handle_goal_collision()

    def handle_enemy_collision(self):
        """Handle player collision with enemies."""
        self.lives -= 1
        if self.lives <= 0:
            show_message('Game Over! Restarting...', MESSAGE_DURATION_GAME_OVER)
            pygame.time.delay(1200)
            self.restart_game()
        else:
            self.player.respawn(*self.level_manager.player_start)
            show_message('You lost a life!', MESSAGE_DURATION_SHORT)

    def handle_goal_collision(self):
        """Handle player collision with goal (tree)."""
        if self.score >= self.level_manager.total_presents:
            if not self.level_manager.completed:
                self.level_manager.completed = True
                self.level_complete_time = pygame.time.get_ticks()
                show_message('Level Complete!', MESSAGE_DURATION_MEDIUM)
        else:
            show_message('Collect all presents before the tree!', MESSAGE_DURATION_LONG)

    def handle_level_progression(self):
        """Handle level completion and progression to next level."""
        if self.level_manager.completed and self.level_complete_time is not None and (pygame.time.get_ticks() - self.level_complete_time > LEVEL_COMPLETE_DELAY):
            if self.level_manager.next_level():
                self.player = Player(*self.level_manager.player_start)
                self.score = 0
                self.level_manager.completed = False
                self.level_complete_time = None
            else:
                self.handle_game_victory()

    def handle_game_victory(self):
        """Handle game completion (all levels finished)."""
        self.screen.fill(GAME_OVER_BACKGROUND_COLOR)
        text = self.big_font.render('You saved Christmas! 🎅🎉', True, COLOR_WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(3000)
        self.restart_game()

    def restart_game(self):
        """Restart the entire game from the beginning."""
        self.level_manager = LevelManager(LEVELS)
        self.player = Player(*self.level_manager.player_start)
        self.lives = STARTING_LIVES
        self.score = 0
        self.level_complete_time = None

    def render(self):
        """Render all game elements to the screen."""
        if self.level_manager.background:
            self.screen.blit(self.level_manager.background, (-self.camera_x, -self.camera_y))
        else:
            self.screen.fill(FALLBACK_SCREEN_COLOR)
        self.screen.blit(self.level_manager.overlay, (-self.camera_x, -self.camera_y))
        self.render_ground()
        self.render_platforms()
        self.render_presents()
        self.render_powerups()
        self.render_enemies()
        self.render_goal()
        self.player.draw(self.screen, self.camera_x, self.camera_y, self.now)
        self.render_hud()
        draw_message(self.screen, SCREEN_WIDTH)

    def render_ground(self):
        """Render the ground platform with tiling."""
        tile = pygame.image.load('assets/ground.png').convert_alpha()
        tile_width = tile.get_width()
        tile_height = tile.get_height()
        for x in range(0, self.level_manager.ground.width, tile_width):
            self.screen.blit(tile, (self.level_manager.ground.x + x - self.camera_x, self.level_manager.ground.y - self.camera_y))

    def render_platforms(self):
        """Render all floating platforms."""
        for plat in self.level_manager.platforms:
            surf = get_texture('platform', (plat.width, plat.height))
            self.screen.blit(surf, (plat.x - self.camera_x, plat.y - self.camera_y))

    def render_presents(self):
        """Render all presents."""
        for present in self.level_manager.presents:
            surf = get_texture(present['texture'], (present['rect'].width, present['rect'].height))
            self.screen.blit(surf, (present['rect'].x - self.camera_x, present['rect'].y - self.camera_y))

    def render_powerups(self):
        """Render all powerups."""
        for powerup in self.level_manager.powerups:
            surf = get_texture(powerup['type'], (powerup['rect'].width, powerup['rect'].height))
            self.screen.blit(surf, (powerup['rect'].x - self.camera_x, powerup['rect'].y - self.camera_y))

    def render_enemies(self):
        """Render all enemies."""
        for enemy in self.level_manager.enemies:
            surf = enemy.texture
            if not enemy.facing_right:
                surf = pygame.transform.flip(surf, True, False)
            self.screen.blit(surf, (enemy.rect.x - self.camera_x, enemy.rect.y - self.camera_y))

    def render_goal(self):
        """Render the goal (tree)."""
        tree_texture_name = 'tree1' if self.level_manager.completed else 'tree'
        surf_tree = get_texture(tree_texture_name, (self.level_manager.goal.width, self.level_manager.goal.height))
        self.screen.blit(surf_tree, (self.level_manager.goal.x - self.camera_x, self.level_manager.goal.y - self.camera_y))

    def render_hud(self):
        """Render the Heads-Up Display."""
        draw_hud(self.screen, self.lives, self.level_manager.index, self.level_manager.name, self.score, self.level_manager.total_presents, self.player, SCREEN_WIDTH)

    def update(self):
        """Update all game systems for one frame."""
        self.now = pygame.time.get_ticks()
        self.player.update_powerups(self.now)
        self.handle_level_progression()

    def run(self):
        """Run the main game loop."""
        self.running = True
        while self.running:
            self.dt_ms = self.clock.tick(FPS)
            self.now = pygame.time.get_ticks()
            if not self.handle_events():
                self.running = False
                continue
            self.handle_input()
            self.update()
            self.update_physics()
            self.check_collisions()
            self.render()
            pygame.display.flip()
        pygame.quit()

    def quit_game(self):
        """Quit the game gracefully."""
        self.running = False

def run_game(screen=None, levels_data=None):
    """
    Convenience function to run the game with optional custom screen and levels.

    Args:
        screen (pygame.Surface, optional): Custom screen surface
        levels_data (list, optional): Custom level data

    Returns:
        Game: The game instance (useful for testing)
    """
    game = Game(screen, levels_data)
    game.run()
    return game