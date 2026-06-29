SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "银纹秘境：彝饰守护者"
DEBUG_COLLISION = False
DEBUG_OVERLAY = True

SCENES_CONFIG_PATH = "data/scenes.json"
DEFAULT_SCENE = "village"

SCENE_MAPS = {
    "village": "assets/maps/village_hub.tmx",
    "mountain": "assets/maps/river_valley.tmx",
    "workshop": "assets/maps/workshop_interior.tmx",
    "festival": "assets/maps/festival_square.tmx",
    "pattern_mountain": "assets/maps/pattern_mountain.tmx",
}

DISABLED_SCENE_MAPS = {
    "market": "assets/maps/village_market.tmx",
    "pattern_water": "assets/maps/pattern_water.tmx",
    "pattern_sun": "assets/maps/pattern_sun.tmx",
    "pattern_flower_bird": "assets/maps/pattern_flower_bird.tmx",
    "village_entrance": "assets/maps/village_entrance.tmx",
    "workshop_exterior": "assets/maps/workshop_exterior.tmx",
}

SCENE_ALIASES = {
    "village_hub": "village",
    "village_market": "market",
    "river_valley": "mountain",
    "workshop_exterior": "workshop",
    "workshop_interior": "workshop",
    "festival_square": "festival",
    "festival_plaza": "festival",
    "festival_scene": "festival",
    "plaza": "festival",
}
