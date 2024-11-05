import pygame
from os.path import dirname, join
import sys
import csv
import json

class Game():
    def __init__(self):

        pygame.init()
        pygame.mixer.init()

        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 640
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        self.level_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.environment_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.player_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.ui_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.menu_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.menu_surface.fill((0, 0, 0, 127))
        self.menu_select_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        

        self.clock = pygame.time.Clock()
        self.is_running = True

        self.dt = 0

        current_dir = dirname(__file__)


        self.is_show_debug = True

        self.player_sprite_static = self.load_tile(join(current_dir, "assets/player/tile_static.png"))
        self.player_sprite_jump_static = self.load_tile(join(current_dir, "assets/player/tile_jump_static.png"))
        self.player_sprite_jump_moving = self.load_tile(join(current_dir, "assets/player/tile_jump_moving.png"))
        self.player_sprite_jump_moving_flipped = pygame.transform.flip(self.player_sprite_jump_moving, True, False)
        self.misc_sprite_menu_select = self.load_tile(join(current_dir, "assets/misc/menu_select.png"), scale=3)

        self.tilemap_full = pygame.image.load(join(current_dir, "assets/misc/tilemap_full.png")).convert()
        self.tilemap_full = pygame.transform.scale(self.tilemap_full, (640, 640))
        self.tilemap_full.set_colorkey((0, 0, 0))
        self.tilemap_size = (20, 20)

        self.player_tileset_run = pygame.image.load(join(current_dir, "assets/player/tileset_run_flipped.png")).convert()
        self.player_tileset_run = pygame.transform.scale(self.player_tileset_run, (128, 64))
        self.player_tileset_run.set_colorkey((0, 0, 0))

        self.player_tileset_idle = pygame.image.load(join(current_dir, "assets/player/tileset_idle.png")).convert()
        self.player_tileset_idle = pygame.transform.scale(self.player_tileset_idle, (128, 32))
        self.player_tileset_idle.set_colorkey((0, 0, 0))

        self.sfx_death = pygame.mixer.Sound(join(current_dir, "assets/sfx/death_3.wav"))
        self.sfx_jump = pygame.mixer.Sound(join(current_dir, "assets/sfx/jump_4.wav"))
        self.sfx_jump.set_volume(0.6)
        self.sfx_menu_select = pygame.mixer.Sound(join(current_dir, "assets/sfx/menu_select.wav"))
        self.sfx_menu_select.set_volume(0.7)
        self.sfx_menu = pygame.mixer.Sound(join(current_dir, "assets/sfx/menu.wav"))
        self.sfx_menu.set_volume(0.5)
        self.sfx_quit = pygame.mixer.Sound(join(current_dir, "assets/sfx/quit.wav"))
        self.sfx_menu_enter = pygame.mixer.Sound(join(current_dir, "assets/sfx/menu_enter.wav"))
        self.sfx_menu_enter.set_volume(0.5)
        self.sfx_next_level = pygame.mixer.Sound(join(current_dir, "assets/sfx/next_level_6.wav"))
        self.sfx_next_level.set_volume(0.5)

        
        self.load_music(current_dir, 2)
        

        self.tile_size = 32
        self.sprite_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self.number_of_sprites = 4
        self.sprite_counter = 0
        self.sprite_frame_delay = 3
        self.sprite_frame_delay_counter = 0

        self.number_of_sprites_idle = 4
        self.sprite_counter_idle = 0
        self.sprite_frame_delay_idle = 8
        self.sprite_frame_delay_counter_idle = 0


        self.player_position = pygame.Vector2(self.screen.get_width() / 2 - self.tile_size / 2, self.screen.get_height() / 2)
        self.player_velocity = pygame.Vector2(0, 0)
        self.player_acceleration = pygame.Vector2(0, 0)

        self.is_player_on_ground = False
        self.previous_is_player_on_ground = self.is_player_on_ground
        self.is_movement_keys = False
        self.is_player_moving = False
        self.gravity = 10

        self.is_jumped = True

        self.is_dashed = False
        self.is_in_dash = False
        self.last_direction = 1
        self.enable_gravity = True

        self.fps = 0
        self.TARGET_FPS = 60

        self.font = pygame.font.Font(join(current_dir, "assets/fonts/Pono_048.ttf"), 80)
        self.font_menu = pygame.font.Font(join(current_dir, "assets/fonts/Pono_048.ttf"), 64)

        self.score = 0


        self.k_speed = 15
        self.k_friction = 10
        self.k_max_speed = 50
        self.k_gravity = 20
        self.k_terminal_velocity = 100

        self.coyote_time_jump_nof_frames = 7
        self.coyote_time_jump_countdown = self.coyote_time_jump_nof_frames
        self.start_coyote_timer = False
    
        self.coyote_time_jump_nof_frames_edge = 3
        self.coyote_time_jump_countdown_edge = self.coyote_time_jump_nof_frames_edge
        self.start_coyote_timer_edge = False

        self.dash_cooldown_nof_frames = 30
        self.dash_cooldown_countdown = self.dash_cooldown_nof_frames
        self.start_dash_cooldown_timer = False

        pygame.display.set_caption("FleaRun")

        self.is_paused = False
        self.menu_pressed_quit = False
        self.menu_pressed_resume = True
        self.menu_pressed_credits = False
        self.menu_pressed_confirm = False

        self.pause_menu_action = True

        self.render_pause_menu()

        self.level_names_list = ["main_screen", "lvl_1", "lvl_2", "lvl_3", "end"]
        self.level_names_list_working = self.level_names_list.copy()

        self.heart_tile_number = 41
        self.door_tile_number = 59
        self.empty_tile = 0

        self.load_next_level()
    

    def load_music(self, current_dir, track_number):
        if track_number == 1:
            pygame.mixer.music.load(join(current_dir, "assets/music/press_x_twice.mp3"))
        elif track_number == 2:
            pygame.mixer.music.load(join(current_dir, "assets/music/a_lil_bit.mp3"))
        elif track_number == 3:
            pygame.mixer.music.load(join(current_dir, "assets/music/power_walking.mp3"))

        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)


    def load_next_level(self):
        # print(self.level_names_list_working, self.level_names_list)
        level_name = self.level_names_list_working.pop(0)
        if level_name == "end":
            self.level_names_list_working = self.level_names_list.copy()
            level_name = self.level_names_list_working.pop(0)
            self.load_level_by_name(level_name)
        else:
            self.load_level_by_name(level_name)

    def load_level_by_name(self, level_name):
        current_dir = dirname(__file__)
        
        if level_name == "main_screen":
            self.load_level(join(current_dir, "assets/levels2/lvl2_0.json"))
            creator_text = self.font.render("Created by g0fher", True, (255, 255, 255))
            self.level_surface.blit(creator_text, (self.SCREEN_WIDTH / 2 - creator_text.get_width() / 2, self.SCREEN_HEIGHT / 5))
        elif level_name == "lvl_1":
            self.load_level(join(current_dir, "assets/levels2/lvl2_1.json"))
        elif level_name == "lvl_2":
            self.load_level(join(current_dir, "assets/levels2/lvl2_2.json"))
        elif level_name == "lvl_3":
            self.load_level(join(current_dir, "assets/levels2/lvl2_3.json"))



    def load_level(self, level_path, add=''):
        self.tiles, self.collision_boxes, self.spikes = self.read_json(level_path)
        
        self.where_is_door = (-1, -1)
        self.is_door = False

        self.where_is_heart = (-1, -1)
        self.is_heart = False

        self.render_level()

        if self.where_is_door != (-1, -1):
            self.door_rect = pygame.Rect(self.where_is_door[0], self.where_is_door[1], self.tile_size, self.tile_size)
            self.is_door = True
        if self.where_is_heart != (-1, -1):
            self.heart_rect = pygame.Rect(self.where_is_heart[0], self.where_is_heart[1], self.tile_size, self.tile_size)
            self.is_heart = True
            self.player_position.x = self.where_is_heart[0]
            self.player_position.y = self.where_is_heart[1]

        
    def load_tile(self, filepath, scale = 2):
        image = pygame.image.load(filepath).convert()
        image = pygame.transform.scale(image, (16 * scale, 16 * scale))
        image.set_colorkey((0, 0, 0))
        return image

    def render_score(self):
        self.ui_surface.fill((0, 0, 0, 0))
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.ui_surface.blit(score_text, (10, 10))

    def jump(self):
        self.player_velocity.y += -200
        self.is_player_on_ground = False
        self.is_jumped = True
        self.sfx_jump.play()

    def dash(self):
        if not self.start_dash_cooldown_timer:
            self.is_dashed = True
            self.is_in_dash = True
            self.enable_gravity = False
            # self.is_player_on_ground = True
            
            self.player_velocity.y = 0
            self.player_velocity.x = 0

            self.k_max_speed = 300
            self.k_friction = 20

            if self.last_direction == 1:
                self.player_velocity.x += 200
            
            if self.last_direction == -1:   
                self.player_velocity.x -= 200
            
            self.start_dash_cooldown_timer = True
            # if self.is_show_debug:
            #     print("Dashed")
    
    def death(self, play_sfx=True):
        if self.is_heart:
            self.player_position.x = self.where_is_heart[0]
            self.player_position.y = self.where_is_heart[1]
        else:
            self.player_position.x = self.screen.get_width() / 2 - self.tile_size / 2
            self.player_position.y = self.screen.get_height() / 2
        self.player_velocity.y = 0
        self.player_velocity.x = 0
        self.is_jumped = True
        self.is_player_on_ground = False
        self.start_coyote_timer = False
        self.start_coyote_timer_edge = False
        self.start_dash_cooldown_timer = False
        self.k_max_speed = 50
        self.k_friction = 10
        self.is_dashed = False
        self.is_in_dash = False
        self.enable_gravity = True
        if play_sfx:
            self.sfx_death.play()

    def collision_detection_horizontal(self):
        player_rect = pygame.Rect(self.player_position.x, self.player_position.y, 32, 32)
        for collision_box in self.collision_boxes:
            if player_rect.colliderect(collision_box):
                if self.player_velocity.x > 0:
                    self.player_position.x = collision_box.left - 32
                    self.player_velocity.x = 0
                elif self.player_velocity.x < 0:
                    self.player_position.x = collision_box.right
                    self.player_velocity.x = 0
    
    def collision_detection_vertical(self):
        player_rect = pygame.Rect(self.player_position.x, self.player_position.y, 32, 32)
        for collision_box in self.collision_boxes:
            if player_rect.colliderect(collision_box):
                if self.player_velocity.y > 0:
                    self.player_position.y = collision_box.top - 32
                    self.player_velocity.y = 0
                    self.is_jumped = False
                    self.is_player_on_ground = True
                elif self.player_velocity.y < 0:
                    self.player_position.y = collision_box.bottom
                    self.player_velocity.y = 0
    
    def spikes_collision(self):
        player_rect = pygame.Rect(self.player_position.x, self.player_position.y, 32, 32)
        for collision_box in self.spikes:
            if player_rect.colliderect(collision_box):
                self.death()

    def extract_objects_from_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        objects = []
        for layer in data['layers']:
            if layer['type'] == 'objectgroup':
                for obj in layer['objects']:
                    objects.append(pygame.Rect(obj['x'] * 2, obj['y'] * 2, obj['width'] * 2, obj['height'] * 2))
        
        return objects

    def read_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        tiles = []
        colliders = []
        spikes = []

        for layer in data['layers']:
            if layer['name'] == 'tiles':
                width = layer['width']
                for i in range(0, len(layer['data']), width):
                    tiles.append(layer['data'][i:i + width])

            if layer['name'] == 'collision':
                for obj in layer['objects']:
                    colliders.append(pygame.Rect(obj['x'] * 2, obj['y'] * 2, obj['width'] * 2, obj['height'] * 2))
            
            if layer['name'] == 'spikes':
                for obj in layer['objects']:
                    spikes.append(pygame.Rect(obj['x'] * 2, obj['y'] * 2, obj['width'] * 2, obj['height'] * 2))
            
        return tiles, colliders, spikes
    
    # def read_csv(self, filename):
    #     level_map = []
    #     with open(filename) as data:
    #         data = csv.reader(data, delimiter=',')
    #         for row in data:
    #             level_map.append(list(row))
    #     return level_map

    def render_level(self):
        self.level_surface.fill((0, 0, 0, 0))
        # level_map = self.read_csv(filename)
        level_map = self.tiles
        
        for i in range(len(level_map)):
            for j in range(len(level_map[0])):
                if int(level_map[i][j]) == self.empty_tile:
                    continue
                else:
                    if int(level_map[i][j]) == self.door_tile_number:
                        self.where_is_door = (j * self.tile_size, i * self.tile_size)
                    elif int(level_map[i][j]) == self.heart_tile_number:
                        self.where_is_heart = (j * self.tile_size, i * self.tile_size)
                    self.level_surface.blit(self.tilemap_full, (j * self.tile_size, i * self.tile_size), (((int(level_map[i][j]) - 1) % self.tilemap_size[0]) * self.tile_size, ((int(level_map[i][j]) - 1) // self.tilemap_size[1]) * self.tile_size, self.tile_size, self.tile_size))
    
    def render_pause_menu(self):
        self.resume = self.font_menu.render("Resume", True, (255, 255, 255))
        self.quit = self.font_menu.render("Quit", True, (255, 255, 255))
        self.menu_surface.blit(self.resume, (self.SCREEN_WIDTH / 2 - self.resume.get_width() / 2, self.SCREEN_HEIGHT / 5))
        self.menu_surface.blit(self.quit, (self.SCREEN_WIDTH / 2 - self.quit.get_width() / 2, self.SCREEN_HEIGHT / 5 + self.font_menu.get_height() * 1.2))

    def run(self):
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.mixer.music.stop()
                    pygame.time.wait(500)
                    if self.is_show_debug:
                        print("Shut down.")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.is_paused:
                            self.is_paused = False
                            self.sfx_menu_select.play()
                            pygame.mixer.music.set_volume(0.2)
                        else:
                            self.is_paused = True
                            self.sfx_menu_enter.play()
                            if self.is_show_debug:
                                print("Pause")
                            pygame.mixer.music.set_volume(0.05)
                    if not self.is_paused:
                        if event.key == pygame.K_r:
                            self.death()
                        if event.key == pygame.K_SPACE:
                            if not self.is_jumped:
                                # if self.is_player_on_ground or self.start_coyote_timer_edge:
                                #     self.jump()
                                if self.is_player_on_ground:
                                    self.jump()
                                elif self.start_coyote_timer_edge:
                                    self.jump()
                                    if self.is_show_debug:
                                        print("coyote edge", self.coyote_time_jump_countdown_edge)
                            else:
                                self.start_coyote_timer = True
                        if event.key == pygame.K_LSHIFT:
                            # print("shift")
                            if not self.start_dash_cooldown_timer:
                                self.dash()
                    else:
                        self.pause_menu_action = True

                        self.menu_pressed_confirm = False
                        if event.key == pygame.K_s:
                            if not self.menu_pressed_quit:
                                self.sfx_menu.play()
                                self.menu_pressed_quit = True
                                self.menu_pressed_resume = False
                                self.menu_pressed_confirm = False
                        elif event.key == pygame.K_w:
                            if not self.menu_pressed_resume:
                                self.sfx_menu.play()
                                self.menu_pressed_resume = True
                                self.menu_pressed_quit = False
                                self.menu_pressed_confirm = False
                        elif event.key == pygame.K_SPACE:
                            self.menu_pressed_confirm = True
            

            if self.is_paused:

                if self.pause_menu_action:

                    self.menu_select_surface.fill((0, 0, 0, 0))

                    if self.menu_pressed_confirm:
                        if self.menu_pressed_resume:
                            self.sfx_menu_select.play()
                            self.is_paused = False
                            pygame.mixer.music.set_volume(0.2)
                            if self.is_show_debug:
                                print("Unpause")
                        elif self.menu_pressed_quit:
                            self.is_running = False
                            self.sfx_quit.play()
                            pygame.mixer.music.stop()
                            pygame.time.wait(500)
                            if self.is_show_debug:
                                print("Shut down.")
                    else:
                        if self.menu_pressed_resume:
                            self.menu_select_surface.blit(self.misc_sprite_menu_select, (self.SCREEN_WIDTH / 2 - self.resume.get_width() / 2 - 64, self.SCREEN_HEIGHT / 5 + self.resume.get_height() * 0.2))
                        elif self.menu_pressed_quit:
                            self.menu_select_surface.blit(self.misc_sprite_menu_select, (self.SCREEN_WIDTH / 2 - self.resume.get_width() / 2 - 64, self.SCREEN_HEIGHT / 5 + self.resume.get_height() * 0.2 + self.font_menu.get_height() * 1.2))

                    self.screen.fill((0, 0, 0))
                    self.screen.blit(self.level_surface, (0, 0))
                    # self.screen.blit(self.environment_surface, (0, 0))
                    self.screen.blit(self.player_surface, (0, 0))
                    self.screen.blit(self.menu_surface, (0, 0))
                    self.screen.blit(self.menu_select_surface, (0, 0))
                    self.pause_menu_action = False


            else:
                
                self.is_player_moving = bool(abs(self.player_velocity.x))



                ### Select characher sprite for this frame
                if self.is_player_moving:
                    if self.is_player_on_ground:
                        self.sprite_frame_delay_counter = (self.sprite_frame_delay_counter + 1) % self.sprite_frame_delay
                        
                        if self.sprite_frame_delay_counter == 0:

                            self.sprite_surface.fill((0, 0, 0, 0))
                            
                            if self.player_velocity.x < 0:
                                self.sprite_surface.blit(self.player_tileset_run, (0, 0), (self.sprite_counter * self.tile_size, self.tile_size, self.tile_size, self.tile_size))
                            else:
                                self.sprite_surface.blit(self.player_tileset_run, (0, 0), (self.sprite_counter * self.tile_size, 0, self.tile_size, self.tile_size))
                            
                            self.sprite_counter = (self.sprite_counter + 1) % self.number_of_sprites
                    else:
                        self.sprite_surface.fill((0, 0, 0, 0))
                        if self.player_velocity.x < 0:
                            self.sprite_surface.blit(self.player_sprite_jump_moving_flipped, (0, 0))
                        else:
                            self.sprite_surface.blit(self.player_sprite_jump_moving, (0, 0))
                        self.sprite_frame_delay_counter = 0
                        self.sprite_counter = 0
                    
                    self.sprite_frame_delay_counter_idle = 0
                    self.sprite_counter_idle = 0
                else:
                    if self.is_player_on_ground:
                        self.sprite_frame_delay_counter_idle = (self.sprite_frame_delay_counter_idle + 1) % self.sprite_frame_delay_idle
                        # print("idle")
                        if self.sprite_frame_delay_counter_idle == 0:
                            self.sprite_surface.fill((0, 0, 0, 0))
                            self.sprite_surface.blit(self.player_tileset_idle, (0, 0), (self.sprite_counter_idle * self.tile_size, 0, self.tile_size, self.tile_size))
                            self.sprite_counter_idle = (self.sprite_counter_idle + 1) % self.number_of_sprites_idle

                    else:
                        self.sprite_surface.fill((0, 0, 0, 0))
                        self.sprite_surface.blit(self.player_sprite_jump_static, (0, 0))
                        self.sprite_frame_delay_counter_idle = 0
                        self.sprite_counter_idle = 0

                    self.sprite_frame_delay_counter = 0
                    self.sprite_counter = 0
                    




                ### Coyote time on landing
                if self.start_coyote_timer:
                    if self.is_player_on_ground:
                        if self.is_show_debug:
                            print("coyote landing", self.coyote_time_jump_countdown)
                        self.jump()
                        self.start_coyote_timer = False
                        self.coyote_time_jump_countdown = self.coyote_time_jump_nof_frames
                    else:
                        self.coyote_time_jump_countdown -= 1
                        if self.coyote_time_jump_countdown <= 0:
                            self.start_coyote_timer = False
                            self.coyote_time_jump_countdown = self.coyote_time_jump_nof_frames

                ### Coyote time on edge
                if self.start_coyote_timer_edge:
                    if self.is_player_on_ground:
                        self.start_coyote_timer_edge = False
                        self.coyote_time_jump_countdown_edge = self.coyote_time_jump_nof_frames_edge
                    else:
                        self.coyote_time_jump_countdown_edge -= 1
                        if self.coyote_time_jump_countdown_edge <= 0:
                            self.start_coyote_timer_edge = False
                            self.coyote_time_jump_countdown_edge = self.coyote_time_jump_nof_frames_edge

                ### Dash cooldown
                if self.start_dash_cooldown_timer:
                    self.dash_cooldown_countdown -= 1
                    if self.dash_cooldown_countdown <= 0:
                        self.start_dash_cooldown_timer = False
                        self.dash_cooldown_countdown = self.dash_cooldown_nof_frames
                        self.is_dashed = False
                        print("Dash restored")

                # Get input keys
                keys = pygame.key.get_pressed()

                if not self.is_in_dash:
                    if keys[pygame.K_a]:
                        if self.player_velocity.x > -self.k_max_speed:
                            self.player_velocity.x -= self.k_speed

                    elif keys[pygame.K_d]:
                        if self.player_velocity.x < self.k_max_speed:
                            self.player_velocity.x += self.k_speed
               
                    # Apply friction if the player is moving without any movement keys pressed
                    else:
                        if self.player_velocity.x > 0:
                            self.player_velocity.x -= self.k_friction
                            if self.player_velocity.x < 0:
                                self.player_velocity.x = 0
                        elif self.player_velocity.x < 0:
                            self.player_velocity.x += self.k_friction
                            if self.player_velocity.x > 0:
                                self.player_velocity.x = 0
                
                else:
                    # print("input blocked")
                    if self.player_velocity.x > 0:
                        self.player_velocity.x -= self.k_friction
                        if self.player_velocity.x < 0:
                            self.player_velocity.x = 0
                    elif self.player_velocity.x < 0:
                        self.player_velocity.x += self.k_friction
                        if self.player_velocity.x > 0:
                            self.player_velocity.x = 0

                
                # Limit velocity
                if self.player_velocity.x > self.k_max_speed:
                    self.player_velocity.x = self.k_max_speed
                elif self.player_velocity.x < -self.k_max_speed:
                    self.player_velocity.x = -self.k_max_speed
                
                # Apply horizontal velocity to change the X position
                self.player_position.x += self.player_velocity.x * self.dt * 10

                if self.player_velocity.x > 0:
                    self.last_direction = 1
                elif self.player_velocity.x < 0:
                    self.last_direction = -1

                if self.is_in_dash and self.player_velocity.x == 0:
                    self.enable_gravity = True
                    self.is_dashed = False
                    self.is_in_dash = False
                    self.k_max_speed = 50
                    self.k_friction = 10
                    # if self.is_show_debug:
                    #     print("Gravity on")
                
                # if self.is_dashed:
                #     print("Is dashed")
                # if self.is_in_dash:
                #     print("Is in dash")
                

                self.collision_detection_horizontal()

                # Apply gravity
                # if not self.is_player_on_ground or self.is_apply_gravity_always:
                if self.enable_gravity:
                    self.is_player_on_ground = False
                    self.player_velocity.y += self.k_gravity
                    # Limit fall velocity
                    if self.player_velocity.y >= self.k_terminal_velocity:
                        self.player_velocity.y = self.k_terminal_velocity
                
                # Apply vertical velocity to change the Y position
                self.player_position.y += self.player_velocity.y * self.dt * 10

                self.collision_detection_vertical()


                if self.previous_is_player_on_ground and not self.is_player_on_ground:
                    # start coyote edge timer
                    self.start_coyote_timer_edge = True

                self.previous_is_player_on_ground = self.is_player_on_ground

                self.spikes_collision()

                # if player_rect.colliderect(self.basic_floor):
                #     if self.player_velocity.y >  0:
                #         self.player_position.y = self.basic_floor.top - 32
                #         self.player_velocity.y = 0
                #         self.is_jumped = False
                #         self.is_player_on_ground = True
                #         # print("on ground")

                # self.check_collision_player(player_rect)

                # self.collision(player_rect, self.basic_floor)
                # self.collision(player_rect, self.basic_floor_2)                
                    
                player_rect = pygame.Rect(self.player_position.x, self.player_position.y, 32, 32)
                if self.is_door:
                    if player_rect.colliderect(self.door_rect):
                        self.load_next_level()
                        self.death(play_sfx=False)
                        self.sfx_next_level.play()
                        # print("door")

                # Prevent player from going offscreen
                if self.player_position.y > self.SCREEN_HEIGHT or self.player_position.y < 0 or self.player_position.x > self.SCREEN_WIDTH or self.player_position.x < 0 - 32:
                    self.death()


                self.screen.fill((0, 0, 0))
                self.player_surface.fill((0, 0, 0, 0))

                # Draw the player
                # if self.player_velocity.x != 0:
                #     pass
                # self.player_surface.blit(self.player_sprite_static, self.player_position)
                self.player_surface.blit(self.sprite_surface, self.player_position)

                # self.environment_surface.fill((10, 5, 15, 0))

                # if player_rect.colliderect(self.basic_floor):
                #     pygame.draw.rect(self.environment_surface, (128, 128, 128), self.basic_floor)
                # else:

                # collision boxes debug
                # for box in self.collision_boxes:
                #     # box_rect = pygame.Rect(box[0], box[1], box[2], box[3])
                #     pygame.draw.rect(self.environment_surface, (255, 255, 255, 100), box)

                # pygame.draw.rect(self.environment_surface, (255, 255, 255), self.basic_floor)

                # pygame.draw.rect(self.environment_surface, (255, 255, 255), self.basic_floor_2)
                
                # self.screen.blit(self.environment_surface, (0, 0))
                self.screen.blit(self.level_surface, (0, 0))
                self.screen.blit(self.player_surface, (0, 0))


            pygame.display.update()

            # Get time between frames in seconds
            # Fix fps to target fps
            self.dt = self.clock.tick(self.TARGET_FPS) / 1000
            # print(self.dt)

            # self.fps = self.clock.get_fps()
            # print(self.fps)

        pygame.quit()

if __name__ == "__main__":
    Game().run()
    sys.exit()
