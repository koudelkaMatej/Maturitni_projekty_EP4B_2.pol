import pygame, settings

class Piece:
    def __init__(self, grid, index):
        self.grid = grid
        self.shape = settings.SHAPES[index]
        self.color = settings.SHAPE_COLORS[index]
        self.x = settings.COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        old = self.shape
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        if not self.valid(): self.shape = old

    def valid(self, dx=0, dy=0):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    nx, ny = self.x + x + dx, self.y + y + dy
                    if not (0 <= nx < settings.COLUMNS and 0 <= ny < settings.ROWS) or \
                       (ny >= 0 and self.grid[ny][nx]): return False
        return True

    def place(self):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell: self.grid[self.y + y][self.x + x] = self.color

class Button:
    def __init__(self, x, y, w, h, text, font, color=settings.PRIMARY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text, self.font, self.color = text, font, color

    def draw(self, win):
        m = pygame.mouse.get_pos()
        h = self.rect.collidepoint(m)
        pygame.draw.rect(win, (30,30,30) if h else (15,15,15), self.rect, border_radius=10)
        pygame.draw.rect(win, self.color if h else (80,80,80), self.rect, 2, border_radius=10)
        txt = self.font.render(self.text, True, (255,255,255))
        win.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, e):
        return e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos)