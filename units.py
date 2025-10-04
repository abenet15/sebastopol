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
        self.shake_timer = 0
        self.shake_intensity = 0
        self.trail = []  # stores past positions
        self.max_trail = 5  # number of echoes to keep
        self.trail_duration = 500
        self.laser_sound = pygame.mixer.Sound("sounds/laser0.mp3")
        self.laser_sound.set_volume(0.5)  # optional: adjust loudness
        self.hit_sound = pygame.mixer.Sound("sounds/hit0.mp3")
        self.hit_sound.set_volume(0.1)  # optional: adjust loudness
        self.move_sound = pygame.mixer.Sound("sounds/swoosh0.mp3")
        self.move_sound.set_volume(0.2)  # optional: adjust loudness
        
    def get_shake_offset(self):
        if self.shake_timer > 0:
            return np.random.randint(-self.shake_intensity, self.shake_intensity + 1), \
                   np.random.randint(-self.shake_intensity, self.shake_intensity + 1)
        return 0, 0
    
    def trigger_shake(self, frames=20, intensity=800):
        self.shake_timer = frames
        self.shake_intensity = intensity

    def update_shake(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            
    def add_trail(self):
        now = pygame.time.get_ticks()
        self.trail.append((self.x, self.y, now))

    def update_trail(self):
        now = pygame.time.get_ticks()
        self.trail = [(x, y, t) for (x, y, t) in self.trail if now - t < self.trail_duration]

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
        self.trigger_shake()
        bullet = Bullet(self.x+16, self.y+16, self.direction, self.pixel)
        self.bullets.append(bullet)
        self.shake_timer = 5  # frames to shake
        self.shake_intensity = 2  # pixels to jitte
        self.laser_sound.play()

    def agot_shot(self, bullets):
        avatar_rect = pygame.Rect(self.x, self.y, 16*3, 16*3)
        for bullet in bullets:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 16, 16)
            if avatar_rect.colliderect(bullet_rect):
                self.hit_sound.play()
                return True
            return False
        
    def got_shot(self, bullets):
        avatar_rect = pygame.Rect(self.x, self.y, 16*3, 16*3)
        for bullet in bullets:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 16, 16)
            if avatar_rect.colliderect(bullet_rect):
                self.hit_sound.play()
                self.trigger_shake(frames=15, intensity=4)
                return bullet  # Return the bullet that hit
        return None

    
    def move(self, rig, controler=0):
        keys = [
            [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RSHIFT],
            [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_e]
        ][controler]
        
        self.add_trail()
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
            
        if rig in keys[:4]:
            self.move_sound.play()
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
        # Draw echo trail first
        now = pygame.time.get_ticks()
        for (tx, ty, t) in self.trail:
            age = now - t
            alpha = int(50 * (1 - age / self.trail_duration))
            ghost = self.orentation.copy()
            ghost.set_alpha(max(0, alpha))
            screen.blit(ghost, (tx, ty))

        # Apply shake offset if active
        offset_x = offset_y = 0
        if self.shake_timer > 0:
            offset_x = np.random.randint(-self.shake_intensity, self.shake_intensity + 1)
            offset_y = np.random.randint(-self.shake_intensity, self.shake_intensity + 1)
    
        # Draw tank with offset
        screen.blit(self.orentation, (self.x + offset_x, self.y + offset_y))

        # Draw bullets
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
    clock = pygame.time.Clock()
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
        player_one.update_trail()
        player_one.update_shake()  
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


