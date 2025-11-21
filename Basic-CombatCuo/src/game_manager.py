import pygame
import os
from player import Player

class GameManager:
    def __init__(self, screen, assets_path):
        self.screen = screen
        self.assets_path = assets_path
        self.debug_mode = False
        
        self.sounds = {}
        self.load_sounds()
        
        # Создаем двух одинаковых игроков
        self.players = [
            # Игрок 1 - WASD + QE
            Player(300, 300, screen, assets_path, self, 
                  controls={
                      'left': pygame.K_a,
                      'right': pygame.K_d,
                      'jump': pygame.K_w,
                      'attack': pygame.K_e,
                      'heavy_attack': pygame.K_q,
                      'block': pygame.K_s
                  },
                  player_id=1, facing_right=True),
            
            # Игрок 2 - Стрелки + KL  
            Player(700, 300, screen, assets_path, self,
                  controls={
                      'left': pygame.K_LEFT,
                      'right': pygame.K_RIGHT, 
                      'jump': pygame.K_UP,
                      'attack': pygame.K_l,
                      'heavy_attack': pygame.K_k,
                      'block': pygame.K_DOWN
                  },
                  player_id=2, facing_right=False)
        ]
        
        self.camera_offset = [0, 0]
        self.camera_smoothness = 0.05
        
        # Арена
        self.platforms = self.create_arena()
    
    def create_arena(self):
        """Создает арену для битвы"""
        screen_width, screen_height = self.screen.get_size()
        return [
            # Основная платформа
            pygame.Rect(0, screen_height - 50, screen_width, 50),
            # Небольшие платформы
            pygame.Rect(200, 400, 150, 25),
            pygame.Rect(500, 350, 150, 25),
            pygame.Rect(700, 400, 150, 25)
        ]
    
    def load_sounds(self):
        sound_config = {
            'background': ('background_music.mp3', None),
            'attack': ('attack.wav', 0.7),
            'heavy_attack': ('heavy_attack.wav', 0.8),
            'block': ('block.wav', 0.5),
            'jump': ('jump.wav', 0.6),
            'hit': ('hit.wav', 0.8),
        }
        
        for sound_name, (filename, volume) in sound_config.items():
            sound_path = os.path.join(self.assets_path, 'sounds', filename)
            self.load_single_sound(sound_name, sound_path, volume)
        
        self.play_background_music()
    
    def load_single_sound(self, sound_name, path, volume):
        try:
            if os.path.exists(path):
                if sound_name == 'background':
                    self.sounds[sound_name] = path
                else:
                    sound = pygame.mixer.Sound(path)
                    if volume:
                        sound.set_volume(volume)
                    self.sounds[sound_name] = sound
        except Exception as e:
            print(f"Ошибка загрузки {sound_name}: {e}")
            self.sounds[sound_name] = None
    
    def play_background_music(self):
        if self.sounds.get('background'):
            try:
                pygame.mixer.music.load(self.sounds['background'])
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Ошибка музыки: {e}")
    
    def play_sound(self, sound_name):
        sound = self.sounds.get(sound_name)
        if sound and hasattr(sound, 'play'):
            try:
                sound.play()
            except Exception as e:
                print(f"Ошибка звука {sound_name}: {e}")
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Переключение режима отладки по клавише I
            if event.key == pygame.K_i:
                self.debug_mode = not self.debug_mode
                print(f"Режим отладки: {'ВКЛ' if self.debug_mode else 'ВЫКЛ'}")
        
        for player in self.players:
            player.handle_event(event)
    
    def update(self):
        # Обновляем игроков
        for player in self.players:
            player.update(self.platforms, self.players)
        
        # Проверяем столкновения атак
        self.check_attacks()
        
        self.update_camera()
    
    def check_attacks(self):
        """Проверяет столкновения атак между игроками"""
        for i, attacker in enumerate(self.players):
            if not attacker.actions['attacking']:
                continue
                
            for j, defender in enumerate(self.players):
                if i == j:
                    continue
                    
                if attacker.attack_hitbox.colliderect(defender.rect):
                    self.handle_attack_hit(attacker, defender)
    
    def handle_attack_hit(self, attacker, defender):
        """Обрабатывает попадание атаки"""
        # Если защитник блокирует и смотрит в правильную сторону
        if (defender.actions['blocking'] and 
            defender.is_facing_attacker(attacker)):
            
            # Обычный блок
            defender.take_damage(attacker.attack_damage * 0.2)
            self.play_sound('block')
        else:
            # Обычное попадание
            defender.take_damage(attacker.attack_damage)
            defender.knockback(attacker.facing_right, 8 if attacker.actions['heavy_attacking'] else 5)
            self.play_sound('hit')
            
            if attacker.actions['heavy_attacking']:
                self.play_sound('heavy_attack')
            else:
                self.play_sound('attack')
        
        # Сбрасываем атаку после попадания
        attacker.actions['attacking'] = False
        attacker.actions['heavy_attacking'] = False
    
    def update_camera(self):
        """Камера следует за серединой между игроками"""
        if len(self.players) >= 2:
            center_x = (self.players[0].rect.centerx + self.players[1].rect.centerx) // 2
            center_y = (self.players[0].rect.centery + self.players[1].rect.centery) // 2
            
            target_x = center_x - self.screen.get_width() // 2
            target_y = center_y - self.screen.get_height() // 2
            
            self.camera_offset[0] += (target_x - self.camera_offset[0]) * self.camera_smoothness
            self.camera_offset[1] += (target_y - self.camera_offset[1]) * self.camera_smoothness
    
    def draw(self):
        # Очищаем экран
        self.screen.fill((50, 50, 80))
        
        # Рисуем платформы
        for platform in self.platforms:
            draw_rect = platform.move(-self.camera_offset[0], -self.camera_offset[1])
            pygame.draw.rect(self.screen, (100, 70, 40), draw_rect)
            pygame.draw.rect(self.screen, (80, 50, 30), draw_rect, 2)
        
        # Рисуем игроков
        for player in self.players:
            player.draw(self.camera_offset)
        
        # Рисуем хитбоксы в режиме отладки
        if self.debug_mode:
            self.draw_debug_hitboxes()
        
        # Рисуем HUD
        self.draw_hud()
    
    def draw_debug_hitboxes(self):
        """Рисует полупрозрачные хитбоксы для отладки"""
        for player in self.players:
            # Хитбокс персонажа (зеленый)
            char_rect = player.rect.move(-self.camera_offset[0], -self.camera_offset[1])
            debug_surface = pygame.Surface((char_rect.width, char_rect.height), pygame.SRCALPHA)
            debug_surface.fill((0, 255, 0, 128))
            self.screen.blit(debug_surface, char_rect)
            
            # Хитбокс атаки (красный)
            if player.actions['attacking']:
                attack_rect = player.attack_hitbox.move(-self.camera_offset[0], -self.camera_offset[1])
                attack_surface = pygame.Surface((attack_rect.width, attack_rect.height), pygame.SRCALPHA)
                attack_surface.fill((255, 0, 0, 128))
                self.screen.blit(attack_surface, attack_rect)
    
    def draw_hud(self):
        """Рисует интерфейс"""
        font = pygame.font.Font(None, 36)
        
        # Здоровье игрока 1
        health_text1 = f"P1: {self.players[0].health}/100"
        text_surf1 = font.render(health_text1, True, (255, 255, 255))
        self.screen.blit(text_surf1, (20, 20))
        
        # Полоска здоровья игрока 1
        health_width1 = (self.players[0].health / 100) * 200
        pygame.draw.rect(self.screen, (255, 0, 0), (20, 60, 200, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (20, 60, health_width1, 20))
        
        # Здоровье игрока 2  
        health_text2 = f"P2: {self.players[1].health}/100"
        text_surf2 = font.render(health_text2, True, (255, 255, 255))
        self.screen.blit(text_surf2, (780, 20))
        
        # Полоска здоровья игрока 2
        health_width2 = (self.players[1].health / 100) * 200
        pygame.draw.rect(self.screen, (255, 0, 0), (780, 60, 200, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (980 - health_width2, 60, health_width2, 20))
        
        # Индикатор режима отладки
        if self.debug_mode:
            debug_text = "DEBUG MODE: HITBOXES VISIBLE (Press I to hide)"
            debug_surf = font.render(debug_text, True, (255, 255, 0))
            self.screen.blit(debug_surf, (250, 550))