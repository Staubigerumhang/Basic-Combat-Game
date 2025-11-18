import pygame
import os

class Level:
    def __init__(self, screen, assets_path):
        self.screen = screen
        self.assets_path = assets_path
        self.platforms = []
        
        self.load_background()
        self.generate_level()
    
    def load_background(self):
        """Загружает фоновое изображение"""
        background_path = os.path.join(self.assets_path, "backgrounds", "level1.jpg")
        
        try:
            if os.path.exists(background_path):
                self.background = pygame.image.load(background_path).convert()
                self.background = pygame.transform.scale(self.background, 
                                                       self.screen.get_size())
            else:
                self.create_gradient_background()
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")
            self.create_gradient_background()
    
    def create_gradient_background(self):
        """Создает градиентный фон-заглушку"""
        self.background = pygame.Surface(self.screen.get_size())
        for y in range(self.screen.get_height()):
            # Градиент от синего к светлому
            color = (100, 150, max(50, 255 - y // 4))
            pygame.draw.line(self.background, color, (0, y), (self.screen.get_width(), y))
    
    def generate_level(self):
        """Генерирует уровень с платформами"""
        screen_width, screen_height = self.screen.get_size()
        
        # Основные платформы
        level_data = [
            # Земля
            (0, screen_height - 100, screen_width * 3, 100),
            # Платформы (x, y, width, height)
            (300, 400, 200, 20),
            (600, 300, 150, 20),
            (900, 400, 200, 20),
            (1200, 350, 100, 20),
            (1500, 450, 300, 20)
        ]
        
        for x, y, width, height in level_data:
            self.platforms.append(pygame.Rect(x, y, width, height))
    
    def draw(self, camera_offset):
        """Отрисовывает уровень"""
        # Фон
        self.screen.blit(self.background, (0, 0))
        
        # Платформы
        for platform in self.platforms:
            draw_rect = platform.move(-camera_offset[0], -camera_offset[1])
            pygame.draw.rect(self.screen, (139, 69, 19), draw_rect)  # Коричневый
            pygame.draw.rect(self.screen, (101, 67, 33), draw_rect, 2)  # Контур