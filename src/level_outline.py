import pygame
import os
from boss import Boss

class Level_Outline:
    def __init__(self, level_number):
        self.level_number = level_number
        self.gravity = 0.8
        self.ground_level = 500  # Уровень "земли"
        
        try:
            background_path = os.path.join('backgrounds', f'level{level_number}.png')
            self.background = pygame.image.load(background_path)
            self.background = pygame.transform.scale(self.background, (800, 600))
        except (pygame.error, FileNotFoundError):
            self.background = pygame.Surface((800, 600))
            self.background.fill((100, 150, 200))  
            
        self.terrain_data = self.load_terrain_data()
        self.boss_zones = [(500, 300), (800, 200)]  
        
    def load_terrain_data(self):
        return {
            'platforms': [
                (0, 550, 800, 50),  
                (100, 400, 200, 20), 
                (500, 350, 150, 20),  
            ]
        }
    
    def load_environment(self):
        platforms = []
        for platform_data in self.terrain_data['platforms']:
            platform = pygame.Rect(platform_data)
            platforms.append(platform)
        return platforms
    
    def spawn_bosses(self):
        bosses = []
        for i, zone in enumerate(self.boss_zones):
            boss = Boss(zone[0], zone[1], boss_type=f"boss_{i+1}")
            bosses.append(boss)
        return bosses
    
    def apply_gravity(self, creature):
        if not creature.on_ground:
            creature.velocity_y += self.gravity
            creature.y += creature.velocity_y
            
            if creature.y >= self.ground_level - creature.rect.height:
                creature.y = self.ground_level - creature.rect.height
                creature.velocity_y = 0
                creature.on_ground = True
                if creature.current_state == 'jump':
                    creature.current_state = 'idle'
        else:
            creature.velocity_y = 0
            
    def draw_platforms(self, screen):
        for platform in self.load_environment():
            pygame.draw.rect(screen, (100, 100, 100), platform)
