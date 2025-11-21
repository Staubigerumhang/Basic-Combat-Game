import pygame
import sys
import os

class Game:
    def __init__(self):
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 600
        self.FPS = 60
        
        self.init_pygame()
        self.setup_paths()
        self.create_game_objects()
    
    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("2D Fighter - Sword vs Spear")
        self.clock = pygame.time.Clock()
    
    def setup_paths(self):
        project_path = r"C:\Users\student\Desktop\Basic-CombatCuo"
        if os.path.exists(project_path):
            os.chdir(project_path)
        self.assets_path = os.path.join(os.getcwd(), 'assets')
    
    def create_game_objects(self):
        from game_manager import GameManager
        self.game_manager = GameManager(self.screen, self.assets_path)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            self.game_manager.handle_event(event)
        return True
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.game_manager.update()
            self.game_manager.draw()
            pygame.display.flip()
            self.clock.tick(self.FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()