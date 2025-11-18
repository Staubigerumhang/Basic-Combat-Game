import pygame
import os
from player import Player
from level_outline import Level

class GameManager:
    def __init__(self, screen, assets_path):
        self.screen = screen
        self.assets_path = assets_path
        
        self.sounds = {}
        self.load_sounds()
        
        self.level = Level(screen, assets_path)
        self.player = Player(100, 300, screen, assets_path, self)
        
        self.camera_offset = [0, 0]
        self.camera_smoothness = 0.05  # Плавность камеры
        
    def load_sounds(self):
        """Загружает звуковые эффекты"""
        sound_config = {
            'background': ('background_music.mp3', None),  # (файл, громкость)
            'attack': ('attack.wav', 0.7),
            'block': ('block.wav', 0.5),
            'jump': ('jump.wav', 0.6),
            'dodge': ('dodge.wav', 0.4),
            'hit': ('hit.wav', 0.8)
        }
        
        for sound_name, (filename, volume) in sound_config.items():
            sound_path = os.path.join(self.assets_path, 'sounds', filename)
            self.load_single_sound(sound_name, sound_path, volume)
        
        self.play_background_music()
    
    def load_single_sound(self, sound_name, path, volume):
        """Загружает один звуковой файл"""
        try:
            if os.path.exists(path):
                if sound_name == 'background':
                    self.sounds[sound_name] = path
                else:
                    sound = pygame.mixer.Sound(path)
                    if volume:
                        sound.set_volume(volume)
                    self.sounds[sound_name] = sound
                print(f"✓ Звук загружен: {sound_name}")
            else:
                print(f"✗ Файл не найден: {path}")
                self.sounds[sound_name] = None
        except Exception as e:
            print(f"✗ Ошибка загрузки {sound_name}: {e}")
            self.sounds[sound_name] = None
    
    def play_background_music(self):
        """Запускает фоновую музыку"""
        if self.sounds.get('background'):
            try:
                pygame.mixer.music.load(self.sounds['background'])
                pygame.mixer.music.set_volume(0.3)  # Тише фоновую музыку
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Ошибка музыки: {e}")
    
    def play_sound(self, sound_name):
        """Воспроизводит звуковой эффект"""
        sound = self.sounds.get(sound_name)
        if sound and hasattr(sound, 'play'):
            try:
                sound.play()
            except Exception as e:
                print(f"Ошибка звука {sound_name}: {e}")
    
    def handle_event(self, event):
        """Обрабатывает события"""
        self.player.handle_event(event)
    
    def update(self):
        """Обновляет состояние игры"""
        self.player.update(self.level.platforms)
        self.update_camera()
    
    def update_camera(self):
        """Обновляет позицию камеры"""
        target_x = self.player.rect.centerx - self.screen.get_width() // 2
        target_y = self.player.rect.centery - self.screen.get_height() // 2
        
        # Плавное движение камеры
        self.camera_offset[0] += (target_x - self.camera_offset[0]) * self.camera_smoothness
        self.camera_offset[1] += (target_y - self.camera_offset[1]) * self.camera_smoothness
    
    def draw(self):
        """Отрисовывает игровые объекты"""
        self.level.draw(self.camera_offset)
        self.player.draw(self.camera_offset)