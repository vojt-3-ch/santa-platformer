from pathlib import Path
from constants import ASSETS_DIR, FALLBACK_BACKGROUND_COLOR, OVERLAY_ALPHA, GROUND_HEIGHT

def create_level_data(name, width, height, player_start, goal, platforms, presents, enemies=None, powerups=None, background_name=None):
    return {'name': name, 'width': width, 'height': height, 'player_start': player_start, 'goal': goal, 'platforms': platforms, 'presents': presents, 'enemies': enemies or [], 'powerups': powerups or [], 'background_name': background_name, 'ground': (0, height - GROUND_HEIGHT, width, GROUND_HEIGHT)}
LEVELS = [
    create_level_data(
        name="Snowy Village",
        width=1600,
        height=600,
        player_start=(80, 480),
        goal=(1500, 480, 60, 80), 
        platforms=[
            (200, 430, 160, 20),
            (420, 330, 160, 20),
            (700, 460, 200, 20),
            (1100, 380, 200, 20),
            (1350, 300, 180, 20),
        ],
        presents=[
            (220, 400, 30, 30),
            (460, 300, 30, 30),
            (760, 430, 30, 30),
            (1120, 350, 30, 30),
            (1370, 270, 30, 30),
        ],
        enemies=[
            # x, y, w, h, patrol_min_x, patrol_max_x, speed
            (780, 420, 40, 40, 700, 860, 2),
            (1180, 340, 40, 40, 1100, 1260, 1.5),
        ],
        powerups=[
            {"rect": (520, 480, 24, 24), "type": "double_jump"},
            {"rect": (900, 420, 24, 24), "type": "speed_boost"},
        ],
        background_name="bckg1"
    ),

    create_level_data(
        name="Icicle Climb",
        width=1200,
        height=800,
        player_start=(60, 700),
        goal=(1100, 700, 60, 80),
        platforms=[
            (100, 650, 200, 20),
            (250, 520, 150, 20),
            (100, 400, 120, 20),
            (250, 300, 150, 20),
            (450, 250, 130, 20),
            (750, 250, 150, 20),
        ],
        presents=[
            (150, 620, 30, 30),
            (300, 490, 30, 30),
            (150, 370, 30, 30),
            (325, 270, 30, 30),
            (515, 220, 30, 30),
        ],
        enemies=[
            (325, 480, 40, 40, 270, 380, 2.2),
            (325, 260, 40, 40, 270, 380, 1.7),
        ],
        powerups=[
            {"rect": (725, 170, 24, 24), "type": "invincibility"},
        ],
        background_name="bckg2"
    ),

    create_level_data(
        name="Frosty Peaks",
        width=1400,
        height=700,
        player_start=(70, 600),
        goal=(1300, 600, 60, 80),
        platforms=[
            (200, 550, 160, 20),
            (400, 450, 160, 20),
            (650, 350, 160, 20),
            (900, 250, 160, 20),
            (1150, 150, 160, 20),
        ],
        presents=[
            (220, 520, 30, 30),
            (420, 420, 30, 30),
            (670, 320, 30, 30),
            (920, 220, 30, 30),
            (1170, 120, 30, 30),
        ],
        enemies=[
            (1000, 620, 40, 40, 700, 1300, 2.5),
            (980, 210, 40, 40, 920, 1040, 2),
            (730, 310, 40, 40, 670, 790, 2),
        ],
        powerups=[
            {"rect": (750, 310, 24, 24), "type": "invincibility"},
        ],
        background_name="bckg1"
    ),
	
    create_level_data(
        name="Gummy Bear Forest",
        width=1600,
        height=600,
        player_start=(80, 480),
        goal=(1500, 480, 60, 80), 
        platforms=[
            (150, 480, 180, 20),
            (380, 380, 180, 20),
            (650, 510, 220, 20),
            (1050, 430, 220, 20),
            (1300, 350, 200, 20),
        ],
        presents=[
            (170, 450, 30, 30),
            (400, 350, 30, 30),
            (710, 480, 30, 30),
            (1070, 400, 30, 30),
            (1320, 320, 30, 30),
        ],
        enemies=[
            (730, 470, 40, 40, 650, 800, 2.3),
            (1130, 390, 40, 40, 1050, 1200, 1.8),
        ],
        powerups=[
            {"rect": (480, 430, 24, 24), "type": "speed_boost"},
            {"rect": (950, 380, 24, 24), "type": "double_jump"},
        ],
        background_name="bckg1"
    ),

    create_level_data(
        name="Castle Guard",
        width=2000,
        height=800,
        player_start=(100, 700),
        goal=(1900, 700, 60, 80),
        platforms=[
            (200, 650, 150, 20),
            (400, 550, 150, 20),
            (600, 450, 150, 20),
            (800, 350, 150, 20),
            (1000, 250, 150, 20),
            (1200, 150, 150, 20),
            (1400, 250, 150, 20),
        ],
        presents=[
            (250, 620, 30, 30),
            (450, 520, 30, 30),
            (650, 420, 30, 30),
            (850, 320, 30, 30),
            (1050, 220, 30, 30),
        ],
        enemies=[
            (420, 510, 40, 40, 400, 550, 2),
            (620, 410, 40, 40, 600, 750, 2),
            (820, 310, 40, 40, 800, 950, 2),
            (1020, 210, 40, 40, 1000, 1150, 2),
            (1220, 110, 40, 40, 1200, 1350, 2),
            (1420, 210, 40, 40, 1400, 1550, 2),
        ],
        powerups=[
            {"rect": (1600, 100, 24, 24), "type": "invincibility"},
            {"rect": (1263, 126, 24, 24), "type": "double_jump"},
        ],
        background_name="bckg2"
    )
]

