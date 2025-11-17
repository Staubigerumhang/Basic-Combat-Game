import pygame
import os
from player import Player
from level_outline import Level_Outline

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_level = None
        self.player = None
        self.bosses = []
        self.is_paused = False
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # Загрузка звуков
        self.sounds = {}
        try:
            self.sounds['hit'] = pygame.mixer.Sound(os.path.join('assets', 'sounds', 'player_hit.wav'))
            self.sounds['background_music'] = os.path.join('assets', 'sounds', 'background_music.mp3')
        except (pygame.error, FileNotFoundError):
            print("Некоторые звуковые файлы не найдены")
            # Создаем заглушки для звуков
            self.sounds['hit'] = None
            
        # Шрифт для интерфейса
        self.font = pygame.font.Font(None, 36)
        
    def start_game(self):
        """Запуск игры, загрузка первого уровня"""
        try:
            pygame.mixer.music.load(self.sounds['background_music'])
            pygame.mixer.music.play(-1)  # Зацикливание музыки
            pygame.mixer.music.set_volume(0.5)
        except:
            print("Фоновая музыка не найдена")
            
        self.load_level(1)
        
    def load_level(self, level_number):
        """Загрузка уровня по номеру"""
        self.current_level = Level_Outline(level_number)
        self.player = Player(100, 300)  # Начальная позиция игрока
        self.bosses = self.current_level.spawn_bosses()
        print(f"Загружен уровень {level_number}")
        
    def update(self):

        if not self.is_paused:
            self.current_level.apply_gravity(self.player)
            
            self.player.update()

            for boss in self.bosses:
                if boss.is_alive:
                    boss.update(self.player)
                    
            self.check_collisions()
            
            self.check_victory()
            self.check_game_over()
            
    def check_collisions(self):
        if self.player.is_attacking and self.player.attack_rect:
            for boss in self.bosses:
                if (boss.is_alive and boss.rect.colliderect(self.player.attack_rect)):
                    boss.take_damage(self.player.damage)
                    if self.sounds['hit']:
                        self.sounds['hit'].play()
                    
        for boss in self.bosses:
            if (boss.is_attacking and boss.attack_rect and
                boss.attack_rect.colliderect(self.player.rect) and
                not self.player.is_blocking and not self.player.is_dodging):
                self.player.take_damage(boss.damage)
                if self.sounds['hit']:
                    self.sounds['hit'].play()
    
    def check_victory(self):
        if all(not boss.is_alive for boss in self.bosses):
            print("Победа! Уровень пройден!")
            
    def check_game_over(self):
        if not self.player.is_alive:
            print("Игра окончена!")
            
    def pause_game(self):
        self.is_paused = True
        pygame.mixer.music.pause()
        
    def resume_game(self):
        self.is_paused = False
        pygame.mixer.music.unpause()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_paused = not self.is_paused
                    if self.is_paused:
                        self.pause_game()
                    else:
                        self.resume_game()
                elif event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_LSHIFT:
                    self.player.dodge()
                elif event.key == pygame.K_e:
                    self.player.attack()
                elif event.key == pygame.K_r: 
                    self.load_level(1)
                    
        if not self.is_paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.player.move('left')
            elif keys[pygame.K_d]:
                self.player.move('right')
                
            if keys[pygame.K_s]:
                self.player.block()
            else:
                self.player.is_blocking = False
                
        return True
    
    def draw_ui(self):
        health_text = self.font.render(f"HP: {self.player.health}/{self.player.max_health}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 10))
        
        alive_bosses = sum(1 for boss in self.bosses if boss.is_alive)
        bosses_text = self.font.render(f"Боссы: {alive_bosses}/{len(self.bosses)}", True, (255, 255, 255))
        self.screen.blit(bosses_text, (10, 50))
        
        if self.is_paused:
            pause_text = self.font.render("ПАУЗА", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(400, 300))
            self.screen.blit(pause_text, text_rect)
