import pygame
import numpy as np

world_scale = 16

class World:
    def __init__(self, width, height, pixel_off, pixel_on):
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.rect = self.surface.get_rect()
        self.pixel = (pixel_off, pixel_on)
        self.grid = []  # store pixel positions
        self.draw()

    def draw(self):
        for y in range(int(self.height / world_scale)):
            for x in range(int(self.width / world_scale)):
                pos = (x * world_scale, y * world_scale)
                self.grid.append(pos)
                self.surface.blit(self.pixel[0], pos)

    def turbulence(self, screen, time):
        for i, (x, y) in enumerate(self.grid):
            alpha = int(128 + 127 * np.sin((x + y + time) * 0.01))  # smooth shimmer
            pixel = self.pixel[1].copy()
            pixel.set_alpha(alpha)
            screen.blit(pixel, (x, y))

    def put_on(self, screen, offset=(0, 0)):
        screen.blit(self.surface, offset)
               
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((500,500))
    clock = pygame.time.Clock()
    pixel_on = pygame.image.load('pixels/b1.png').convert()
    pixel_off = pygame.image.load('pixels/diago 0.png').convert()
    bg = World(600, 600, pixel_off, pixel_on)
    run = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                run = True
        bg.put_on(screen)
        bg.turbulence(screen, pygame.time.get_ticks())
        pygame.display.flip()
        clock.tick(30)        
    pygame.quit()
    sys.exit()
