from pathlib import Path

WIDTH, HEIGHT = 480, 640
FPS = 60
TITLE = "Flappy Bird – Maturita"

GROUND_H = 80
GRAVITY = 900
FLAP_VELOCITY = -300
PIPE_SPEED = 180
PIPE_GAP = 170
PIPE_SPAWN_EVERY = 1.25

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True, parents=True)
DB_PATH = DATA / "db.sqlite3"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (30, 30, 30)
ACCENT = (250, 200, 50)
GREEN = (60, 180, 60)
BLUE = (66, 170, 255)
BROWN = (120, 80, 40)
