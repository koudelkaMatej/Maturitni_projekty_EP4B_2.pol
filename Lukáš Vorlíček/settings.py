# Rozměry a mřížka
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20
WIDTH = COLUMNS * BLOCK_SIZE
HEIGHT = ROWS * BLOCK_SIZE

# Neonové barvy
PRIMARY = (0, 242, 255)    # Cyan
SECONDARY = (112, 0, 255)  # Fialová
ACCENT = (255, 0, 200)     # Růžová
BG_COLOR = (10, 10, 10)

FPS, MAX_FPS = 5, 30
LEVEL_UP_SCORE = 300

# Tetrominoes
SHAPES = [
    [[1, 1, 1, 1]], # I
    [[1, 1], [1, 1]], # O
    [[0, 1, 0], [1, 1, 1]], # T
    [[1, 1, 0], [0, 1, 1]], # S
    [[0, 1, 1], [1, 1, 0]], # Z
    [[1, 0, 0], [1, 1, 1]], # J
    [[0, 0, 1], [1, 1, 1]]  # L
]
SHAPE_COLORS = [(0,255,255), (255,255,0), (128,0,128), (0,255,0), (255,0,0), (0,0,255), (255,165,0)]
FPS, MAX_FPS = 5, 30