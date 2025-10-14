"""
Utility classes and functions for the Sebastopol game.
"""
import pygame
import random
import math
from config import *

class ResourceManager:
    """
    Singleton class to manage game resources like images and sounds.
    Prevents loading the same resources multiple times.
    """
    _instance = None
    _sounds = {}
    _images = {}
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ResourceManager()
        return cls._instance
    
    def __init__(self):
        # Print available sprite files for debugging
        self._print_available_sprites()
    
    def _print_available_sprites(self):
        """Print available sprite files in the sprites directory."""
        try:
            import os
            if os.path.exists("sprites"):
                print("Available sprite files:")
                for file in os.listdir("sprites"):
                    print(f"  - sprites/{file}")
            else:
                print("Sprites directory not found!")
        except Exception as e:
            print(f"Error checking sprites: {e}")
    
    def get_sound(self, path, volume=1.0):
        """Load a sound file or return from cache if already loaded."""
        if path not in self._sounds:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self._sounds[path] = sound
        return self._sounds[path]
    
    def get_image(self, path):
        """Load an image file or return from cache if already loaded."""
        if path not in self._images:
            try:
                # Print for debugging
                print(f"Attempting to load image: {path}")
                self._images[path] = pygame.image.load(path).convert_alpha()
                print(f"Successfully loaded image: {path}")
            except pygame.error as e:
                print(f"Could not load image: {path} - Error: {e}")
                return None
        return self._images[path]

class GameObject(pygame.sprite.Sprite):
    """
    Base class for all game objects (tanks, bullets, power-ups).
    Provides common functionality for position, rendering, and collision.
    Inherits from pygame.sprite.Sprite for sprite-based collision detection.
    """
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.surface = None
        self.image = None  # Sprite image
        self.rect = None
        self.mask = None  # For pixel-perfect collision
        self.update_rect()
    
    def update_rect(self):
        """Update the collision rectangle based on current position and surface."""
        if self.surface:
            # Ensure rect matches the actual surface size
            self.rect = pygame.Rect(self.x, self.y, self.surface.get_width(), self.surface.get_height())
            # Update sprite image from surface
            self.image = self.surface
        else:
            # Default size if no surface
            self.rect = pygame.Rect(self.x, self.y, WORLD_SCALE, WORLD_SCALE)
            # Create a default image if none exists
            if self.image is None:
                self.image = pygame.Surface((WORLD_SCALE, WORLD_SCALE), pygame.SRCALPHA)
        
        # Update mask for pixel-perfect collision
        if isinstance(self.image, pygame.Surface):
            self.mask = pygame.mask.from_surface(self.image)
            # Print for debugging
            print(f"Updated rect for object at ({self.x}, {self.y}): {self.rect.width}x{self.rect.height}")
    
    def update(self):
        """Update the game object state. Override in subclasses."""
        pass
    
    def put_on(self, screen):
        """Draw the game object on the screen."""
        if self.surface:
            screen.blit(self.surface, (self.x, self.y))
            
    def collides_with(self, other):
        """Check if this object collides with another object using sprite collision."""
        self.update_rect()
        other.update_rect()
        
        # First do a quick rect collision check (faster)
        if not self.rect.colliderect(other.rect):
            return False
            
        # Then do a more precise mask collision check
        offset_x = other.rect.x - self.rect.x
        offset_y = other.rect.y - self.rect.y
        
        # Use mask collision for pixel-perfect detection
        return self.mask.overlap(other.mask, (offset_x, offset_y)) is not None

class PowerUp(GameObject):
    """
    Power-up class for special abilities and bonuses.
    """
    TYPES = ["speed", "shield", "rapid_fire"]
    SPRITE_PATHS = {
        "speed": "sprites/blue.png",
        "shield": "sprites/yellow.png",
        "rapid_fire": "sprites/red.png"
    }
    
    def __init__(self, x, y, power_type=None):
        super().__init__(x, y)
        self.resource_manager = ResourceManager.get_instance()
        
        # If no type specified, choose random
        if power_type is None:
            power_type = random.choice(self.TYPES)
            
        self.type = power_type
        self.active = True
        self.create_surface()
        # Ensure rect is properly sized
        self.rect = pygame.Rect(self.x, self.y, WORLD_SCALE, WORLD_SCALE)
        # Print for debugging
        print(f"Created PowerUp {self.type} at ({self.x}, {self.y}) with rect {self.rect}")
        
    def create_surface(self):
        """Create the visual representation of the power-up using sprites."""
        # Load sprite image from sprites folder
        sprite_path = self.SPRITE_PATHS.get(self.type)
        if sprite_path:
            self.surface = self.resource_manager.get_image(sprite_path)
            # Scale the image to match the world scale
            self.surface = pygame.transform.scale(self.surface, (WORLD_SCALE*3, WORLD_SCALE*3))
        else:
            # Fallback to colored rectangle if sprite not found
            self.surface = pygame.Surface((WORLD_SCALE*2, WORLD_SCALE*2), pygame.SRCALPHA)

            # Different colors for different power-up types
            color = {
                "speed": (0, 255, 0),      # Green for speed
                "shield": (0, 0, 255),     # Blue for shield
                "rapid_fire": (255, 0, 0)  # Red for rapid fire
            }.get(self.type, (255, 255, 0))  # Yellow default
            
        # Update the image and mask for sprite collision
        self.image = self.surface
        self.mask = pygame.mask.from_surface(self.image)
        
    def apply(self, tank):
        """Apply the power-up effect to a tank."""
        if self.type == "speed":
            tank.speed_boost(POWERUP_DURATION)
        elif self.type == "shield":
            tank.activate_shield(POWERUP_DURATION)
        elif self.type == "rapid_fire":
            tank.rapid_fire(POWERUP_DURATION)
        self.active = False