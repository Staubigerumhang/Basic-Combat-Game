import pygame

class Creature:
    def __init__(self, x, y, screen):
        self.screen = screen
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        
        # Физика
        self.gravity = 0.5
        self.speed = 3
        self.on_ground = False
        
        # Анимации
        self.animations = {}
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.facing_right = True
        
        # Хитбокс
        self.rect = pygame.Rect(x, y, 50, 80)
        
        # Статус
        self.health = 100
        self.is_alive = True
    
    def apply_physics(self):
        if not self.on_ground:
            self.velocity.y += self.gravity
        
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        self.rect.x = self.position.x
        self.rect.y = self.position.y
    
    def handle_collisions(self, platforms):
        self.on_ground = False
        
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.y > 0:  # Падение вниз
                    self.rect.bottom = platform.top
                    self.position.y = self.rect.y
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0:  # Движение вверх
                    self.rect.top = platform.bottom
                    self.position.y = self.rect.y
                    self.velocity.y = 0
    
    def update_animation(self):
        self.animation_frame += self.animation_speed
        if self.animation_frame >= len(self.animations[self.current_animation]):
            self.animation_frame = 0
    
    def draw(self, camera_offset):
        frame_index = int(self.animation_frame) % len(self.animations[self.current_animation])
        current_frame = self.animations[self.current_animation][frame_index]
        
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        self.screen.blit(current_frame, (draw_x, draw_y))