import pygame 
import sys
import random
import os
from pathlib import Path

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

GRAVITY = 0.6          # px/frame^2
MAX_FALL = 15          # terminal velocity
BASE_SPEED = 5         # px/frame
BASE_JUMP = -13        # px/frame

STARTING_LIVES = 3

ASSETS_DIR = Path(__file__).parent / "assets"

# --- Utilities: texture loader with cache and fallback ---
_texture_cache = {}

def get_texture(name, size):
    
    key = (name, size)
    if key in _texture_cache:
        return _texture_cache[key]

    path = ASSETS_DIR / f"{name}.png"
    w, h = size
    surf = None
    if path.exists():
        try:
            img = pygame.image.load(str(path)).convert_alpha()
            surf = pygame.transform.smoothscale(img, (w, h))
        except Exception as e:
            print("Failed to load", path, e)

    if surf is None:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        colors = {
            'player': (200, 40, 40),
            'platform': (139, 69, 19),
            'present': (255, 215, 0),
            'enemy': (245, 245, 245),
            'tree': (20, 120, 20),
            'double_jump': (150, 50, 200),
            'speed_boost': (50, 120, 255),
            'invincibility': (255, 200, 60),
        }
        color = colors.get(name, (120, 120, 120))
        surf.fill(color)
        # small decorations
        if name == 'present':
            pygame.draw.rect(surf, (180, 20, 20), (w//4, 0, w//2, h))         # ribbon vertical
            pygame.draw.rect(surf, (200, 40, 40), (0, h//3, w, h//6))        # ribbon horizontal
        elif name == 'player':
            pygame.draw.rect(surf, (255, 255, 255), (w//6, h//6, w//6, h//8))  # faux beard
        elif name == 'tree':
            pygame.draw.polygon(surf, (10, 80, 10), [(w//2, 0), (w, h), (0, h)])
    _texture_cache[key] = surf
    return surf

# --- Classes ---
class Player:
    def __init__(self, start_x, start_y):
        self.w, self.h = 40, 60
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

        # powerups timers
        self.power_until = {'speed_boost':0,'double_jump':0,'invincibility':0}
        self.hit_invincible_until = 0

        # --- Animation ---
        self.idle_frame = get_texture("player", (self.w, self.h))
        self.walk_frames = [
            get_texture("player1", (self.w, self.h)),
            get_texture("player2", (self.w, self.h))
        ]
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200  # ms per frame

    def update_animation(self, dt_ms):
        if self.vx != 0:  # moving
            self.animation_timer += dt_ms
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
        else:
            self.current_frame = 0  # reset walk animation when idle

    def get_current_frame(self):
        if self.vx != 0:  # moving
            frame = self.walk_frames[self.current_frame]
        else:  # idle
            frame = self.idle_frame

        # Flip horizontally if facing left
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        return frame

    def is_invincible(self, now_ms):
        return now_ms < self.power_until['invincibility'] or now_ms < self.hit_invincible_until

    def update_powerups(self, now_ms):
        # speed boost duration effect
        if now_ms < self.power_until['speed_boost']:
            self.speed = self.base_speed * 1.8
        else:
            self.speed = self.base_speed

        # double jump effect
        if now_ms < self.power_until['double_jump']:
            self.max_jumps = 2
        else:
            self.max_jumps = 1

        # reset jumps when landing handled elsewhere
        # invincibility handled in is_invincible()

    def apply_powerup(self, ptype, duration_ms, now_ms):
        self.power_until[ptype] = now_ms + duration_ms
        # if double jump power gained immediately refill jumps so player can use it right away
        if ptype == 'double_jump':
            self.jumps_remaining = self.max_jumps if now_ms < self.power_until['double_jump'] else self.jumps_remaining

    def respawn(self, start_x, start_y):
        self.x = float(start_x)
        self.y = float(start_y)
        self.rect.topleft = (start_x, start_y)
        self.vx = 0
        self.vy = 0
        # give a short invincible window after respawn
        self.hit_invincible_until = pygame.time.get_ticks() + 1200

class Enemy:
    def __init__(self, x, y, w, h, patrol_min_x, patrol_max_x, speed=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.vx = speed
        self.patrol_min = patrol_min_x
        self.patrol_max = patrol_max_x
        self.speed = speed
        self.facing_right = True
        self.texture = get_texture('enemy', (w, h))


    def update(self):
        self.rect.x += self.vx

        if self.rect.x < self.patrol_min:
            self.rect.x = self.patrol_min
            self.vx = abs(self.speed)
            self.facing_right = True
        elif self.rect.x > self.patrol_max:
            self.rect.x = self.patrol_max
            self.vx = -abs(self.speed)
            self.facing_right = False


class LevelManager:
    def __init__(self, levels_data):
        self.completed = False
        self.levels = levels_data
        self.index = 0
        self.load_level(self.index)

    def load_level(self, index):
        data = self.levels[index]
        self.width = data.get('width', WIDTH)
        self.height = data.get('height', HEIGHT)

        # --- auto-generate ground at the bottom ---
        ground_height = 40
        self.ground = pygame.Rect(0, self.height - ground_height, self.width, ground_height)

        # --- floating platforms ---
        self.platforms = [pygame.Rect(*p) for p in data['platforms']]

        self.presents = []
        for p in data['presents']:
            rect = pygame.Rect(*p)
            texture = random.choice(["present", "present1", "present2", "present3"])
            self.presents.append({"rect": rect, "texture": texture})
        self.powerups = [{'rect': pygame.Rect(*p['rect']), 'type': p['type']} for p in data.get('powerups', [])]
        self.enemies = [Enemy(*e) for e in data.get('enemies', [])]
        sx, sy = data['player_start']
        gx, gy, gw, gh = data['goal']
        self.goal = pygame.Rect(gx, gy, gw, gh)
        self.player_start = (sx, sy)
        self.total_presents = len(self.presents)
        self.name = data.get('name', f"Level {index+1}")

        # --- Load background ---
        bg_path = ASSETS_DIR / f"bckg{index+1}.png"
        if bg_path.exists():
            bg_img = pygame.image.load(str(bg_path)).convert()
            self.background = pygame.transform.scale(bg_img, (self.width, self.height))
        else:
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((50, 50, 100))  # fallback color
        
        self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 120))

    def next_level(self):
        if self.index + 1 < len(self.levels):
            self.index += 1
            self.load_level(self.index)
            return True
        else:
            return False  # no more levels

# --- Level definitions (example: 2 levels) ---
LEVELS = [
    {
        "name": "Snowy Village",
        "width": 1600,
        "height": 600,
        "player_start": (80, 480),
        "goal": (1500, 480, 60, 80),  # tree
        "ground": (0, 560, 1600, 40),
        "platforms": [
            (200, 430, 160, 20),
            (420, 330, 160, 20),
            (700, 460, 200, 20),
            (1100, 380, 200, 20),
            (1350, 300, 180, 20),
        ],
        "presents": [
            (220, 400, 30, 30),
            (460, 300, 30, 30),
            (760, 430, 30, 30),
            (1120, 350, 30, 30),
            (1370, 270, 30, 30),
        ],
        "enemies": [
            # x,y,w,h, patrol_min_x, patrol_max_x, speed
            (600, 520, 40, 40, 500, 740, 2),
            (1300, 340, 40, 40, 1250, 1450, 1.5),
        ],
        "powerups": [
            {"rect": (520, 480, 24, 24), "type": "double_jump"},
            {"rect": (900, 420, 24, 24), "type": "speed_boost"},
        ]
    },

    {
        "name": "Icicle Climb",
        "width": 1200,
        "height": 800,
        "player_start": (60, 700),
        "goal": (1100, 700, 60, 80),
        "ground": (0, 760, 1200, 40),
        "platforms": [
            (150, 640, 130, 20),
            (320, 520, 130, 20),
            (510, 400, 130, 20),
            (720, 280, 130, 20),
            (920, 160, 130, 20),
        ],
        "presents": [
            (170, 510, 30, 30),
            (340, 490, 30, 30),
            (530, 370, 30, 30),
            (740, 250, 30, 30),
            (940, 130, 30, 30),
        ],
        "enemies": [
            (400, 720, 40, 40, 300, 520, 2.2),
            (800, 720, 40, 40, 760, 980, 1.7),
        ],
        "powerups": [
            {"rect": (600, 360, 24, 24), "type": "invincibility"},
        ]
    }
]

# --- Game Initialization ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Santa Platformer (Pygame)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 48)

level_manager = LevelManager(LEVELS)

player = Player(*level_manager.player_start)
lives = STARTING_LIVES
score = 0
level_complete_time = None

camera_x = 0
camera_y = 0

# message display helpers
message = ""
message_until = 0

def show_message(text, ms=1500):
    global message, message_until
    message = text
    message_until = pygame.time.get_ticks() + ms

# --- Collision helpers ---
def resolve_horizontal(player, platforms):
    player.rect.x = int(player.x)
    for plat in platforms:
        if player.rect.colliderect(plat):
            if player.vx > 0:
                player.rect.right = plat.left
            elif player.vx < 0:
                player.rect.left = plat.right
            player.x = player.rect.x

def resolve_vertical(player, platforms):
    player.rect.y = int(player.y)
    on_ground = False
    for plat in platforms:
        if player.rect.colliderect(plat):
            if player.vy > 0:
                # falling -> land on top
                player.rect.bottom = plat.top
                player.vy = 0
                player.y = player.rect.y
                on_ground = True
                # refill jumps when landing
                player.jumps_remaining = player.max_jumps
            elif player.vy < 0:
                # hit bottom of platform
                player.rect.top = plat.bottom
                player.vy = 0
                player.y = player.rect.y
    return on_ground

def draw_hud():
    # Lives, Level, Score
    lives_surf = font.render(f"Lives: {lives}", True, (255,255,255))
    level_surf = font.render(f"Level: {level_manager.index+1} - {level_manager.name}", True, (255,255,255))
    score_surf = font.render(f"Presents: {score}/{level_manager.total_presents}", True, (255,255,255))
    screen.blit(lives_surf, (10, 8))
    screen.blit(level_surf, (10, 32))
    screen.blit(score_surf, (10, 56))

    # active powerups + timers
    now = pygame.time.get_ticks()
    x = WIDTH - 10
    y = 8
    for ptype in ['double_jump','speed_boost','invincibility']:
        end = player.power_until[ptype]
        if end > now:
            remain_s = (end - now) // 1000 + 1
            text = f"{ptype} {remain_s}s"
            surf = font.render(text, True, (255,255,255))
            rect = surf.get_rect(topright=(x,y))
            screen.blit(surf, rect)
            y += 22

# --- Main loop ---
running = True
while running:
    dt_ms = clock.tick(FPS)
    now = pygame.time.get_ticks()

    # --- Events ---
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.key in (pygame.K_UP, pygame.K_SPACE, pygame.K_w):
                # jump press
                if player.jumps_remaining > 0:
                    player.vy = player.jump_strength
                    player.jumps_remaining -= 1
        elif ev.type == pygame.KEYUP:
            pass

    keys = pygame.key.get_pressed()
    player.vx = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.vx = -player.speed
        player.facing_right = False
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.vx = player.speed
        player.facing_right = True

    # update powerup effects
    player.update_powerups(now)

    # --- Physics ---
    # apply gravity
    player.vy += GRAVITY
    if player.vy > MAX_FALL:
        player.vy = MAX_FALL

    # update position floats
    player.x += player.vx
    # resolve horizontal collisions
    resolve_horizontal(player, [level_manager.ground] + level_manager.platforms)

    # clamp player within horizontal level bounds
    if player.rect.left < 0:
        player.rect.left = 0
        player.x = player.rect.x
    if player.rect.right > level_manager.width:
        player.rect.right = level_manager.width
        player.x = player.rect.x

    player.y += player.vy
    on_ground = resolve_vertical(player, [level_manager.ground] + level_manager.platforms)

    # clamp player vertically
    if player.rect.top < 0:
        player.rect.top = 0
        player.y = player.rect.y
    if player.rect.bottom > level_manager.height:
        player.rect.bottom = level_manager.height
        player.y = player.rect.y
        player.vy = 0
        player.jumps_remaining = player.max_jumps

    # keep player rect synchronized
    player.rect.x = int(player.x)
    player.rect.y = int(player.y)

    # --- Camera (simple follow, clamped to level bounds) ---
    camera_x = int(player.rect.centerx - WIDTH // 2)
    camera_y = int(player.rect.centery - HEIGHT // 2)
    # clamp
    camera_x = max(0, min(level_manager.width - WIDTH, camera_x))
    camera_y = max(0, min(level_manager.height - HEIGHT, camera_y))

    # --- Enemies update ---
    for e in level_manager.enemies:
        e.update()

    # --- Collisions: presents ---
    for p in level_manager.presents[:]:
        if player.rect.colliderect(p["rect"]):
            level_manager.presents.remove(p)
            score += 1
            show_message("Present collected!", 900)


    # --- Collisions: powerups ---
    for pu in level_manager.powerups[:]:
        if player.rect.colliderect(pu['rect']):
            ptype = pu['type']
            # durations in ms
            durations = {'double_jump': 15000, 'speed_boost': 8000, 'invincibility': 6000}
            player.apply_powerup(ptype, durations[ptype], now)
            level_manager.powerups.remove(pu)
            show_message(f"Powerup: {ptype}", 1100)

    # --- Collisions: enemies ---
    collided_enemy = None
    for e in level_manager.enemies:
        if player.rect.colliderect(e.rect):
            collided_enemy = e
            break

    if collided_enemy:
        if not player.is_invincible(now):
            lives -= 1
            if lives <= 0:
                # Game Over -> restart everything
                show_message("Game Over! Restarting...", 2000)
                pygame.time.delay(1200)
                # Restart full game
                level_manager = LevelManager(LEVELS)
                player = Player(*level_manager.player_start)
                lives = STARTING_LIVES
                score = 0
                continue
            else:
                # respawn player at start of current level
                player.respawn(*level_manager.player_start)
                show_message("You lost a life!", 900)

    # --- Goal check ---
    if player.rect.colliderect(level_manager.goal):
        if score >= level_manager.total_presents:
            if not level_manager.completed:
                # Mark level completed and start timer (don't switch levels yet)
                level_manager.completed = True
                level_complete_time = pygame.time.get_ticks()
                show_message("Level Complete!", 1500)
        else:
            show_message("Collect all presents before the tree!", 1300)

    # --- Drawing ---
    if level_manager.background:
        screen.blit(level_manager.background, (-camera_x, -camera_y))
    else:
        screen.fill((24, 36, 60))  # fallback
    
    screen.blit(level_manager.overlay, (-camera_x, -camera_y))

    # draw ground (tiled horizontally)
    tile = pygame.image.load("assets/ground.png").convert_alpha()
    tile_width = tile.get_width()
    tile_height = tile.get_height()

    for x in range(0, level_manager.ground.width, tile_width):
        screen.blit(tile, (level_manager.ground.x + x - camera_x,
                        level_manager.ground.y - camera_y))
        
    # draw floating platforms
    for plat in level_manager.platforms:
        surf = get_texture('platform', (plat.width, plat.height))
        screen.blit(surf, (plat.x - camera_x, plat.y - camera_y))

    # draw presents
    for p in level_manager.presents:
        surf = get_texture(p["texture"], (p["rect"].width, p["rect"].height))
        screen.blit(surf, (p["rect"].x - camera_x, p["rect"].y - camera_y))

    # draw powerups
    for pu in level_manager.powerups:
        surf = get_texture(pu['type'], (pu['rect'].width, pu['rect'].height))
        screen.blit(surf, (pu['rect'].x - camera_x, pu['rect'].y - camera_y))

    # draw enemies
    for e in level_manager.enemies:
        surf = e.texture
        if not e.facing_right:
            surf = pygame.transform.flip(surf, True, False)
        screen.blit(surf, (e.rect.x - camera_x, e.rect.y - camera_y))


    # draw goal (tree)
    tree_texture_name = 'tree1' if level_manager.completed else 'tree'
    surf_tree = get_texture(tree_texture_name, (level_manager.goal.width, level_manager.goal.height))
    screen.blit(surf_tree, (level_manager.goal.x - camera_x, level_manager.goal.y - camera_y))
    
    player.update_animation(dt_ms)  # dt_ms from clock.tick()
    surf_player = player.get_current_frame()

    # invincibility flicker
    if not (player.is_invincible(now) and (now // 150) % 2 == 0):
        screen.blit(surf_player, (player.rect.x - camera_x, player.rect.y - camera_y))

    # HUD
    draw_hud()

    # message text
    if message and now < message_until:
        m_surf = font.render(message, True, (255, 255, 255))
        screen.blit(m_surf, (WIDTH//2 - m_surf.get_width()//2, 8))
        # --- Handle delayed level switch ---
    if level_manager.completed and level_complete_time is not None:
        if pygame.time.get_ticks() - level_complete_time > 3000:  # wait 3 seconds
            advanced = level_manager.next_level()
            if advanced:
                player = Player(*level_manager.player_start)
                score = 0
                level_manager.completed = False
                level_complete_time = None
            else:
                # final victory
                screen.fill((10,10,40))
                text = big_font.render("You saved Christmas! 🎅🎉", True, (255,255,200))
                screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
                pygame.display.flip()
                pygame.time.delay(3000)
                # restart game
                level_manager = LevelManager(LEVELS)
                player = Player(*level_manager.player_start)
                lives = STARTING_LIVES
                score = 0
                level_complete_time = None
    pygame.display.flip()

pygame.quit()
sys.exit()