import pygame as pg
from settings import WIDTH, HEIGHT, FPS, TITLE
from states.menu import Menu, HighScores
from states.game import Game
from states.game_over import GameOver

class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.state = None
        self.context = {}
        self.change_state("MENU")

    def change_state(self, name: str):
        if name == "MENU":
            self.state = Menu(self)
        elif name == "HIGHSCORES":
            self.state = HighScores(self)
        elif name == "GAME":
            self.state = Game(self)
        elif name == "GAMEOVER":
            self.state = GameOver(self)
        else:
            raise ValueError(f"Unknown state {name}")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                else:
                    self.state.handle_event(event)
            self.state.update(dt)
            self.state.draw(self.screen)
            pg.display.flip()
        pg.quit()

if __name__ == "__main__":
    App().run()
