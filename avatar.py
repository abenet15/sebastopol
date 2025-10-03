import pygame
import numpy as np
import sys

world_scale = 16

class Avatar:
    def __init__(self, image, x, y, pixel_off, pixel_on):
        self.clock = 0
        self.image = image
        self.pixel = [pixel_off, pixel_on]
        self.directions = [(-1,0),(1,0),(0,-1),(0,1)]
        self.direction = self.directions[0]
        self.x = x
        self.y = y
        self.bullets = []

        self.surface_a = pygame.Surface((16*3, 16*3))
        self.surface_d = pygame.Surface((16*3, 16*3))
        self.surface_w = pygame.Surface((16*3, 16*3))
        self.surface_s = pygame.Surface((16*3, 16*3))

        self.draw(self.surface_a, np.rot90(self.image, k=1))
        self.draw(self.surface_d, np.rot90(self.image, k=-1))
        self.draw(self.surface_w, self.image)
        self.draw(self.surface_s, np.rot90(np.rot90(self.image, k=1)))

        self.num = 0
        self.orentation = self.surface_w
        self.fire = -1

    def rotate(self,num):
        self.palet = [self.surface_a, self.surface_d, self.surface_w, self.surface_s]
        self.orentation = self.palet[num]
        self.direction = self.directions[num]
        self.num = num

    def shot(self):
        bullet = Bullet(self.x+16, self.y+16, self.direction, self.pixel[0], self.pixel[1])
        self.bullets.append(bullet)

    def got_shot(self, bullets):
        avatar_rect = pygame.Rect(self.x, self.y, 16*3, 16*3)
        for bullet in bullets:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 16, 16)
            if avatar_rect.colliderect(bullet_rect):
                return True
        return False
    
    def move(self, rig, controler = 0):
        if controler == 0:
            self.controler = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_p]
        if controler == 1:
            self.controler = [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_c]
        
        if rig == self.controler[0]:
            self.num = 0
            self.orentation = self.surface_a
            self.direction = self.directions[0]
            self.x -= 1 * world_scale
        elif rig == self.controler[1]:
            self.num = 1
            self.orentation = self.surface_d
            self.direction = self.directions[1]
            self.x += 1 * world_scale
        elif rig == self.controler[2]:
            self.num = 2
            self.orentation = self.surface_w
            self.direction = self.directions[2]
            self.y -= 1 * world_scale
        elif rig == self.controler[3]:
            self.num = 3
            self.orentation = self.surface_s
            self.direction = self.directions[3]
            self.y += 1 * world_scale
            
        if rig == self.controler[4]:
            self.fire *= -1
            bullet = Bullet(self.x+16, self.y+16, self.direction, self.pixel[0], self.pixel[1])
            self.bullets.append(bullet)
             
    def draw(self, surface, np_image):
        for y, row in enumerate(np_image):
                for x, pixel in enumerate(row):
                    if pixel == 1:
                        surface.blit(self.pixel[1], (x * world_scale, y * world_scale))
                    elif pixel == 0:
                        surface.blit(self.pixel[0], (x * world_scale, y * world_scale))
        
    def put_on(self, screen):
        for bullet in self.bullets:
            bullet.move()
            bullet.put_on(screen)      
        screen.blit(self.orentation, (self.x, self.y))
        
class Bullet:
    def __init__(self, x, y, direction,  pixel_off, pixel_on):
        self.surface = pygame.Surface((16, 16))
        self.x = x
        self.y = y
        self.direction = direction
        self.pixel = (pixel_off, pixel_on)
        self.draw()
        
    def move(self):
        self.x += self.direction[0]*16
        self.y += self.direction[1]*16
        
    def draw(self):
        self.surface.blit(self.pixel[1], (0, 0))

    def put_on(self, screen):
        screen.blit(self.surface, (self.x, self.y))
        
                

