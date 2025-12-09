import pygame
from constants import GRAVITY, MAX_FALL, BASE_SPEED, BASE_JUMP, PLAYER_WIDTH, PLAYER_HEIGHT, SPEED_BOOST_MULTIPLIER, RESPAWN_INVINCIBILITY_DURATION, HIT_INVINCIBILITY_FLICKER
from assets import get_texture

class Player:

    def __init__(self, start_x, start_y):
        self.w, self.h = (PLAYER_WIDTH, PLAYER_HEIGHT)
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
        self.power_until = {'speed_boost': 0, 'double_jump': 0, 'invincibility': 0}
        self.hit_invincible_until = 0
        self.idle_frame = get_texture('player', (self.w, self.h))
        self.walk_frames = [get_texture('player1', (self.w, self.h)), get_texture('player2', (self.w, self.h))]
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200

    def update_animation(self, dt_ms):
        if self.vx != 0:
            self.animation_timer += dt_ms
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
        else:
            self.current_frame = 0

    def get_current_frame(self):

        if self.vx != 0:
            frame = self.walk_frames[self.current_frame]
        else:
            frame = self.idle_frame
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        return frame

    def is_invincible(self, now_ms):
        return now_ms < self.power_until['invincibility'] or now_ms < self.hit_invincible_until

    def update_powerups(self, now_ms):
        if now_ms < self.power_until['speed_boost']:
            self.speed = self.base_speed * SPEED_BOOST_MULTIPLIER
        else:
            self.speed = self.base_speed
        if now_ms < self.power_until['double_jump']:
            self.max_jumps = 2
        else:
            self.max_jumps = 1

    def apply_powerup(self, ptype, duration_ms, now_ms):
        self.power_until[ptype] = now_ms + duration_ms
        if ptype == 'double_jump':
            self.jumps_remaining = self.max_jumps if now_ms < self.power_until['double_jump'] else self.jumps_remaining

    def respawn(self, start_x, start_y):
        self.x = float(start_x)
        self.y = float(start_y)
        self.rect.topleft = (start_x, start_y)
        self.vx = 0
        self.vy = 0
        self.hit_invincible_until = pygame.time.get_ticks() + RESPAWN_INVINCIBILITY_DURATION

    def set_movement(self, direction, move):
        if direction == 'left':
            self.vx = -self.speed if move else 0
            if move:
                self.facing_right = False
        elif direction == 'right':
            self.vx = self.speed if move else 0
            if move:
                self.facing_right = True

    def jump(self):
        if self.jumps_remaining > 0:
            self.vy = self.jump_strength
            self.jumps_remaining -= 1
            return True
        return False

    def apply_physics(self):
        self.vy += GRAVITY
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL
        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def resolve_horizontal_collisions(self, platforms):
        self.rect.x = int(self.x)
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vx > 0:
                    self.rect.right = plat.left
                elif self.vx < 0:
                    self.rect.left = plat.right
                self.x = self.rect.x

    def resolve_vertical_collisions(self, platforms):
        self.rect.y = int(self.y)
        on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vy > 0:
                    self.rect.bottom = plat.top
                    self.vy = 0
                    self.y = self.rect.y
                    on_ground = True
                    self.jumps_remaining = self.max_jumps
                elif self.vy < 0:
                    self.rect.top = plat.bottom
                    self.vy = 0
                    self.y = self.rect.y
        return on_ground

    def clamp_to_level_bounds(self, level_width, level_height):
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.x
        if self.rect.right > level_width:
            self.rect.right = level_width
            self.x = self.rect.x
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.y
        if self.rect.bottom > level_height:
            self.rect.bottom = level_height
            self.y = self.rect.y
            self.vy = 0
            self.jumps_remaining = self.max_jumps

    def check_enemy_collision(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                return enemy
        return None

    def check_present_collision(self, presents):
        collected = []
        for present in presents[:]:
            if self.rect.colliderect(present['rect']):
                collected.append(present)
        return collected

    def check_powerup_collision(self, powerups):
        collected = []
        for powerup in powerups[:]:
            if self.rect.colliderect(powerup['rect']):
                collected.append(powerup)
        return collected

    def check_goal_collision(self, goal_rect):
        return self.rect.colliderect(goal_rect)

    def draw(self, screen, camera_x, camera_y, now_ms):
        dt_ms = 16
        self.update_animation(dt_ms)
        surf_player = self.get_current_frame()
        if not (self.is_invincible(now_ms) and now_ms // HIT_INVINCIBILITY_FLICKER % 2 == 0):
            screen.blit(surf_player, (self.rect.x - camera_x, self.rect.y - camera_y))