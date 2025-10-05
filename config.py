"""
Configuration settings for the Sebastopol game.
Contains constants and settings used throughout the game.
"""

# Display settings
WORLD_SCALE = 16
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Game settings
FPS = 30
BACKGROUND_COLOR = (123, 137, 100)

# Tank settings
TANK_TRAIL_MAX = 5
TANK_TRAIL_DURATION = 500
TANK_SHAKE_FRAMES = 15
TANK_SHAKE_INTENSITY = 4

# Sound settings
LASER_VOLUME = 0.5
HIT_VOLUME = 0.1
MOVE_VOLUME = 0.2

# Bullet settings
BULLET_SPEED = 1

# Power-up settings
POWERUP_DURATION = 10000  # 10 seconds
POWERUP_SPAWN_RATE = 0.005  # 0.5% chance per frame