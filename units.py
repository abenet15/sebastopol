"""
Units module for the Sebastopol game.
Contains classes for tanks, bullets, and related game objects.
"""
import pygame
import numpy as np
import sys
from utils import GameObject, ResourceManager
from config import *

class Bullet(GameObject):
    """Bullet class for projectiles fired by tanks."""
    def __init__(self, x, y, direction, pixel_on):
        super().__init__(x, y)
        self.direction = direction
        self.pixel = pixel_on
        self.clock = 0
        self.speed = BULLET_SPEED
        self.create_surface()
        
    def create_surface(self):
        """Create the visual representation of the bullet."""
        self.surface = pygame.Surface((WORLD_SCALE, WORLD_SCALE), pygame.SRCALPHA)
        self.surface.blit(self.pixel, (0, 0))
        self.update_rect()

    def move(self):
        """Move the bullet in its current direction."""
        self.clock += 1
        if self.clock >= self.speed:
            self.x += self.direction[0] * WORLD_SCALE
            self.y += self.direction[1] * WORLD_SCALE
            self.clock = 0
            self.update_rect()

class TankUnit(GameObject):
    """Tank unit class for player-controlled vehicles."""
    def __init__(self, image, x, y, pixel_on):
        super().__init__(x, y)
        self.image = image
        self.pixel = pixel_on
        self.directions = [(-1,0),(1,0),(0,-1),(0,1)]  # Left, Right, Up, Down
        self.direction = self.directions[0]
        self.bullets = []
        
        # Create orientations (rotated versions of the tank)
        self.orientations = {
            0: self.create_surface(np.rot90(self.image, k=1)),   # Left
            1: self.create_surface(np.rot90(self.image, k=-1)),  # Right
            2: self.create_surface(self.image),                  # Up
            3: self.create_surface(np.rot90(self.image, k=2))    # Down
        }
        self.orientation = self.orientations[2]  # Default orientation (up)
        self.direction_num = 2
        
        # Visual effects
        self.fire_cooldown = -1
        self.shake_timer = 0
        self.shake_intensity = 0
        self.trail = []  # stores past positions
        self.max_trail = TANK_TRAIL_MAX
        self.trail_duration = TANK_TRAIL_DURATION
        
        # Power-up states
        self.has_shield = False
        self.shield_timer = 0
        self.has_speed_boost = False
        self.speed_boost_timer = 0
        self.has_rapid_fire = False
        self.rapid_fire_timer = 0
        
        # Load sounds using ResourceManager
        self.resource_manager = ResourceManager.get_instance()
        self.laser_sound = self.resource_manager.get_sound("sounds/laser0.mp3", LASER_VOLUME)
        self.hit_sound = self.resource_manager.get_sound("sounds/hit0.mp3", HIT_VOLUME)
        self.move_sound = self.resource_manager.get_sound("sounds/swoosh0.mp3", MOVE_VOLUME)
        
    def create_surface(self, np_image):
        """Create a surface from a numpy array representation of the tank."""
        surface = pygame.Surface((WORLD_SCALE*3, WORLD_SCALE*3), pygame.SRCALPHA)
        for y, row in enumerate(np_image):
            for x, pixel in enumerate(row):
                if pixel == 1:
                    surface.blit(self.pixel, (x * WORLD_SCALE, y * WORLD_SCALE))
        return surface

    def get_shake_offset(self):
        """Get random offset for shake effect."""
        if self.shake_timer > 0:
            return np.random.randint(-self.shake_intensity, self.shake_intensity + 1), \
                   np.random.randint(-self.shake_intensity, self.shake_intensity + 1)
        return 0, 0
    
    def trigger_shake(self, frames=TANK_SHAKE_FRAMES, intensity=TANK_SHAKE_INTENSITY):
        """Trigger screen shake effect."""
        self.shake_timer = frames
        self.shake_intensity = intensity

    def update_shake(self):
        """Update shake effect timer."""
        if self.shake_timer > 0:
            self.shake_timer -= 1
            
    def add_trail(self):
        """Add current position to the trail."""
        now = pygame.time.get_ticks()
        self.trail.append((self.x, self.y, now))

    def update_trail(self):
        """Update trail positions and remove expired ones."""
        now = pygame.time.get_ticks()
        self.trail = [(x, y, t) for (x, y, t) in self.trail if now - t < self.trail_duration]

    def shot(self):
        """Fire a bullet in the current direction."""
        self.trigger_shake()
        bullet = Bullet(self.x+WORLD_SCALE, self.y+WORLD_SCALE, self.direction, self.pixel)
        self.bullets.append(bullet)
        self.laser_sound.play()
        
        # Add rapid fire effect if power-up is active
        if self.has_rapid_fire:
            # Add slight spread to rapid fire bullets
            offset = 5
            bullet_left = Bullet(self.x+WORLD_SCALE-offset, self.y+WORLD_SCALE-offset, self.direction, self.pixel)
            bullet_right = Bullet(self.x+WORLD_SCALE+offset, self.y+WORLD_SCALE+offset, self.direction, self.pixel)
            self.bullets.extend([bullet_left, bullet_right])

    def got_shot(self, bullets):
        """Check if tank was hit by any bullets and handle the hit."""
        if self.has_shield:
            return None  # Shield blocks all bullets
            
        avatar_rect = pygame.Rect(self.x, self.y, WORLD_SCALE*3, WORLD_SCALE*3)
        for bullet in bullets:
            if avatar_rect.colliderect(bullet.rect):
                self.hit_sound.play()
                self.trigger_shake(frames=TANK_SHAKE_FRAMES, intensity=TANK_SHAKE_INTENSITY)
                return bullet  # Return the bullet that hit
        return None

    def move(self, key, controler=0):
        """Handle movement based on key input."""
        # Define control keys for each player
        keys = [
            [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RSHIFT],
            [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_e]
        ][controler]
        
        self.add_trail()
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
            
        # Movement keys
        if key in keys[:4]:
            self.move_sound.play()
            self.direction_num = keys.index(key)
            self.orientation = self.orientations[self.direction_num]
            self.direction = self.directions[self.direction_num]
            
            # Apply speed boost if active
            move_distance = WORLD_SCALE * (2 if self.has_speed_boost else 1)
            self.x += self.direction[0] * move_distance
            self.y += self.direction[1] * move_distance
            self.update_rect()
            
        # Fire key
        elif key == keys[4]:
            self.fire_cooldown *= -1
            self.shot()

    def update(self):
        """Update tank state including power-ups and bullets."""
        # Update power-up timers
        current_time = pygame.time.get_ticks()
        
        if self.has_shield and current_time > self.shield_timer:
            self.has_shield = False
            
        if self.has_speed_boost and current_time > self.speed_boost_timer:
            self.has_speed_boost = False
            
        if self.has_rapid_fire and current_time > self.rapid_fire_timer:
            self.has_rapid_fire = False
            
        # Update bullets
        for bullet in self.bullets:
            bullet.move()
            
        # Update visual effects
        self.update_trail()
        self.update_shake()
        
    def put_on(self, screen):
        """Draw the tank and its effects on the screen."""
        # Draw echo trail first
        now = pygame.time.get_ticks()
        for (tx, ty, t) in self.trail:
            age = now - t
            alpha = int(50 * (1 - age / self.trail_duration))
            ghost = self.orientation.copy()
            ghost.set_alpha(max(0, alpha))
            screen.blit(ghost, (tx, ty))

        # Apply shake offset if active
        offset_x, offset_y = self.get_shake_offset()
    
        # Draw shield effect if active
        if self.has_shield:
            shield_surface = pygame.Surface((WORLD_SCALE*3 + 10, WORLD_SCALE*3 + 10), pygame.SRCALPHA)
            shield_color = (0, 100, 255, 100)  # Semi-transparent blue
            pygame.draw.ellipse(shield_surface, shield_color, shield_surface.get_rect())
            screen.blit(shield_surface, (self.x - 5 + offset_x, self.y - 5 + offset_y))
    
        # Draw tank with offset
        screen.blit(self.orientation, (self.x + offset_x, self.y + offset_y))

        # Draw bullets
        for bullet in self.bullets[:]:
            # Remove bullets that go off-screen
            if (bullet.x < 0 or bullet.x > screen.get_width() or 
                bullet.y < 0 or bullet.y > screen.get_height()):
                self.bullets.remove(bullet)
            else:
                bullet.put_on(screen)
                
    def speed_boost(self, duration):
        """Activate speed boost power-up."""
        self.has_speed_boost = True
        self.speed_boost_timer = pygame.time.get_ticks() + duration
        
    def activate_shield(self, duration):
        """Activate shield power-up."""
        self.has_shield = True
        self.shield_timer = pygame.time.get_ticks() + duration
        
    def rapid_fire(self, duration):
        """Activate rapid fire power-up."""
        self.has_rapid_fire = True
        self.rapid_fire_timer = pygame.time.get_ticks() + duration

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    clock = pygame.time.Clock()
    pixel_on = pygame.image.load('pixels/b1.png').convert()
    player_one = TankUnit([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 4 * WORLD_SCALE, 4 * WORLD_SCALE, pixel_on)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                player_one.move(event.key, controler=0)
             
        screen.fill(BACKGROUND_COLOR)
        player_one.update()
        player_one.put_on(screen)
        pygame.display.flip()
        clock.tick(FPS)


