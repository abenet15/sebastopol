import pygame
import numpy as np
import sys
import world
import units

world_scale = 16

def draw_scene(surface, bg, player_one, player_two):
    bg.put_on(surface)
    player_one.put_on(surface)
    player_two.put_on(surface)

def draw_over(screen):
    screen.fill((123, 137, 100))
    f1 = pygame.font.Font("pixels/8-BIT WONDER.TTF", 64)
    over = f1.render("END GAME", True, (142, 148, 136))
    over_rect = over.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(over, over_rect)
    pygame.display.flip()


def menu_loop(screen):
    blink = True
    blink_timer = 0
    running = True
    f1 = pygame.font.Font("pixels/8-BIT WONDER.TTF", 64)
    f2 = pygame.font.Font("pixels/PressStart2P-Regular.TTF", 24)
    while running:
        screen.fill((123, 137, 100))

        image = pygame.image.load("pixels/sebastopol.png").convert_alpha()
        image = pygame.transform.scale(image, (1000/2, 600/2))
        image_rect = image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(image, image_rect)
        # Blinking "Press any key"
        if blink:
            prompt = f2.render("Press any key", True, (142, 148, 136))
            prompt_rect = prompt.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 180))
            screen.blit(prompt, prompt_rect)

        pygame.display.flip()
        pygame.time.delay(100)
        blink_timer += 1
        if blink_timer % 10 == 0:
            blink = not blink

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                return  # Exit menu and start game

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()

    pixel_off = pygame.image.load('pixels/b0.png').convert()
    po = pygame.image.load('pixels/b01.png').convert()
    pixel_on = pygame.image.load('pixels/b1.png').convert()

    bg = world.World(1600 + 16, 880 + 16, pixel_off, po)
    player_one = units.TankUnit([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 4 * 16, 4 * 16, pixel_on)
    player_two = units.TankUnit([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 6 * 16, 10 * 16, pixel_on)

    menu_loop(screen)
    bg_offset = [0, 0]
    bg_shake_timer = 0
    running = True
    while running:
        screen.fill((123, 137, 100))  # Background fill

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                player_one.move(event.key, controler=0)
                player_two.move(event.key, controler=1)
                
        if player_one.got_shot(player_two.bullets):
            bg_shake_timer = 15  # frames to shake
            player_one.trigger_shake(frames=15, intensity=4)
            #draw_over(screen)
            
        if player_two.got_shot(player_one.bullets):
            bg_shake_timer = 15  # frames to shake
            player_two.trigger_shake(frames=15, intensity=4)
            #draw_over(screen)

        hit_bullet = player_one.got_shot(player_two.bullets)
        if hit_bullet:
            player_two.bullets.remove(hit_bullet)
        hit_bullet = player_two.got_shot(player_one.bullets)
        if hit_bullet:
            player_one.bullets.remove(hit_bullet)

        if bg_shake_timer > 0:
            bg_shake_timer -= 1
            bg_offset[0] = np.random.randint(-8, 9)
            bg_offset[1] = np.random.randint(-8, 9)
        else:
            bg_offset = [0, 0]
    
        bg.put_on(screen, offset=bg_offset)
        bg.turbulence(screen, pygame.time.get_ticks())
        
        player_one.put_on(screen)
        player_one.update_trail()
        player_one.update_shake()

        player_two.put_on(screen)
        player_two.update_trail()
        player_two.update_shake()
        
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
