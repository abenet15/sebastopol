import pygame
import numpy as np
import sys
import world
import avatar

world_scale = 16
pygame.init()
screen = pygame.display.set_mode((800, 800))
pixel_off = pygame.image.load('image/b0.png').convert()
pixel_on = pygame.image.load('image/b1.png').convert()
bg = world.World(16, 1600 + 16, 880 + 16, pixel_off, pixel_on)
player_one = avatar.Avatar([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 4 * 16, 4 * 16, pixel_off, pixel_on)
player_two = avatar.Avatar([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 6 * 16, 10 * 16, pixel_off, pixel_on)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            player_one.move(event.key, controler=0)
            player_two.move(event.key, controler=1)

    if player_one.got_shot(player_two.bullets):
        running = False
        
    if player_two.got_shot(player_one.bullets):
        running = False
        
    bg.put_on(screen)
    player_one.put_on(screen)
    player_two.put_on(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
