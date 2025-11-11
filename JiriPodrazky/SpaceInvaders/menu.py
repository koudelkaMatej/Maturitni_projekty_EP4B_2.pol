import pygame
import sys
import subprocess

pygame.init()

# Okno
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Invaders - Menu")

# Barvy
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# Font
font = pygame.font.Font('freesansbold.ttf', 40)

# Tlačítka [text, x, y, width, height]
buttons = [
    ["Hrát", 300, 200, 200, 60],
    ["Nastavení", 300, 300, 200, 60],
    ["Konec hry", 300, 400, 200, 60],
]

def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
    label = font.render(text, True, WHITE)
    screen.blit(label, (x + (w - label.get_width()) // 2, y + 10))

def menu_loop():
    while True:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Detekce kliknutí na tlačítka
                for text, x, y, w, h in buttons:
                    if x <= mx <= x + w and y <= my <= y + h:
                        if text == "Hrát":
                            pygame.quit()
                            subprocess.run(["python", "main.py"])  # ⬅️ spustí hru
                            sys.exit()
                        elif text == "Nastavení":
                            print("Zatím žádná nastavení 🙂")
                            pygame.quit()
                            sys.exit()
                        elif text == "Konec hry":
                            pygame.quit()
                            sys.exit()

        # vykreslení tlačítek
        mx, my = pygame.mouse.get_pos()
        for text, x, y, w, h in buttons:
            color = RED if x <= mx <= x + w and y <= my <= y + h else GRAY
            draw_button(text, x, y, w, h, color)

        pygame.display.flip()

if __name__ == "__main__":
    menu_loop()
