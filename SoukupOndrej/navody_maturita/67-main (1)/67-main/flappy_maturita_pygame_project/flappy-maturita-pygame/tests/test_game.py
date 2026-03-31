import sys
from pathlib import Path
import importlib

CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"
sys.path.insert(0, str(CLIENT_DIR))

game = importlib.import_module("main")


def test_circle_rect_collide_hits_pipe():
    # kruh zasahuje do obdélníku
    hit = game.circle_rect_collide(
        cx=100, cy=100, cr=20,
        rx=110, ry=90, rw=50, rh=80
    )
    assert hit is True


def test_circle_rect_collide_misses_pipe():
    # kruh je mimo obdélník
    hit = game.circle_rect_collide(
        cx=50, cy=50, cr=10,
        rx=200, ry=200, rw=60, rh=120
    )
    assert hit is False