class LevelMetadata:

    def __init__(self, levels_data):
        self.levels_data = levels_data
        self.total_levels = len(levels_data)

    def get_level(self, index):
        if 0 <= index < self.total_levels:
            return self.levels_data[index]
        raise IndexError(f'Level index {index} out of range (0-{self.total_levels - 1})')

    def get_level_by_name(self, name):
        for level in self.levels_data:
            if level['name'] == name:
                return level
        raise ValueError(f"Level '{name}' not found")

    def get_background_path(self, level_index):
        level = self.get_level(level_index)
        bg_name = level.get('background_name')
        if bg_name:
            return ASSETS_DIR / f'{bg_name}.png'
        return None

    def get_present_textures(self):
        return ['present', 'present1', 'present2', 'present3']

    def get_powerup_types(self):
        return ['double_jump', 'speed_boost', 'invincibility']

    def get_powerup_durations(self):
        return {'double_jump': 15000, 'speed_boost': 8000, 'invincibility': 6000}

def validate_level_data(level_data):
    required_fields = ['name', 'width', 'height', 'player_start', 'goal', 'platforms', 'presents', 'enemies', 'powerups']
    for field in required_fields:
        if field not in level_data:
            raise ValueError(f'Missing required field: {field}')
    if not isinstance(level_data['name'], str):
        raise ValueError('Level name must be a string')
    if not isinstance(level_data['width'], int) or level_data['width'] <= 0:
        raise ValueError('Level width must be a positive integer')
    if not isinstance(level_data['height'], int) or level_data['height'] <= 0:
        raise ValueError('Level height must be a positive integer')
    if not isinstance(level_data['player_start'], (tuple, list)) or len(level_data['player_start']) != 2:
        raise ValueError('Player start must be a tuple/list of (x, y)')
    if not isinstance(level_data['goal'], (tuple, list)) or len(level_data['goal']) != 4:
        raise ValueError('Goal must be a tuple/list of (x, y, width, height)')
    if not isinstance(level_data['platforms'], (tuple, list)):
        raise ValueError('Platforms must be a tuple/list')
    if not isinstance(level_data['presents'], (tuple, list)):
        raise ValueError('Presents must be a tuple/list')
    if not isinstance(level_data['enemies'], (tuple, list)):
        raise ValueError('Enemies must be a tuple/list')
    if not isinstance(level_data['powerups'], (tuple, list)):
        raise ValueError('Powerups must be a tuple/list')
    return True

def create_empty_level(name='New Level', width=800, height=600):
    return create_level_data(name=name, width=width, height=height, player_start=(50, height - 100), goal=(width - 100, height - 100, 60, 80), platforms=[(200, height - 150, 150, 20), (400, height - 250, 150, 20), (600, height - 200, 150, 20)], presents=[(220, height - 180, 30, 30), (420, height - 280, 30, 30), (620, height - 230, 30, 30)], enemies=[], powerups=[])
level_metadata = LevelMetadata(LEVELS)
for i, level in enumerate(LEVELS):
    try:
        validate_level_data(level)
    except ValueError as e:
        print(f"Warning: Level {i} ({level.get('name', 'Unknown')}) has invalid data: {e}")
__all__ = ['LEVELS', 'LevelMetadata', 'level_metadata', 'create_level_data', 'validate_level_data', 'create_empty_level']