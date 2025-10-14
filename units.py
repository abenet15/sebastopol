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
    def __init__(self, x, y, direction, pixel_on, is_red_fire=False):
        super().__init__(x, y)
        self.direction = direction
        self.pixel = pixel_on
        self.clock = 0
        self.speed = BULLET_SPEED
        self.is_red_fire = is_red_fire  # Red fire bullets deal double damage
        self.damage = 2 if is_red_fire else 1
        self.resource_manager = ResourceManager.get_instance()
        self.create_surface()
        
    def create_surface(self):
        """Create the visual representation of the bullet."""
        if self.is_red_fire:
            # Use red bullet sprite for red fire power-up
            self.surface = self.resource_manager.get_image("sprites/bullet_red.png")
            self.surface = pygame.transform.scale(self.surface, (WORLD_SCALE, WORLD_SCALE))
        else:
            # Use regular bullet or fallback to pixel
            try:
                self.surface = self.resource_manager.get_image("sprites/bullet.png")
                self.surface = pygame.transform.scale(self.surface, (WORLD_SCALE, WORLD_SCALE))
            except:
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
        self.pixel = pixel_on
        self.directions = [(-1,0),(1,0),(0,-1),(0,1)]  # Left, Right, Up, Down
        self.direction = self.directions[0]
        self.bullets = []
        self.image = image  # Store original image
        self.direction_num = 2  # Default to up
        
        # Try to load tank sprite (will override pixel array if successful)
        try:
            resource_manager = ResourceManager.get_instance()
            tank_sprite = resource_manager.get_image("sprites/tank.png")
            if tank_sprite:
                # Ensure surface has per-pixel alpha and scale it
                tank_sprite = pygame.transform.scale(tank_sprite, (WORLD_SCALE*3, WORLD_SCALE*3)).convert_alpha()
                # Create rotated orientations using pygame transforms (keeps alpha)
                self.orientations = {
                    0: pygame.transform.rotate(tank_sprite, 90),   # Left
                    1: pygame.transform.rotate(tank_sprite, -90),  # Right
                    2: tank_sprite,                                # Up (original)
                    3: pygame.transform.rotate(tank_sprite, 180)   # Down
                }
                self.orientation = self.orientations[self.direction_num]
                self.surface = self.orientation
                print("Tank sprite loaded successfully (with alpha preserved)")
        except Exception as e:
            print(f"Using fallback pixel array: {e}")
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
        self.is_moving = False
        self.last_key_pressed = None
        
        # Continuous movement for speed boost
        self.is_moving = False
        self.last_key_pressed = None
        
        # Load sounds using ResourceManager
        self.resource_manager = ResourceManager.get_instance()
        self.laser_sound = self.resource_manager.get_sound("sounds/laser0.mp3", LASER_VOLUME)
        self.hit_sound = self.resource_manager.get_sound("sounds/hit0.mp3", HIT_VOLUME)
        self.move_sound = self.resource_manager.get_sound("sounds/swoosh0.mp3", MOVE_VOLUME)
        
        
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
        
        # Check if red fire power-up is active
        is_red_fire = self.has_rapid_fire
        
        # Create bullet with appropriate type
        bullet = Bullet(self.x+WORLD_SCALE, self.y+WORLD_SCALE, self.direction, self.pixel, is_red_fire)
        self.bullets.append(bullet)
        self.laser_sound.play()
        
        # Add rapid fire effect if power-up is active
        if self.has_rapid_fire:
            # Add slight spread to rapid fire bullets
            offset = 5
            bullet_left = Bullet(self.x+WORLD_SCALE-offset, self.y+WORLD_SCALE-offset, self.direction, self.pixel, is_red_fire)
            bullet_right = Bullet(self.x+WORLD_SCALE+offset, self.y+WORLD_SCALE+offset, self.direction, self.pixel, is_red_fire)
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

    def move(self, key, controler=0, key_up=False, other_tank=None):
        """Handle movement based on key input."""
        # Define control keys for each player
        keys = [
            [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RSHIFT],
            [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_e]
        ][controler]
        
        # Handle key release for continuous movement
        if key_up:
            if key in keys[:4] and key == self.last_key_pressed:
                self.is_moving = False
                self.last_key_pressed = None
            return
            
        self.add_trail()
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
            
        # Movement keys
        if key in keys[:4]:
            self.move_sound.play()
            self.direction_num = keys.index(key)
            self.orientation = self.orientations[self.direction_num]
            self.direction = self.directions[self.direction_num]
            
            # Set continuous movement if speed boost is active
            if self.has_speed_boost:
                self.is_moving = True
                self.last_key_pressed = key
            
            # Calculate new position
            move_distance = WORLD_SCALE * (2 if self.has_speed_boost else 1)
            new_x = self.x + self.direction[0] * move_distance
            new_y = self.y + self.direction[1] * move_distance
            
            # Create temporary rect for collision detection
            temp_rect = pygame.Rect(new_x, new_y, WORLD_SCALE*3, WORLD_SCALE*3)
            
            # Check for collision with other tank
            can_move = True
            if other_tank and temp_rect.colliderect(other_tank.rect):
                can_move = False
                
            # Apply movement if no collision
            if can_move:
                self.x = new_x
                self.y = new_y
                self.update_rect()
            
        # Fire key
        elif key == keys[4]:
            self.fire_cooldown *= -1
            self.shot()

    def update(self, other_tank=None):
        """Update tank state including power-ups and bullets."""
        # Update power-up timers
        current_time = pygame.time.get_ticks()
        
        # Check if any power-ups have expired
        shield_expired = self.has_shield and current_time > self.shield_timer
        speed_expired = self.has_speed_boost and current_time > self.speed_boost_timer
        fire_expired = self.has_rapid_fire and current_time > self.rapid_fire_timer
        
        # Reset power-up states
        if shield_expired:
            self.has_shield = False
            
        if speed_expired:
            self.has_speed_boost = False
            self.is_moving = False
            
        if fire_expired:
            self.has_rapid_fire = False
            
        # Reset tank sprite if all power-ups expired
        if shield_expired or speed_expired or fire_expired:
            if not (self.has_shield or self.has_speed_boost or self.has_rapid_fire):
                # Reset to default tank sprite
                try:
                    self.update_tank_sprite("sprites/tank.png")
                except:
                    # If sprite not found, revert to original orientation
                    self.surface = self.orientations[self.direction_num]
                    self.update_rect()
            
        # Handle continuous movement if speed boost is active
        if self.is_moving and self.has_speed_boost:
            move_distance = WORLD_SCALE * 2  # Double speed with boost
            # Check for collision with other tank before moving
            new_x = self.x + self.direction[0] * move_distance
            new_y = self.y + self.direction[1] * move_distance
            temp_rect = pygame.Rect(new_x, new_y, WORLD_SCALE*3, WORLD_SCALE*3)
            
            can_move = True
            if other_tank and temp_rect.colliderect(other_tank.rect):
                can_move = False
                
            if can_move:
                self.x = new_x
                self.y = new_y
                self.update_rect()
                self.add_trail()
            
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
            # Add pulsing effect based on time remaining
            current_time = pygame.time.get_ticks()
            time_left = self.shield_timer - current_time
            shield_alpha = 100
            if time_left < 1000:  # Last second, make it blink
                if time_left % 200 < 100:  # Blink every 0.2 seconds
                    shield_alpha = 180
            shield_color = (0, 100, 255, shield_alpha)  # Semi-transparent blue
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
        # Change tank sprite to speed boost version
        try:
            self.update_tank_sprite("sprites/tank_speed_boost.png")
        except:
            pass
        
    def activate_shield(self, duration):
        """Activate shield power-up."""
        self.has_shield = True
        self.shield_timer = pygame.time.get_ticks() + duration
        # Change tank sprite to shield version
        try:
            self.update_tank_sprite("sprites/tank_activate_shield.png")
        except:
            pass
        
    def rapid_fire(self, duration):
        """Activate rapid fire power-up."""
        self.has_rapid_fire = True
        self.rapid_fire_timer = pygame.time.get_ticks() + duration
        # Change tank sprite to red fire version
        try:
            self.update_tank_sprite("sprites/tank_red_fire.png")
        except:
            pass
        # Change tank sprite to red fire version
        try:
            self.update_tank_sprite("sprites/tank_red_fire.png")
        except:
            pass
            
    def update_tank_sprite(self, sprite_path):
        """Update the tank sprite based on power-up (preserving alpha)."""
        try:
            tank_sprite = self.resource_manager.get_image(sprite_path)
            if tank_sprite:
                tank_sprite = pygame.transform.scale(tank_sprite, (WORLD_SCALE*3, WORLD_SCALE*3)).convert_alpha()
                self.orientations = {
                    0: pygame.transform.rotate(tank_sprite, 90),   # Left
                    1: pygame.transform.rotate(tank_sprite, -90),  # Right
                    2: tank_sprite,                                # Up
                    3: pygame.transform.rotate(tank_sprite, 180)   # Down
                }
                self.orientation = self.orientations[self.direction_num]
                self.surface = self.orientation
                self.update_rect()
                print(f"Tank sprite updated to: {sprite_path} (alpha preserved)")
        except Exception as e:
            print(f"Error updating tank sprite: {e}")

if __name__ == '__main__':
    pass


