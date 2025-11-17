import pygame
from creature import Creature

class Player(Creature):
    def __init__(self, x, y):
        super().__init__(x, y, health=200, damage=20, speed=7)
        self.jump_force = -15
        self.hotbar = ['sword', 'potion']
        self.is_blocking = False
        self.is_dodging = False
        self.dodge_timer = 0
        self.dodge_duration = 20 
        self.dodge_cooldown = 0
        self.max_dodge_cooldown = 60
        
        self.load_animations()
        
    def load_animations(self):
        self.animations = {
            'idle': self.load_frames('idle', 2),
            'walk': self.load_frames('walk', 2),
            'jump': self.load_frames('jump', 1),
            'attack': self.load_frames('attack', 2),
            'block': self.load_frames('block', 1),
            'dodge': self.load_frames('dodge', 1),
            'death': self.load_frames('death', 1)
        }
        
    def jump(self):
        if self.on_ground and not self.is_attacking and not self.is_dodging:
            self.velocity_y = self.jump_force
            self.on_ground = False
            self.current_state = 'jump'
            
    def block(self):
        if self.on_ground and not self.is_attacking and not self.is_dodging:
            self.is_blocking = True
            self.current_state = 'block'
            
    def dodge(self):
        if (not self.is_dodging and self.on_ground and 
            not self.is_attacking and self.dodge_cooldown <= 0):
            self.is_dodging = True
            self.dodge_timer = self.dodge_duration
            self.current_state = 'dodge'
            self.dodge_cooldown = self.max_dodge_cooldown
            
    def update(self):
        super().update()
        
        if self.is_dodging:
            self.dodge_timer -= 1

            if self.current_direction == 'left':
                self.x -= 8
            else:
                self.x += 8
                
            if self.dodge_timer <= 0:
                self.is_dodging = False
                self.current_state = 'idle'
                
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= 1
            
        if (self.on_ground and not self.is_attacking and 
            not self.is_dodging and self.current_state == 'walk'):
            self.current_state = 'idle'
            
        if not self.on_ground:
            self.is_blocking = False
