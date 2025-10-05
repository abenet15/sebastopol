"""
World module for the Sebastopol game.
Contains the World class for managing the game environment.
"""
import pygame
import numpy as np
import random
from utils import GameObject, PowerUp
from config import *

class World(GameObject):
    """
    World class for managing the game environment, background, and obstacles.
    """
    def __init__(self, width, height, pixel_off, pixel_on):
        super().__init__(0, 0)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.rect = self.surface.get_rect()
        self.pixel = (pixel_off, pixel_on)
        self.grid = []  # store pixel positions
        self.power_ups = []  # store active power-ups
        self.last_power_up_time = 0
        self.power_up_cooldown = 5000  # 5 seconds between power-up spawns
        self.draw()

    def draw(self):
        """Draw the initial world grid."""
        for y in range(int(self.height / WORLD_SCALE)):
            for x in range(int(self.width / WORLD_SCALE)):
                pos = (x * WORLD_SCALE, y * WORLD_SCALE)
                self.grid.append(pos)
                self.surface.blit(self.pixel[0], pos)

    def turbulence(self, screen, time):
        """Create a shimmering effect on the background."""
        for i, (x, y) in enumerate(self.grid):
            alpha = int(128 + 127 * np.sin((x + y + time) * 0.01))  # smooth shimmer
            pixel = self.pixel[1].copy()
            pixel.set_alpha(alpha)
            screen.blit(pixel, (x, y))

    def spawn_power_up(self):
        """Randomly spawn a power-up in the world."""
        current_time = pygame.time.get_ticks()
        
        # Check if it's time to spawn a power-up
        if (current_time - self.last_power_up_time > self.power_up_cooldown and 
            random.random() < POWERUP_SPAWN_RATE):
            
            # Choose a random position
            x = random.randint(1, int(self.width / WORLD_SCALE) - 2) * WORLD_SCALE
            y = random.randint(1, int(self.height / WORLD_SCALE) - 2) * WORLD_SCALE
            
            # Create a new power-up
            power_up = PowerUp(x, y)
            self.power_ups.append(power_up)
            self.last_power_up_time = current_time

    def update(self, tanks):
        """Update the world state including power-ups."""
        # Spawn new power-ups
        self.spawn_power_up()
        
        # Check for power-up collisions with tanks
        for tank in tanks:
            for power_up in self.power_ups[:]:
                if power_up.active and power_up.collides_with(tank):
                    power_up.apply(tank)
                    self.power_ups.remove(power_up)

    def put_on(self, screen, offset=(0, 0)):
        """Draw the world and its elements on the screen."""
        # Draw the base world
        screen.blit(self.surface, offset)
        
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.put_on(screen)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    clock = pygame.time.Clock()
    pixel_on = pygame.image.load('pixels/b1.png').convert()
    pixel_off = pygame.image.load('pixels/diago 0.png').convert()
    bg = World(600, 600, pixel_off, pixel_on)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        screen.fill(BACKGROUND_COLOR)
        bg.update([])  # No tanks in this test
        bg.put_on(screen)
        bg.turbulence(screen, pygame.time.get_ticks())
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
