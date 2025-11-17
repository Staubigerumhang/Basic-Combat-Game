import pygame
import sys
from game_manager import GameManager

def main():
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Boss Fighter Game")
    
    game_manager = GameManager(screen)
    game_manager.start_game()
    
    running = True
    while running:
        running = game_manager.handle_events()
        
        game_manager.update()
        screen.blit(game_manager.current_level.background, (0, 0))
        game_manager.current_level.draw_platforms(screen)
        
        player_image = game_manager.player.get_current_image()
        if player_image:
            if game_manager.player.current_direction == 'left':
                player_image = pygame.transform.flip(player_image, True, False)
            screen.blit(player_image, (game_manager.player.x, game_manager.player.y))

            if game_manager.player.is_attacking and game_manager.player.attack_rect:
                pygame.draw.rect(screen, (255, 0, 0), game_manager.player.attack_rect, 2)
            
        for boss in game_manager.bosses:
            if boss.is_alive:
                boss_image = boss.get_current_image()
                if boss_image:
                    screen.blit(boss_image, (boss.x, boss.y))
                    
                    if boss.is_attacking and boss.attack_rect:
                        pygame.draw.rect(screen, (255, 165, 0), boss.attack_rect, 2)
        
        game_manager.draw_ui()
        pygame.display.flip()
        game_manager.clock.tick(game_manager.FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
