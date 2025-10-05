"""
Utility classes and functions for the Sebastopol game.
"""
import pygame
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
            self._images[path] = pygame.image.load(path).convert_alpha()
        return self._images[path]

class GameObject:
    """
    Base class for all game objects (tanks, bullets, power-ups).
    Provides common functionality for position, rendering, and collision.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.surface = None
        self.rect = None
        self.update_rect()
    
    def update_rect(self):
        """Update the collision rectangle based on current position and surface."""
        if self.surface:
            self.rect = pygame.Rect(self.x, self.y, self.surface.get_width(), self.surface.get_height())
        else:
            self.rect = pygame.Rect(self.x, self.y, WORLD_SCALE, WORLD_SCALE)
    
    def update(self):
        """Update the game object state. Override in subclasses."""
        pass
    
    def put_on(self, screen):
        """Draw the game object on the screen."""
        if self.surface:
            screen.blit(self.surface, (self.x, self.y))
            
    def collides_with(self, other):
        """Check if this object collides with another object."""
        self.update_rect()
        other.update_rect()
        return self.rect.colliderect(other.rect)

class PowerUp(GameObject):
    """
    Power-up class for special abilities and bonuses.
    """
    TYPES = ["speed", "shield", "rapid_fire"]
    
    def __init__(self, x, y, power_type=None):
        super().__init__(x, y)
        self.resource_manager = ResourceManager.get_instance()
        
        # If no type specified, choose random
        if power_type is None:
            import random
            power_type = random.choice(self.TYPES)
            
        self.type = power_type
        self.active = True
        self.create_surface()
        
    def create_surface(self):
        """Create the visual representation of the power-up."""
        self.surface = pygame.Surface((WORLD_SCALE, WORLD_SCALE), pygame.SRCALPHA)
        
        # Different colors for different power-up types
        color = {
            "speed": (0, 255, 0),      # Green for speed
            "shield": (0, 0, 255),     # Blue for shield
            "rapid_fire": (255, 0, 0)  # Red for rapid fire
        }.get(self.type, (255, 255, 0))  # Yellow default
        
        pygame.draw.rect(self.surface, color, (0, 0, WORLD_SCALE, WORLD_SCALE))
        pygame.draw.rect(self.surface, (255, 255, 255), (2, 2, WORLD_SCALE-4, WORLD_SCALE-4), 2)
        
    def apply(self, tank):
        """Apply the power-up effect to a tank."""
        if self.type == "speed":
            tank.speed_boost(POWERUP_DURATION)
        elif self.type == "shield":
            tank.activate_shield(POWERUP_DURATION)
        elif self.type == "rapid_fire":
            tank.rapid_fire(POWERUP_DURATION)
        self.active = False