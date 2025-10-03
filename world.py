import pygame

world_scale = 16

class World:
    def __init__(self, cell_size, width, height, pixel_off, pixel_on):
        self.surface = pygame.Surface((width, height))
        self.rect = self.surface.get_rect()
        self.pixel = (pixel_off, pixel_on)
        self.draw()
        
    def grid(self,screen, thickness):
        for x in range(0, 800, 16):
            pygame.draw.line(screen, (240, 240, 240), (x, 0), (x, self.height),thickness)
        for y in range(0, 800, 16):
            pygame.draw.line(screen, (240, 240, 240), (0, y), (self.width, y),thickness)

    def draw(self):
        for y in range(3000):
            for x in range(3000):
                self.surface.blit(self.pixel[0], (x * world_scale, y * world_scale))
                
    def put_on(self, screen):
        screen.blit(self.surface, (0,0))
        
