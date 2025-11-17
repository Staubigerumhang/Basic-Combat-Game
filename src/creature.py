import pygame
import os

class Creature:
    def __init__(self, x, y, health=100,damage=10,speed=5):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.on_ground = False
        self.is_attacking = False
        self.attack_rect = None
        self.current_direction = 'right'

        self.animations = {}
        self.current_state = 'idle'
        self.current_frame = 0
        self.animation_speed = 0.2

    @property
    def rect(self):
        return pygame.Rect(self.x,self.y,50,80)
        
    def load_animations(self):
        pass

    def load_frames(self, path, frame_count):
        frames = []
        for i in range(frame_count):
            try:
                filename = f"{path}_{i}.png"
                full_path = os.path.join('assets','player',filename)
                
                frame = pygame.image.load(full_path)
                frame = frame.convert_alpha()
                frames.append(frame)

            except(pygame.error, FileNotFoundError):
                print(f"Файл не найден: {full_path}")
                frame = pygame.Surface((50,80),pygame.SRCALPHA)
                frame.fill((255,0,0,128))
                frames.append(frame)
            return frames
        
    def update_animations(self):
        if not self.is_alive:
            return
            
        self.current_frame += self.animation_speed
        if self.current_state in self.animations:
            frame_count = len(self.animations[self.current_state])
            if self.current_frame >= frame_count:
                self.current_frame = 0
             
                if self.current_state == 'attack':
                    self.is_attacking = False
                    self.current_state = 'idle'
            
                elif self.current_state == 'death':
                    self.current_frame = frame_count - 1
                
    def get_current_image(self):
        if (self.current_state in self.animations and len(self.animations[self.current_state > 0])):
            frame_index = int(self.current_frame) % len(self.animations[self.current_state])
            return self.animations[self.current_state][frame_index]
        
        surface = pygame.Surface((50,80), pygame.SRCALPHA)
        surface.fill(255,255,0,128)
        return surface
    
    def move(self, direction):
        if not self.is_alive or self.is_attacking:
            return
        
        if direction == 'left':
            self.x -= self.speed
            self.current_direction = 'left'

        if self.current_state != 'attack' and self.on_ground:
                self.current_state = 'walk'
        elif direction == 'right':
            self.x += self.speed
            self.current_direction = 'right'
            if self.current_state != 'attack' and self.on_ground:
                self.current_state = 'walk'
                
                
        self.x = max(0, min(self.x, 750)) 
                
    def take_damage(self, damage):
        if not self.is_alive:
            return
            
        self.health -= damage
        print(f"Получено урона: {damage}. Осталось здоровья: {self.health}")
        
        if self.health <= 0:
            self.die()
            
    def attack(self):
        if not self.is_alive or self.is_attacking:
            return
            
        self.is_attacking = True
        self.current_state = 'attack'
        self.current_frame = 0
    
        attack_width = 80
        if self.current_direction == 'left':
            attack_x = self.x - 30
        else:
            attack_x = self.x + 50
            
        self.attack_rect = pygame.Rect(attack_x, self.y, attack_width, 50)
        
    def die(self):
        self.is_alive = False
        self.current_state = 'death'
        self.current_frame = 0
        print("Существо погибло!")
        
    def update(self):
        if self.is_alive:
            self.update_animation()
