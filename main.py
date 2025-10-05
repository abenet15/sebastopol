"""
Main module for the Sebastopol game.
Contains the game loop and main game logic.
"""
import pygame
import numpy as np
import sys
import world
import units
from utils import ResourceManager
from config import *

class GameState:
    """
    Class to manage different game states (menu, playing, game over).
    """
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2

def draw_scene(surface, bg, player_one, player_two):
    """Draw all game elements on the screen."""
    bg.put_on(surface)
    player_one.put_on(surface)
    player_two.put_on(surface)

def draw_game_over(screen, winner=None):
    """Draw the game over screen."""
    screen.fill(BACKGROUND_COLOR)
    f1 = pygame.font.Font("pixels/8-BIT WONDER.TTF", 64)
    over = f1.render("GAME OVER", True, (142, 148, 136))
    over_rect = over.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(over, over_rect)
    
    if winner:
        f2 = pygame.font.Font("pixels/PressStart2P-Regular.TTF", 24)
        winner_text = f2.render(f"PLAYER {winner} WINS!", True, (142, 148, 136))
        winner_rect = winner_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
        screen.blit(winner_text, winner_rect)
    
    f3 = pygame.font.Font("pixels/PressStart2P-Regular.TTF", 16)
    restart = f3.render("PRESS SPACE TO RESTART", True, (142, 148, 136))
    restart_rect = restart.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 120))
    screen.blit(restart, restart_rect)
    
    pygame.display.flip()

def menu_loop(screen):
    """Display and handle the menu screen."""
    blink = True
    blink_timer = 0
    running = True
    f1 = pygame.font.Font("pixels/8-BIT WONDER.TTF", 64)
    f2 = pygame.font.Font("pixels/PressStart2P-Regular.TTF", 24)
    f3 = pygame.font.Font("pixels/PressStart2P-Regular.TTF", 16)
    
    while running:
        screen.fill(BACKGROUND_COLOR)

        # Load and display the title image
        resource_manager = ResourceManager.get_instance()
        image = resource_manager.get_image("pixels/sebastopol.png")
        image = pygame.transform.scale(image, (1000/2, 600/2))
        image_rect = image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
        screen.blit(image, image_rect)
        
        # Display game controls
        controls1 = f3.render("PLAYER 1: ARROWS + RIGHT SHIFT", True, (142, 148, 136))
        controls1_rect = controls1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
        screen.blit(controls1, controls1_rect)
        
        controls2 = f3.render("PLAYER 2: WASD + E", True, (142, 148, 136))
        controls2_rect = controls2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 130))
        screen.blit(controls2, controls2_rect)
        
        # Blinking "Press any key"
        if blink:
            prompt = f2.render("Press any key to start", True, (142, 148, 136))
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
    """Main game function."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sebastopol")
    clock = pygame.time.Clock()

    # Load resources using ResourceManager
    resource_manager = ResourceManager.get_instance()
    pixel_off = resource_manager.get_image('pixels/b0.png')
    po = resource_manager.get_image('pixels/b01.png')
    pixel_on = resource_manager.get_image('pixels/b1.png')

    # Game state
    game_state = GameState.MENU
    winner = None
    player_lives = [3, 3]  # Lives for player 1 and player 2
    
    # Create game objects
    bg = world.World(1600 + WORLD_SCALE, 880 + WORLD_SCALE, pixel_off, po)
    player_one = units.TankUnit([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 4 * WORLD_SCALE, 4 * WORLD_SCALE, pixel_on)
    player_two = units.TankUnit([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 6 * WORLD_SCALE, 10 * WORLD_SCALE, pixel_on)

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                # Menu state
                if game_state == GameState.MENU:
                    game_state = GameState.PLAYING
                    
                # Playing state
                elif game_state == GameState.PLAYING:
                    player_one.move(event.key, controler=0)
                    player_two.move(event.key, controler=1)
                    
                # Game over state
                elif game_state == GameState.GAME_OVER and event.key == pygame.K_SPACE:
                    # Reset game
                    game_state = GameState.PLAYING
                    player_lives = [3, 3]
                    player_one = units.TankUnit([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 4 * WORLD_SCALE, 4 * WORLD_SCALE, pixel_on)
                    player_two = units.TankUnit([[0, 1, 0], [1, 1, 1], [1, 0, 1]], 6 * WORLD_SCALE, 10 * WORLD_SCALE, pixel_on)
        
        # Menu state
        if game_state == GameState.MENU:
            menu_loop(screen)
            game_state = GameState.PLAYING
            
        # Playing state
        elif game_state == GameState.PLAYING:
            screen.fill(BACKGROUND_COLOR)
            
            # Update game objects
            player_one.update()
            player_two.update()
            bg.update([player_one, player_two])
            
            # Check for hits
            hit_bullet = player_one.got_shot(player_two.bullets)
            if hit_bullet:
                player_two.bullets.remove(hit_bullet)
                player_lives[0] -= 1
                if player_lives[0] <= 0:
                    game_state = GameState.GAME_OVER
                    winner = 2
                
            hit_bullet = player_two.got_shot(player_one.bullets)
            if hit_bullet:
                player_one.bullets.remove(hit_bullet)
                player_lives[1] -= 1
                if player_lives[1] <= 0:
                    game_state = GameState.GAME_OVER
                    winner = 1
            
            # Draw everything
            bg.put_on(screen)
            bg.turbulence(screen, pygame.time.get_ticks())
            player_one.put_on(screen)
            player_two.put_on(screen)
            
            # Draw lives
            f = pygame.font.Font("pixels/PressStart2P-Regular.TTF", 16)
            lives1 = f.render(f"P1: {'♥' * player_lives[0]}", True, (0, 0, 0))
            lives2 = f.render(f"P2: {'♥' * player_lives[1]}", True, (0, 0, 0))
            screen.blit(lives1, (20, 20))
            screen.blit(lives2, (SCREEN_WIDTH - 120, 20))
            
        # Game over state
        elif game_state == GameState.GAME_OVER:
            draw_game_over(screen, winner)
            
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
