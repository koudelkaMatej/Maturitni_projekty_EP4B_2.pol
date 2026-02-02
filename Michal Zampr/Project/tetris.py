import pygame
import random

pygame.init()

# ---------- CONSTANTS ----------
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
COLS, ROWS = 10, 20

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 24)

BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
WHITE = (220, 220, 220)

SHAPES = [
    [[1, 1, 1, 1]],                  # I
    [[1, 1], [1, 1]],                # O
    [[0, 1, 0], [1, 1, 1]],           # T
    [[1, 0, 0], [1, 1, 1]],           # L
    [[0, 0, 1], [1, 1, 1]],           # J
    [[1, 1, 0], [0, 1, 1]],           # S
    [[0, 1, 1], [1, 1, 0]]            # Z
]

COLORS = [
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (255, 165, 0),
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0)
]

# ---------- CLASSES ----------
class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = COLORS[SHAPES.index(self.shape)]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))

# ---------- FUNCTIONS ----------
def create_grid(locked):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked.items():
        if y >= 0:
            grid[y][x] = color
    return grid

def valid_move(piece, grid, dx=0, dy=0):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece.x + x + dx
                new_y = piece.y + y + dy
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False
                if new_y >= 0 and grid[new_y][new_x] != BLACK:
                    return False
    return True

def clear_lines(grid, locked):
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            for x in range(COLS):
                del locked[(x, y)]
            for (x, yy) in sorted(list(locked), key=lambda k: k[1])[::-1]:
                if yy < y:
                    locked[(x, yy + 1)] = locked.pop((x, yy))
    return cleared

def draw_grid(grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(
                SCREEN,
                grid[y][x],
                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
            )
            pygame.draw.rect(
                SCREEN,
                GRAY,
                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                1,
            )

def draw_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    SCREEN,
                    piece.color,
                    ((piece.x + x) * BLOCK_SIZE,
                     (piece.y + y) * BLOCK_SIZE,
                     BLOCK_SIZE,
                     BLOCK_SIZE),
                )

# ---------- MAIN GAME ----------
def main():
    locked = {}
    grid = create_grid(locked)
    piece = Piece()
    fall_time = 0
    fall_speed = 60
    score = 0
    running = True

    while running:
        grid = create_grid(locked)
        fall_time += CLOCK.get_rawtime()
        CLOCK.tick(60)

        if fall_time > fall_speed:
            fall_time = 0
            if valid_move(piece, grid, dy=1):
                piece.y += 1
            else:
                for y, row in enumerate(piece.shape):
                    for x, cell in enumerate(row):
                        if cell:
                            locked[(piece.x + x, piece.y + y)] = piece.color
                piece = Piece()
                score += clear_lines(grid, locked) * 100
                if not valid_move(piece, grid):
                    running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and valid_move(piece, grid, dx=-1):
                    piece.x -= 1
                elif event.key == pygame.K_RIGHT and valid_move(piece, grid, dx=1):
                    piece.x += 1
                elif event.key == pygame.K_DOWN and valid_move(piece, grid, dy=1):
                    piece.y += 1
                elif event.key == pygame.K_UP:
                    old_shape = piece.shape
                    piece.rotate()
                    if not valid_move(piece, grid):
                        piece.shape = old_shape

        SCREEN.fill(BLACK)
        draw_grid(grid)
        draw_piece(piece)

        score_text = FONT.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        pygame.display.flip()

    print("Game Over! Final Score:", score)

if __name__ == "__main__":
    main()
