import pygame
import os
import re

class Player:
    def __init__(self, x, y, screen, assets_path, game_manager=None, 
                 controls=None, player_id=1, facing_right=True):
        self.screen = screen
        self.assets_path = assets_path
        self.game_manager = game_manager
        self.player_id = player_id
        
        # Начальная позиция для возрождения
        self.spawn_position = pygame.Vector2(x, y)
        
        # Управление
        self.controls = controls or {
            'left': pygame.K_a,
            'right': pygame.K_d, 
            'jump': pygame.K_w,
            'attack': pygame.K_e,
            'heavy_attack': pygame.K_q,
            'block': pygame.K_s
        }
        
        # Физика и движение
        self.setup_physics(x, y)
        
        # Боевая система
        self.setup_combat()
        
        # Анимации
        self.setup_animations(facing_right)
        
        # Состояния и таймеры
        self.setup_state()
    
    def setup_physics(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        
        self.gravity = 0.5
        self.jump_power = -12
        self.speed = 5
        self.ground_check_margin = 5
        
        self.rect = pygame.Rect(x, y, 80, 120)
        self.on_ground = True
        self.is_jumping = False
        self.was_on_ground = True
    
    def setup_combat(self):
        self.health = 100
        self.attack_damage = 10
        self.heavy_attack_damage = 20
        self.attack_hitbox = pygame.Rect(0, 0, 0, 0)
        self.attack_range = 70
        self.attack_active = False
        self.attack_animation_completed = False
    
    def setup_animations(self, facing_right):
        self.animations = {}
        self.current_animation = "idle"
        self.animation_frame = 0
        self.facing_right = facing_right
        
        # НАСТРОЙКИ СКОРОСТИ АНИМАЦИЙ (кадров в секунду)
        self.animation_speeds = {
            "idle": 8,
            "walk": 12,  
            "attack": 10,
            "heavy_attack": 8,
            "block": 1,
            "death": 6,
            "jump": 10,
            "hurt": 8,
            "respawn": 10  # Новая анимация возрождения
        }
        
        # ВРЕМЯ АНИМАЦИЙ В СЕКУНДАХ
        self.animation_durations = {
            "attack": 0.7,
            "heavy_attack": 1.0,
            "hurt": 0.5,
            "death": 1.5,
            "respawn": 1.0  # 1 секунда на анимацию возрождения
        }
        
        self.load_animations()
    
    def setup_state(self):
        self.actions = {
            'attacking': False,
            'heavy_attacking': False,
            'blocking': False,
            'stunned': False,
            'dead': False,
            'respawning': False  # Новое состояние - возрождение
        }
        
        self.cooldowns = {
            'attack': 0,
            'heavy_attack': 0,
            'stun': 0,
            'attack_hit_timer': 0,
            'respawn_timer': 0  # Таймер возрождения
        }
        
        self.animation_flags = {
            'jump_started': False,
            'jump_completed': False,
            'attack_animation_completed': False,
            'death_animation_completed': False,
            'respawn_animation_completed': False
        }
        
        # Таймеры для контроля времени анимаций
        self.animation_timers = {
            'attack_start_time': 0,
            'death_start_time': 0,
            'respawn_start_time': 0,
            'current_animation_duration': 0
        }
    
    def get_animation_speed(self, animation_name):
        return self.animation_speeds.get(animation_name, 10)
    
    def get_animation_duration(self, animation_name):
        return self.animation_durations.get(animation_name, 1.0)
    
    def is_facing_attacker(self, attacker):
        if attacker.rect.centerx > self.rect.centerx:
            return not self.facing_right
        else:
            return self.facing_right
    
    def load_animations(self):
        animation_folders = {
            "idle": "player/idle",
            "walk": "player/walk", 
            "attack": "player/attack",
            "heavy_attack": "player/heavy_attack",
            "block": "player/block",
            "death": "player/death",
            "jump": "player/jump",
            "hurt": "player/hurt",
            "respawn": "player/respawn"  # Новая папка для анимации возрождения
        }
        
        for state, folder in animation_folders.items():
            self.animations[state] = self.load_animation_frames(folder)
            frame_count = len(self.animations[state])
            print(f"Загружено {frame_count} кадров для {state}")
    
    def load_animation_frames(self, folder):
        frames = []
        full_path = os.path.join(self.assets_path, folder)
        
        if os.path.exists(full_path):
            try:
                all_files = [f for f in os.listdir(full_path) 
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                
                def extract_number(filename):
                    numbers = re.findall(r'\d+', filename)
                    return int(numbers[0]) if numbers else 0
                
                image_files = sorted(all_files, key=extract_number)
                
                if not image_files:
                    return frames
                
                for filename in image_files:
                    image_path = os.path.join(full_path, filename)
                    try:
                        image = pygame.image.load(image_path).convert_alpha()
                        image = pygame.transform.scale(image, (100, 150))
                        frames.append(image)
                    except Exception as e:
                        print(f"Ошибка загрузки {image_path}: {e}")
                        
            except Exception as e:
                print(f"Ошибка обработки папки {folder}: {e}")
        
        if not frames:
            frames = self.create_placeholder_animation(folder.split('/')[-1])
            
        return frames
    
    def create_placeholder_animation(self, state):
        color_map = {
            "idle": (0, 255, 0),
            "walk": (255, 255, 0),
            "attack": (255, 0, 0),
            "heavy_attack": (200, 0, 0),
            "block": (0, 0, 255),
            "death": (128, 128, 128),
            "jump": (0, 255, 255),
            "hurt": (255, 255, 255),
            "respawn": (0, 255, 0)  # Зеленый для возрождения
        }
        
        frames_config = {
            "idle": 4,
            "walk": 8, 
            "attack": 7,
            "heavy_attack": 7,
            "block": 1,
            "jump": 9,
            "hurt": 3,
            "death": 5,
            "respawn": 6  # 6 кадров для возрождения
        }
        
        frames_count = frames_config.get(state, 1)
        frames = []
        
        for i in range(frames_count):
            surf = pygame.Surface((100, 150), pygame.SRCALPHA)
            color = color_map.get(state, (255, 255, 255))
            
            pygame.draw.rect(surf, color, (0, 0, 100, 150))
            
            font = pygame.font.Font(None, 20)
            frame_text = font.render(f"{state} {i}", True, (0, 0, 0))
            frame_rect = frame_text.get_rect(center=(50, 75))
            surf.blit(frame_text, frame_rect)
            
            pygame.draw.rect(surf, (0, 0, 0), (0, 0, 100, 150), 2)
            frames.append(surf)
        
        return frames

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls['jump']:
                self.jump()
            elif event.key == self.controls['attack']:
                self.attack()
            elif event.key == self.controls['heavy_attack']:
                self.heavy_attack()
            elif event.key == self.controls['block']:
                self.start_block()
        
        elif event.type == pygame.KEYUP:
            if event.key == self.controls['block']:
                self.stop_block()

    def handle_input(self):
        # ЕСЛИ ИГРОК МЕРТВ ИЛИ ВОЗРОЖДАЕТСЯ - НИКАКОГО ВВОДА
        if self.actions['dead'] or self.actions['respawning']:
            self.velocity.x = 0
            return
            
        keys = pygame.key.get_pressed()
        
        if self.actions['stunned']:
            return
        
        if keys[self.controls['left']]:
            self.velocity.x = -self.speed
            self.facing_right = False
        elif keys[self.controls['right']]:
            self.velocity.x = self.speed
            self.facing_right = True
        else:
            self.velocity.x = 0

    def attack(self):
        if (self.actions['attacking'] or self.cooldowns['attack'] > 0 or 
            self.actions['stunned'] or self.actions['dead'] or self.actions['respawning']):
            return
            
        self.actions['attacking'] = True
        self.current_animation = "attack"
        self.animation_frame = 0
        self.cooldowns['attack'] = 45
        self.attack_damage = 10
        self.attack_active = False
        self.animation_flags['attack_animation_completed'] = False
        
        self.animation_timers['attack_start_time'] = pygame.time.get_ticks()
        self.animation_timers['current_animation_duration'] = self.get_animation_duration("attack")

    def heavy_attack(self):
        if (self.actions['attacking'] or self.cooldowns['heavy_attack'] > 0 or 
            self.actions['stunned'] or self.actions['dead'] or self.actions['respawning']):
            return
            
        self.actions['attacking'] = True
        self.actions['heavy_attacking'] = True
        self.current_animation = "heavy_attack"
        self.animation_frame = 0
        self.cooldowns['heavy_attack'] = 60
        self.attack_damage = 20
        self.attack_active = False
        self.animation_flags['attack_animation_completed'] = False
        
        self.animation_timers['attack_start_time'] = pygame.time.get_ticks()
        self.animation_timers['current_animation_duration'] = self.get_animation_duration("heavy_attack")

    def create_attack_hitbox(self):
        if self.facing_right:
            self.attack_hitbox = pygame.Rect(
                self.rect.right,
                self.rect.centery - 30,
                self.attack_range,
                60
            )
        else:
            self.attack_hitbox = pygame.Rect(
                self.rect.left - self.attack_range,
                self.rect.centery - 30,
                self.attack_range,
                60
            )

    def start_block(self):
        if self.actions['stunned'] or self.actions['dead'] or self.actions['respawning']:
            return
            
        self.actions['blocking'] = True
        self.current_animation = "block"

    def stop_block(self):
        self.actions['blocking'] = False

    def jump(self):
        if (self.on_ground and not self.actions['attacking'] and 
            not self.actions['stunned'] and not self.actions['dead'] and not self.actions['respawning']):
            self.velocity.y = self.jump_power
            self.is_jumping = True
            self.on_ground = False
            self.animation_flags['jump_started'] = True
            self.animation_flags['jump_completed'] = False
            
            if self.game_manager:
                self.game_manager.play_sound('jump')

    def take_damage(self, damage):
        # Не получаем урон если мертвы или возрождаемся
        if self.actions['dead'] or self.actions['respawning']:
            return
            
        self.health = max(0, self.health - damage)
        
        if self.health > 0:
            self.current_animation = "hurt"
            self.animation_frame = 0
            self.stun(30)
        else:
            self.die()

    def knockback(self, direction_right, force):
        self.velocity.x = force if direction_right else -force
        self.velocity.y = -3

    def stun(self, duration):
        self.actions['stunned'] = True
        self.cooldowns['stun'] = duration

    def die(self):
        self.actions['dead'] = True
        self.current_animation = "death"
        self.animation_frame = 0
        self.velocity = pygame.Vector2(0, 0)
        self.animation_flags['death_animation_completed'] = False
        
        # Запоминаем время смерти для таймера возрождения
        self.animation_timers['death_start_time'] = pygame.time.get_ticks()
        
        print(f"Игрок {self.player_id} умер, возрождение через 5 секунд")

    def respawn(self):
        """Возрождает игрока"""
        self.actions['dead'] = False
        self.actions['respawning'] = True
        self.actions['stunned'] = False
        self.health = 100
        self.current_animation = "respawn"
        self.animation_frame = 0
        self.animation_flags['respawn_animation_completed'] = False
        
        # Возвращаем на начальную позицию
        self.position = pygame.Vector2(self.spawn_position.x, self.spawn_position.y)
        self.rect.x = self.position.x
        self.rect.y = self.position.y
        self.velocity = pygame.Vector2(0, 0)
        
        self.animation_timers['respawn_start_time'] = pygame.time.get_ticks()
        self.animation_timers['current_animation_duration'] = self.get_animation_duration("respawn")
        
        print(f"Игрок {self.player_id} возрождается!")

    def update(self, platforms, players):
        self.was_on_ground = self.on_ground
        
        # ОБНОВЛЯЕМ ВОЗРОЖДЕНИЕ
        self.update_respawn()
        
        # ЕСЛИ МЕРТВ ИЛИ ВОЗРОЖДАЕТСЯ - ТОЛЬКО ОБНОВЛЯЕМ АНИМАЦИЮ
        if self.actions['dead'] or self.actions['respawning']:
            self.update_animation()
            return
            
        self.handle_input()
        self.apply_physics()
        self.handle_collisions(platforms)
        self.update_cooldowns()
        self.update_animation_state()
        self.update_animation()
        self.update_attack_hitbox()
        
        if self.animation_flags['jump_started'] and self.animation_frame > 0:
            self.animation_flags['jump_started'] = False
    
    def update_respawn(self):
        """Обновляет логику возрождения"""
        if self.actions['dead'] and not self.actions['respawning']:
            # Проверяем прошло ли 5 секунд с момента смерти
            current_time = pygame.time.get_ticks()
            time_since_death = (current_time - self.animation_timers['death_start_time']) / 1000.0
            
            if time_since_death >= 5.0:  # 5 секунд
                self.respawn()
        
        elif self.actions['respawning']:
            # Проверяем завершилась ли анимация возрождения
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.animation_timers['respawn_start_time']) / 1000.0
            
            if elapsed_time >= self.animation_timers['current_animation_duration']:
                # Завершаем возрождение
                self.actions['respawning'] = False
                self.current_animation = "idle"
                self.animation_frame = 0
                print(f"Игрок {self.player_id} полностью возродился!")
    
    def update_attack_hitbox(self):
        if self.actions['attacking']:
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.animation_timers['attack_start_time']) / 1000.0
            progress = elapsed_time / self.animation_timers['current_animation_duration']
            
            if progress >= 0.7 and not self.attack_active:
                self.attack_active = True
                self.create_attack_hitbox()
            
            if progress >= 0.95 and self.attack_active:
                self.attack_active = False
        else:
            self.attack_active = False
    
    def update_cooldowns(self):
        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] -= 1
        
        # Завершение атаки по времени
        if self.actions['attacking']:
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - self.animation_timers['attack_start_time']) / 1000.0
            
            if elapsed_time >= self.animation_timers['current_animation_duration']:
                self.actions['attacking'] = False
                self.actions['heavy_attacking'] = False
                self.attack_active = False
                self.animation_flags['attack_animation_completed'] = False
        
        if self.actions['stunned'] and self.cooldowns['stun'] <= 0:
            self.actions['stunned'] = False

    def apply_physics(self):
        if not self.on_ground:
            self.velocity.y += self.gravity
        
        if self.actions['blocking']:
            self.velocity.x *= 0.7
        
        self.position += self.velocity
        self.rect.x = self.position.x
        self.rect.y = self.position.y

    def handle_collisions(self, platforms):
        self.on_ground = False
        
        ground_check = pygame.Rect(
            self.rect.left + 8, 
            self.rect.bottom, 
            self.rect.width - 16, 
            self.ground_check_margin
        )
        
        for platform in platforms:
            if self.rect.colliderect(platform):
                self.resolve_collision(platform)
            
            if ground_check.colliderect(platform) and self.velocity.y >= 0:
                self.on_ground = True
                self.is_jumping = False
                self.rect.bottom = platform.top
                self.position.y = self.rect.y
                self.velocity.y = 0
                
                if not self.was_on_ground:
                    self.animation_flags['jump_completed'] = True

    def resolve_collision(self, platform):
        overlaps = {
            'top': self.rect.bottom - platform.top,
            'bottom': platform.bottom - self.rect.top,
            'left': self.rect.right - platform.left,
            'right': platform.right - self.rect.left
        }
        
        min_direction = min(overlaps, key=overlaps.get)
        min_overlap = overlaps[min_direction]
        
        if min_direction == 'top' and self.velocity.y > 0:
            self.rect.bottom = platform.top
            self.position.y = self.rect.y
            self.velocity.y = 0
            self.on_ground = True
            self.is_jumping = False
        elif min_direction == 'bottom' and self.velocity.y < 0:
            self.rect.top = platform.bottom
            self.position.y = self.rect.y
            self.velocity.y = 0
        elif min_direction == 'left' and self.velocity.x > 0:
            self.rect.right = platform.left
            self.position.x = self.rect.x
        elif min_direction == 'right' and self.velocity.x < 0:
            self.rect.left = platform.right
            self.position.x = self.rect.x

    def update_animation_state(self):
        if self.actions['dead']:
            self.current_animation = "death"
            return
            
        if self.actions['respawning']:
            self.current_animation = "respawn"
            return
            
        if self.actions['stunned']:
            if self.current_animation != "hurt":
                self.current_animation = "hurt"
            return
            
        if self.actions['attacking']:
            return
            
        if self.actions['blocking']:
            self.current_animation = "block"
        elif not self.on_ground:
            self.current_animation = "jump"
        elif self.velocity.x != 0:
            self.current_animation = "walk"
        else:
            self.current_animation = "idle"

    def update_animation(self):
        if not self.animations[self.current_animation]:
            return
            
        frames = self.animations[self.current_animation]
        max_frame = len(frames) - 1
        
        animation_speed = self.get_animation_speed(self.current_animation) / 60.0
        
        # ХОДЬБА - ЗАЦИКЛИВАЕМ
        if self.current_animation == "walk":
            self.animation_frame += animation_speed
            if self.animation_frame >= len(frames):
                self.animation_frame = 0
        
        # IDLE - зацикливаем
        elif self.current_animation == "idle":
            self.animation_frame += animation_speed
            if self.animation_frame >= len(frames):
                self.animation_frame = 0
        
        # ПРЫЖОК - проигрывается один раз полностью
        elif self.current_animation == "jump":
            if not self.animation_flags['jump_completed']:
                self.animation_frame += animation_speed
                if self.animation_frame >= max_frame:
                    self.animation_frame = max_frame
                    self.animation_flags['jump_completed'] = True
        
        # АТАКИ - проигрываются по времени
        elif self.current_animation in ["attack", "heavy_attack"]:
            if self.actions['attacking']:
                current_time = pygame.time.get_ticks()
                elapsed_time = (current_time - self.animation_timers['attack_start_time']) / 1000.0
                progress = elapsed_time / self.animation_timers['current_animation_duration']
                
                self.animation_frame = progress * max_frame
                
                if progress >= 1.0:
                    self.animation_frame = max_frame
        
        # СМЕРТЬ - проигрывается один раз полностью
        elif self.current_animation == "death":
            self.animation_frame += animation_speed
            if self.animation_frame >= max_frame:
                self.animation_frame = max_frame
        
        # ВОЗРОЖДЕНИЕ - проигрывается один раз полностью
        elif self.current_animation == "respawn":
            if self.actions['respawning']:
                current_time = pygame.time.get_ticks()
                elapsed_time = (current_time - self.animation_timers['respawn_start_time']) / 1000.0
                progress = elapsed_time / self.animation_timers['current_animation_duration']
                
                self.animation_frame = progress * max_frame
                
                if progress >= 1.0:
                    self.animation_frame = max_frame
        
        # УРОН - проигрывается один раз полностью
        elif self.current_animation == "hurt":
            self.animation_frame += animation_speed
            if self.animation_frame >= max_frame:
                self.animation_frame = max_frame
        
        # БЛОК - зацикливаем первую анимацию
        elif self.current_animation == "block":
            self.animation_frame = 0
        
        # Ограничиваем рамки
        if self.animation_frame > max_frame:
            self.animation_frame = max_frame
        if self.animation_frame < 0:
            self.animation_frame = 0

    def draw(self, camera_offset):
        frames = self.animations[self.current_animation]
        if not frames:
            return
            
        frame_index = min(int(self.animation_frame), len(frames) - 1)
        current_frame = frames[frame_index]
        
        if self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        self.screen.blit(current_frame, (draw_x, draw_y))
        
        # Отладочная информация
        if self.game_manager and self.game_manager.debug_mode:
            font = pygame.font.Font(None, 24)
            frames = self.animations[self.current_animation]
            
            anim_text = f"{self.current_animation}: {int(self.animation_frame)+1}/{len(frames)}"
            anim_surf = font.render(anim_text, True, (255, 255, 255))
            self.screen.blit(anim_surf, (draw_x, draw_y - 20))
            
            # Таймер возрождения
            if self.actions['dead']:
                current_time = pygame.time.get_ticks()
                time_since_death = (current_time - self.animation_timers['death_start_time']) / 1000.0
                respawn_time = max(0, 5.0 - time_since_death)
                respawn_text = f"Respawn in: {respawn_time:.1f}s"
                respawn_surf = font.render(respawn_text, True, (255, 100, 100))
                self.screen.blit(respawn_surf, (draw_x, draw_y - 40))