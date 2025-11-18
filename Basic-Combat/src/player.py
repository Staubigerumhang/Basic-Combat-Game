import pygame
import os

class Player:
    def __init__(self, x, y, screen, assets_path, game_manager=None):
        # Основные ссылки
        self.screen = screen
        self.assets_path = assets_path
        self.game_manager = game_manager
        
        # Физика и движение
        self.setup_physics(x, y)
        
        # Анимации
        self.setup_animations()
        
        # Состояния и таймеры
        self.setup_state()
    
    def setup_physics(self, x, y):
        """Настройка физических параметров"""
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        
        self.gravity = 0.5
        self.jump_power = -12
        self.speed = 5
        self.ground_check_margin = 5
        
        self.rect = pygame.Rect(x, y, 50, 80)
        self.on_ground = True
        self.is_jumping = False
    
    def setup_animations(self):
        """Настройка анимаций"""
        self.animations = {}
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.facing_right = True
        
        self.load_animations()
    
    def setup_state(self):
        """Настройка состояний и таймеров"""
        self.actions = {
            'attacking': False,
            'blocking': False, 
            'dodging': False,
            'dead': False
        }
        
        self.cooldowns = {
            'attack': 0,
            'attack_animation': 0,
            'dodge': 0,
            'dodge_timer': 0
        }
        
        self.sound_flags = {
            'attack': False,
            'block': False,
            'jump': False
        }
    
    def load_animations(self):
        """Загружает анимации из папок"""
        animation_folders = {
            "idle": "player/idle",
            "walk": "player/walk", 
            "attack": "player/attack",
            "block": "player/block",
            "dodge": "player/dodge",
            "death": "player/death",
            "jump": "player/jump"
        }
        
        for state, folder in animation_folders.items():
            self.animations[state] = self.load_animation_frames(folder)
    
    def load_animation_frames(self, folder):
        """Загружает кадры анимации из папки"""
        frames = []
        full_path = os.path.join(self.assets_path, folder)
        
        if os.path.exists(full_path):
            try:
                image_files = sorted([
                    f for f in os.listdir(full_path) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                ])
                
                for filename in image_files:
                    image_path = os.path.join(full_path, filename)
                    image = pygame.image.load(image_path).convert_alpha()
                    image = pygame.transform.scale(image, (60, 90))
                    frames.append(image)
                    
            except Exception as e:
                print(f"Ошибка загрузки {folder}: {e}")
        
        # Создаем заглушку если папка пуста
        if not frames:
            frames = self.create_placeholder_animation(folder)
            
        return frames
    
    def create_placeholder_animation(self, state):
        """Создает анимацию-заглушку"""
        color_map = {
            "idle": (0, 255, 0), "walk": (255, 255, 0), "attack": (255, 0, 0),
            "block": (0, 0, 255), "dodge": (255, 0, 255), "death": (128, 128, 128),
            "jump": (0, 255, 255)
        }
        
        frames_count = 4 if state in ["walk", "attack", "dodge", "jump"] else 1
        frames = []
        
        for i in range(frames_count):
            surf = pygame.Surface((60, 90), pygame.SRCALPHA)
            color = color_map.get(state, (255, 255, 255))
            anim_color = [min(255, c + i * 20) for c in color]
            
            pygame.draw.rect(surf, anim_color, (0, 0, 60, 90))
            pygame.draw.rect(surf, (0, 0, 0), (0, 0, 60, 90), 2)
            
            frames.append(surf)
        
        return frames

    # Остальные методы остаются похожими, но более структурированными
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.jump()
            elif event.key == pygame.K_d and self.cooldowns['dodge'] <= 0 and not self.actions['dodging']:
                self.dodge()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.actions['dodging']:
            # Движение
            if keys[pygame.K_LEFT]:
                self.velocity.x = -self.speed
                self.facing_right = False
            elif keys[pygame.K_RIGHT]:
                self.velocity.x = self.speed
                self.facing_right = True
            else:
                self.velocity.x = 0
            
            # Действия
            if keys[pygame.K_a] and not self.actions['attacking'] and self.cooldowns['attack'] <= 0:
                self.start_attack()
            
            if keys[pygame.K_s] and not self.actions['blocking'] and not self.actions['attacking']:
                self.start_block()
            elif not keys[pygame.K_s]:
                self.stop_block()

    def start_attack(self):
        """Начинает атаку"""
        self.actions['attacking'] = True
        self.current_animation = "attack"
        self.animation_frame = 0
        self.cooldowns['attack'] = 20
        self.cooldowns['attack_animation'] = 15
        self.sound_flags['attack'] = False
        
        if self.game_manager:
            self.game_manager.play_sound('attack')

    def start_block(self):
        """Начинает блокировку"""
        if not self.actions['blocking']:
            self.actions['blocking'] = True
            self.current_animation = "block"
            if self.animations["block"]:
                self.animation_frame = len(self.animations["block"]) - 1
            self.velocity.x *= 0.3
            
            if self.game_manager and not self.sound_flags['block']:
                self.game_manager.play_sound('block')
                self.sound_flags['block'] = True

    def stop_block(self):
        """Заканчивает блокировку"""
        if self.actions['blocking']:
            self.actions['blocking'] = False
            self.sound_flags['block'] = False

    def jump(self):
        """Выполняет прыжок"""
        if self.on_ground and not self.actions['attacking'] and not self.actions['dodging']:
            self.velocity.y = self.jump_power
            self.is_jumping = True
            self.on_ground = False
            
            if self.game_manager and not self.sound_flags['jump']:
                self.game_manager.play_sound('jump')
                self.sound_flags['jump'] = True

    def dodge(self):
        """Выполняет уворот"""
        if not any([self.actions['attacking'], self.actions['blocking'], self.actions['dodging']]):
            self.actions['dodging'] = True
            self.current_animation = "dodge"
            self.animation_frame = 0
            self.cooldowns['dodge'] = 60
            self.cooldowns['dodge_timer'] = 20
            
            # Импульс в направлении взгляда
            direction = 15 if self.facing_right else -15
            self.velocity.x = direction
            
            if self.game_manager:
                self.game_manager.play_sound('dodge')

    def update(self, platforms):
        """Основное обновление состояния игрока"""
        self.handle_input()
        self.apply_physics()
        self.handle_collisions(platforms)
        self.update_cooldowns()
        self.update_animation_state()
        self.update_animation()
        
        # Сбрасываем флаги звуков при изменении состояния
        if self.on_ground:
            self.sound_flags['jump'] = False
    
    def update_cooldowns(self):
        """Обновляет все таймеры и кулдауны"""
        # Уменьшаем все кулдауны
        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] -= 1
        
        # Завершаем уворот по таймеру
        if self.actions['dodging'] and self.cooldowns['dodge_timer'] <= 0:
            self.actions['dodging'] = False
            self.velocity.x *= 0.5
        
        # Завершаем атаку если клавиша отпущена
        keys = pygame.key.get_pressed()
        if (self.actions['attacking'] and 
            not keys[pygame.K_a] and 
            self.cooldowns['attack_animation'] <= 0):
            self.actions['attacking'] = False
            self.animation_frame = 0

    def apply_physics(self):
        """Применяет физику к игроку"""
        # Гравитация
        if not self.on_ground:
            self.velocity.y += self.gravity
        
        # Замедления при особых действиях
        if self.actions['blocking']:
            self.velocity.x *= 0.7
        if self.actions['dodging']:
            self.velocity.y *= 0.8
        
        # Обновление позиции
        self.position += self.velocity
        self.rect.x = self.position.x
        self.rect.y = self.position.y

    def handle_collisions(self, platforms):
        """Обрабатывает столкновения с платформами"""
        self.on_ground = False
        
        # Проверка земли
        ground_check = pygame.Rect(
            self.rect.left + 5, 
            self.rect.bottom, 
            self.rect.width - 10, 
            self.ground_check_margin
        )
        
        for platform in platforms:
            # Основные столкновения
            if self.rect.colliderect(platform):
                self.resolve_collision(platform)
            
            # Проверка нахождения на земле
            if ground_check.colliderect(platform) and self.velocity.y >= 0:
                self.on_ground = True
                self.is_jumping = False
                self.rect.bottom = platform.top
                self.position.y = self.rect.y
                self.velocity.y = 0

    def resolve_collision(self, platform):
        """Разрешает столкновение с платформой"""
        overlaps = {
            'top': self.rect.bottom - platform.top,
            'bottom': platform.bottom - self.rect.top,
            'left': self.rect.right - platform.left,
            'right': platform.right - self.rect.left
        }
        
        min_direction = min(overlaps, key=overlaps.get)
        min_overlap = overlaps[min_direction]
        
        collision_handlers = {
            'top': self.handle_top_collision,
            'bottom': self.handle_bottom_collision, 
            'left': self.handle_left_collision,
            'right': self.handle_right_collision
        }
        
        handler = collision_handlers.get(min_direction)
        if handler:
            handler(platform, min_overlap)

    def handle_top_collision(self, platform, overlap):
        """Обрабатывает столкновение сверху (стоим на платформе)"""
        if self.velocity.y > 0:
            self.rect.bottom = platform.top
            self.position.y = self.rect.y
            self.velocity.y = 0
            self.on_ground = True
            self.is_jumping = False

    def handle_bottom_collision(self, platform, overlap):
        """Обрабатывает столкновение снизу (удар головой)"""
        if self.velocity.y < 0:
            self.rect.top = platform.bottom
            self.position.y = self.rect.y
            self.velocity.y = 0

    def handle_left_collision(self, platform, overlap):
        """Обрабатывает столкновение слева"""
        if self.velocity.x > 0:
            self.rect.right = platform.left
            self.position.x = self.rect.x
            if self.actions['dodging']:
                self.velocity.x = 0

    def handle_right_collision(self, platform, overlap):
        """Обрабатывает столкновение справа"""
        if self.velocity.x < 0:
            self.rect.left = platform.right
            self.position.x = self.rect.x
            if self.actions['dodging']:
                self.velocity.x = 0

    def update_animation_state(self):
        """Обновляет текущую анимацию на основе состояния"""
        priority_states = [
            ('attacking', 'attack'),
            ('blocking', 'block'), 
            ('dodging', 'dodge')
        ]
        
        # Проверяем состояния с высшим приоритетом
        for state_key, animation_name in priority_states:
            if self.actions[state_key]:
                self.current_animation = animation_name
                return
        
        # Базовые состояния
        if not self.on_ground:
            self.current_animation = "jump"
        elif self.velocity.x != 0:
            self.current_animation = "walk"
        else:
            self.current_animation = "idle"

    def update_animation(self):
        """Обновляет кадры анимации"""
        self.animation_frame += self.animation_speed
        frames = self.animations[self.current_animation]
        
        if not frames:
            return
            
        # Особые случаи анимаций
        if self.actions['blocking']:
            self.animation_frame = len(frames) - 1
            return
            
        if self.actions['attacking']:
            if self.animation_frame >= len(frames):
                if self.cooldowns['attack_animation'] <= 0:
                    self.animation_frame = 0
                    self.cooldowns['attack_animation'] = 15
                else:
                    self.animation_frame = len(frames) - 1
            return
            
        if self.actions['dodging'] and self.animation_frame >= len(frames):
            self.animation_frame = len(frames) - 1
            return
            
        # Стандартное зацикливание
        if self.animation_frame >= len(frames):
            self.animation_frame = 0

    def draw(self, camera_offset):
        """Отрисовывает игрока на экране"""
        frames = self.animations[self.current_animation]
        if not frames:
            return
            
        frame_index = min(int(self.animation_frame), len(frames) - 1)
        current_frame = frames[frame_index]
        
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        self.screen.blit(current_frame, (draw_x, draw_y))