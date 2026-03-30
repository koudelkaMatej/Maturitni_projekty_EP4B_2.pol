# constants.py
# Tady jsou všechny konstanty co používám v celém projektu.
# Barvy, rozměry okna, nastavení obtížnosti atd.

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
FPS           = 60

PLAYER_WIDTH  = 240
PLAYER_HEIGHT = 120
FALL_SIZE     = 80

# Aktuální obtížnost - mění se v nastavení
settings = {'difficulty': 'Normal'}

# Parametry pro každou obtížnost:
# fall_speed     = základní rychlost padání objektů
# spawn_interval = jak často (ms) se spawní nový objekt
# speed_increase = o kolik % se zrychlí každých 20 sekund
DIFFICULTY_PARAMS = {
    'Easy':   {'fall_speed': 2,   'spawn_interval': 900, 'speed_increase': 0.04},
    'Normal': {'fall_speed': 3,   'spawn_interval': 700, 'speed_increase': 0.07},
    'Hard':   {'fall_speed': 4.5, 'spawn_interval': 450, 'speed_increase': 0.09},
}

# Barvy (RGB)
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0  )
RED       = (220, 40,  40 )
GREEN     = (50,  200, 50 )
DARK_GRAY = (50,  50,  50 )
GRAY      = (200, 200, 200)
PURPLE    = (128, 0,   128)
GOLD      = (255, 215, 0  )
