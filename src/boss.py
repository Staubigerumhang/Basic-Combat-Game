import pygame
from creature import Creature

class Boss(Creature):
    def __init__(self, x, y, boss_type="default"):
        super().__init__(x, y, health=500, damage=30, speed=3)
        self.boss_type = boss_type
        self.phase = 1
        self.attack_pattern = 0
        self.reward = "special_weapon"
        self.attack_cooldown = 0
        self.move_timer = 0
        self.move_direction = 1  
  
        self.create_basic_animations()
        
    def create_basic_animations(self):
        idle_frames = []
        for i in range(2):
            surface = pygame.Surface((80, 100), pygame.SRCALPHA)
            color = (200, 0, 0) if i == 0 else (150, 0, 0)  
            pygame.draw.rect(surface, color, (0, 0, 80, 100))
            pygame.draw.rect(surface, (100, 0, 0), (10, 20, 60, 40)) 
            idle_frames.append(surface)
            
        attack_frames = []
        for i in range(2):
            surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            color = (255, 0, 0) if i == 0 else (200, 0, 0)
            pygame.draw.rect(surface, color, (0, 0, 100, 100))
            pygame.draw.rect(surface, (150, 0, 0), (15, 20, 70, 40))
            attack_frames.append(surface)
            
        self.animations = {
            'idle': idle_frames,
            'attack': attack_frames,
            'death': [pygame.Surface((80, 100), pygame.SRCALPHA)]
        }
        self.animations['death'][0].fill((100, 100, 100, 128))
        
    def update(self, player):
        super().update()
        
        if not self.is_alive:
            return
            
        self.attack_cooldown -= 1
        self.move_timer -= 1
        
        if self.move_timer <= 0:
            self.move_direction *= -1  
            self.move_timer = 60  
            
        if self.move_direction == 1:
            self.move('right')
        else:
            self.move('left')
            
        health_percentage = self.health / self.max_health
        if health_percentage < 0.3 and self.phase == 2:
            self.change_phase(3)
        elif health_percentage < 0.6 and self.phase == 1:
            self.change_phase(2)
            
        if (self.attack_cooldown <= 0 and 
            abs(self.x - player.x) < 200):  
            self.special_move()
            self.attack_cooldown = 90 
            
    def change_phase(self, new_phase):
        self.phase = new_phase
        self.speed += 1
        self.damage += 10
        print(f"Босс перешел в фазу {new_phase}! Стал быстрее и сильнее!")
        
    def special_move(self):
        self.attack()
        
    def apply_reward(self, player):
        player.hotbar.append(self.reward)
        print(f"Получена награда: {self.reward}")
        
    def die(self):
        super().die()
        print(f"Босс повержен! Награда: {self.reward}")
