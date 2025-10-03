import pygame
import numpy as np
import sys

world_scale = 16

class TankUnit:
    def __init__(self, image, x, y, pixel_on):
        self.image = image
        self.pixel = pixel_on
        self.directions = [(-1,0),(1,0),(0,-1),(0,1)]
        self.direction = self.directions[0]
        self.x, self.y = (x,y)
        self.bullets = []
        self.orientations = {
            0: self.create_surface(np.rot90(self.image, k=1)),   # Left
            1: self.create_surface(np.rot90(self.image, k=-1)),  # Right
            2: self.create_surface(self.image),                  # Up
            3: self.create_surface(np.rot90(self.image, k=2))    # Down
        }
        self.orentation = self.orientations[2]
        self.num = 0
        self.fire = -1

    def create_surface(self, np_image):
        surface = pygame.Surface((16*3, 16*3), pygame.SRCALPHA)
        for y, row in enumerate(np_image):
            for x, pixel in enumerate(row):
                if pixel == 1:
                    surface.blit(self.pixel, (x * world_scale, y * world_scale))
        return surface

    def rotate(self,num):
        self.palet = [self.surface_a, self.surface_d, self.surface_w, self.surface_s]
        self.orentation = self.palet[num]
        self.direction = self.directions[num]
        self.num = num

    def shot(self):
        bullet = Bullet(self.x+16, self.y+16, self.direction, self.pixel)
        self.bullets.append(bullet)

    def got_shot(self, bullets):
        avatar_rect = pygame.Rect(self.x, self.y, 16*3, 16*3)
        for bullet in bullets:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 16, 16)
            if avatar_rect.colliderect(bullet_rect):
                return True
        return False
        
    def move(self, rig, controler=0):
        keys = [
            [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_p],
            [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_c]
        ][controler]

        if rig in keys[:4]:
            self.num = keys.index(rig)
            self.orentation = self.orientations[self.num]
            self.direction = self.directions[self.num]
            self.x += self.direction[0] * world_scale
            self.y += self.direction[1] * world_scale
        elif rig == keys[4]:
            self.fire *= -1
            self.shot()

    def draw(self, surface, np_image):
        for y, row in enumerate(np_image):
                for x, pixel in enumerate(row):
                    if pixel == 1:
                        surface.blit(self.pixel[1], (x * world_scale, y * world_scale))
                    elif pixel == 0:
                        surface.blit(self.pixel[0], (x * world_scale, y * world_scale))

    def put_on(self, screen):
        screen.blit(self.orentation, (self.x, self.y))
        self.bullets = [b for b in self.bullets if 0 <= b.x <= screen.get_width() and 0 <= b.y <= screen.get_height()]
        for bullet in self.bullets:
            bullet.move()
            bullet.put_on(screen)    
      
class Bullet:
    def __init__(self, x, y, direction, pixel_on):
        self.surface = pygame.Surface((16, 16))
        self.x = x
        self.y = y
        self.direction = direction
        self.pixel = pixel_on
        self.clock = 0
        self.speed = 1
        self.draw()
        
    def move(self):
        self.clock += 1
        if self.clock >= self.speed:
            self.x += self.direction[0] * world_scale
            self.y += self.direction[1] * world_scale
            self.clock = 0
            
    def draw(self):
        self.surface.blit(self.pixel, (0, 0))

    def put_on(self, screen):
        screen.blit(self.surface, (self.x, self.y))
        
if __name__ == '__main__':
    world_scale = 16
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    pixel_on = pygame.image.load('pixels/b1.png').convert()
    player_one = TankUnit([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 4 * 16, 4 * 16, pixel_on)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                player_one.move(event.key, controler=0)
                
        screen.fill((123, 137, 100))
        player_one.put_on(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


