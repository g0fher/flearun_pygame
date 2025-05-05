import pygame
from os.path import dirname, join
import sys
import json

class Game():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("FleaRun")

        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 640
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()
        self.dt = 0.0
        self.is_running = True
        self.fps = 0
        # Change at your own risk (don't)
        self.TARGET_FPS = 60

        # 0 - for no debug, 1 - for special action, 2 - for most being shown
        self.debug_level = 1

        current_dir = dirname(__file__)

        # Loading sound effects
        self.sfx_death = pygame.mixer.Sound(join(current_dir, "assets/sfx/death_3.wav"))
        self.sfx_jump = pygame.mixer.Sound(join(current_dir, "assets/sfx/jump_4.wav"))
        self.sfx_jump.set_volume(0.5)
        self.sfx_menu_select = pygame.mixer.Sound(join(current_dir, "assets/sfx/menu_select.wav"))
        self.sfx_menu_select.set_volume(0.7)
        self.sfx_menu = pygame.mixer.Sound(join(current_dir, "assets/sfx/menu.wav"))
        self.sfx_menu.set_volume(0.5)
        self.sfx_quit = pygame.mixer.Sound(join(current_dir, "assets/sfx/quit.wav"))
        self.sfx_menu_enter = pygame.mixer.Sound(join(current_dir, "assets/sfx/menu_enter.wav"))
        self.sfx_menu_enter.set_volume(0.5)
        self.sfx_next_level = pygame.mixer.Sound(join(current_dir, "assets/sfx/next_level_6.wav"))
        self.sfx_next_level.set_volume(0.5)
        self.sfx_dash = pygame.mixer.Sound(join(current_dir, "assets/sfx/slide.wav"))
        self.sfx_dash.set_volume(0.6)

        # Loading music
        self.current_track = 2
        self.load_music(self.current_track)
        self.max_music_tracks = 3

        # Creating fonts
        self.font = pygame.font.Font(join(current_dir, "assets/fonts/Pono_048.ttf"), 80)
        self.font_menu = pygame.font.Font(join(current_dir, "assets/fonts/Pono_048.ttf"), 64)
        self.font_score = pygame.font.Font(join(current_dir, "assets/fonts/Pono_048.ttf"), 32)
        self.font_tutorial = pygame.font.Font(join(current_dir, "assets/fonts/Pono_048.ttf"), 48)
        
        # Setting up all the surfaces
        self.level_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.environment_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.player_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.score_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.timer_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.menu_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.menu_surface.fill((0, 0, 0, 220))
        self.menu_select_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        self.tile_size = 32
        self.sprite_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        
        # Loading sprites and tilesets
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
        self.number_of_sprites_run = 4
        self.sprite_counter_run = 0
        self.sprite_frame_delay_run = 3
        self.sprite_frame_delay_counter_run = 0

        self.player_tileset_idle = pygame.image.load(join(current_dir, "assets/player/tileset_idle.png")).convert()
        self.player_tileset_idle = pygame.transform.scale(self.player_tileset_idle, (128, 32))
        self.player_tileset_idle.set_colorkey((0, 0, 0))
        self.number_of_sprites_idle = 4
        self.sprite_counter_idle = 0
        self.sprite_frame_delay_idle = 8
        self.sprite_frame_delay_counter_idle = 0

        # Player and movement
        self.player_position = pygame.Vector2(self.screen.get_width() / 2 - self.tile_size / 2, self.screen.get_height() / 2)
        self.player_velocity = pygame.Vector2(0, 0)
        self.player_acceleration = pygame.Vector2(0, 0)
        
        self.run_speed = 15
        self.base_run_max_speed = 50
        self.run_max_speed = self.base_run_max_speed
        self.base_friction = 10
        self.friction = self.base_friction
        self.gravity_force = 20
        self.enable_gravity = True
        self.terminal_velocity = 100
        self.jump_force = 200
        self.dash_force = 200

        self.is_player_on_ground = False
        self.previous_is_player_on_ground = self.is_player_on_ground
        self.is_movement_keys = False
        self.is_player_moving = False

        self.is_jumped = True
        self.is_double_jump = False
        self.is_used_double_jump = False

        self.is_dashed = False
        self.is_in_dash = False
        self.last_direction = 1

        self.coyote_time_jump_nof_frames = 7
        self.coyote_time_jump_countdown = self.coyote_time_jump_nof_frames
        self.start_coyote_timer = False
    
        self.coyote_time_jump_nof_frames_edge = 3
        self.coyote_time_jump_countdown_edge = self.coyote_time_jump_nof_frames_edge
        self.start_coyote_timer_edge = False

        self.dash_cooldown_nof_frames = 30
        self.dash_cooldown_countdown = self.dash_cooldown_nof_frames
        self.start_dash_cooldown_timer = False
        
        self.score = 0
        self.timer = 0.0

        # World and menues
        self.is_paused = False
        self.pause_menu_action = True
        self.menu_selected_quit = False
        self.menu_selected_resume = True
        self.menu_pressed_confirm = False

        self.render_pause_menu()

        self.level_names_list = ["main_screen", "lvl_1", "lvl_2", "lvl_3", "lvl_4", "end"]
        self.level_names_list_working = self.level_names_list.copy()

        self.heart_tile_number = 41
        self.door_tile_number = 59
        self.empty_tile_number = 0

        self.load_next_level()

    def load_music(self, track_number, current_dir=dirname(__file__)):
        if self.debug_level >= 2:
            print(f"Load music track {track_number}")

        if track_number == 1:
            pygame.mixer.music.load(join(current_dir, "assets/music/press_x_twice.mp3"))
        elif track_number == 2:
            pygame.mixer.music.load(join(current_dir, "assets/music/a_lil_bit.mp3"))
        elif track_number == 3:
            pygame.mixer.music.load(join(current_dir, "assets/music/power_walking.mp3"))
        else:
            if self.debug_level >= 1:
                print("Track not found")

        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)

    def cycle_music(self):
        if self.debug_level >= 1:
            print("Next music track")

        self.current_track += 1
        if self.current_track > self.max_music_tracks:
            self.current_track = 1
        self.load_music(self.current_track)

    def load_tile(self, filepath, scale=2):
        image = pygame.image.load(filepath).convert()
        image = pygame.transform.scale(image, (16 * scale, 16 * scale))
        image.set_colorkey((0, 0, 0))
        return image

    def render_pause_menu(self):
        self.resume = self.font_menu.render("Resume", True, (255, 255, 255))
        self.quit = self.font_menu.render("Quit", True, (255, 255, 255))
        self.menu_surface.blit(self.resume, (self.SCREEN_WIDTH / 2 - self.resume.get_width() / 2, self.SCREEN_HEIGHT / 5))
        self.menu_surface.blit(self.quit, (self.SCREEN_WIDTH / 2 - self.quit.get_width() / 2, self.SCREEN_HEIGHT / 5 + self.font_menu.get_height() * 1.2))

        self.tutorial_1 = self.font_tutorial.render("WASD-move, SPACE-jump, SHIFT-dash, ESC-pause", True, (255, 255, 255))
        self.tutorial_2 = self.font_tutorial.render("R to reset, M to cycle music", True, (255, 255, 255))
        self.menu_surface.blit(self.tutorial_1, (self.SCREEN_WIDTH / 2 - self.tutorial_1.get_width() / 2, self.SCREEN_HEIGHT / 2))
        self.menu_surface.blit(self.tutorial_2, (self.SCREEN_WIDTH / 2 - self.tutorial_2.get_width() / 2, self.SCREEN_HEIGHT / 2 + self.font_tutorial.get_height() * 1.2))
    
    def render_score(self):
        self.score_surface.fill((0, 0, 0, 0))
        score_text = self.font_score.render(f"Score: {self.score}", True, (255, 255, 255))
        self.score_surface.blit(score_text, (10, 10))
    
    def render_timer(self):
        self.timer_surface.fill((0, 0, 0, 0))
        timer_text = self.font_score.render(f"{round(self.timer, 2):.2f}", True, (255, 255, 255))
        self.timer_surface.blit(timer_text, (self.SCREEN_WIDTH / 2 - timer_text.get_width() / 2, 10))
    
    def load_next_level(self):
        level_name = self.level_names_list_working.pop(0)
        if level_name == "end":
            self.score = 0
            self.timer = 0.0
            self.level_names_list_working = self.level_names_list.copy()
            level_name = self.level_names_list_working.pop(0)
            self.load_level_by_name(level_name)
        else:
            try:
                self.load_level_by_name(level_name)
            except:
                print(f"No level with name {level_name}, loading next level")
                self.load_next_level()

    def load_level_by_name(self, level_name, current_dir=dirname(__file__)):
        if self.debug_level >= 1:
            print(f"Loading level {level_name}")

        if level_name == "main_screen":
            self.load_level(join(current_dir, "assets/levels2/lvl2_0.json"))
            creator_text = self.font.render("FleaRun by g0fher", True, (255, 255, 255))
            self.level_surface.blit(creator_text, (self.SCREEN_WIDTH / 2 - creator_text.get_width() / 2, self.SCREEN_HEIGHT / 5))
        elif level_name == "lvl_1":
            self.load_level(join(current_dir, "assets/levels2/lvl2_1.json"))
        elif level_name == "lvl_2":
            self.load_level(join(current_dir, "assets/levels2/lvl2_2.json"))
        elif level_name == "lvl_3":
            self.load_level(join(current_dir, "assets/levels2/lvl2_3.json"))
        elif level_name == "lvl_4":
            self.load_level(join(current_dir, "assets/levels2/lvl2_4.json"))
        else:
            if self.debug_level >= 1:
                print(f"Level name {level_name} not found")
                return -1                   

    def load_level(self, level_path):
        self.tiles, self.collision_boxes, self.spikes = self.read_json(level_path)
        
        self.where_is_door = (-1, -1)
        self.is_door = False
        self.where_is_heart = (-1, -1)
        self.is_heart = False

        self.render_level()

        # If the render_level function finds either the door or the heart, their positions will be updated
        if self.where_is_door != (-1, -1):
            self.door_rect = pygame.Rect(self.where_is_door[0], self.where_is_door[1], self.tile_size, self.tile_size)
            self.is_door = True
            if self.debug_level >= 2:
                print("Door found")
        if self.where_is_heart != (-1, -1):
            self.heart_rect = pygame.Rect(self.where_is_heart[0], self.where_is_heart[1], self.tile_size, self.tile_size)
            self.is_heart = True
            self.player_position.x = self.where_is_heart[0]
            self.player_position.y = self.where_is_heart[1]
            if self.debug_level >= 2:
                print("Heart found")
    
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

            elif layer['name'] == 'collision':
                for obj in layer['objects']:
                    colliders.append(pygame.Rect(obj['x'] * 2, obj['y'] * 2, obj['width'] * 2, obj['height'] * 2))
            
            elif layer['name'] == 'spikes':
                for obj in layer['objects']:
                    spikes.append(pygame.Rect(obj['x'] * 2, obj['y'] * 2, obj['width'] * 2, obj['height'] * 2))
            
        return tiles, colliders, spikes

    def render_level(self):
        self.level_surface.fill((0, 0, 0, 0))
        level_map = self.tiles
        
        for i in range(len(level_map)):
            for j in range(len(level_map[0])):
                if int(level_map[i][j]) == self.empty_tile_number:
                    continue
                else:
                    if int(level_map[i][j]) == self.door_tile_number:
                        self.where_is_door = (j * self.tile_size, i * self.tile_size)
                    elif int(level_map[i][j]) == self.heart_tile_number:
                        self.where_is_heart = (j * self.tile_size, i * self.tile_size)
                    self.level_surface.blit(
                        self.tilemap_full, 
                        (j * self.tile_size, i * self.tile_size), 
                        (
                            # Tile's column (left to right position) * tile's size in pixels
                            ((int(level_map[i][j]) - 1) % self.tilemap_size[0]) * self.tile_size,
                            # And here tile's row * tile's size in pixels
                            ((int(level_map[i][j]) - 1) // self.tilemap_size[1]) * self.tile_size, 
                            self.tile_size, 
                            self.tile_size
                        )
                    )
    
    def jump(self, should_play_sfx=1):
        # Jump is disabled during the dash
        if not self.is_dashed:
            self.player_velocity.y = -200
            self.is_player_on_ground = False
            self.is_jumped = True
            self.score += 1
            if should_play_sfx:
                self.sfx_jump.play()
            if self.debug_level >= 1:
                print("Jump")

    def dash(self):
        if not self.start_dash_cooldown_timer:
            self.is_dashed = True
            self.is_in_dash = True
            self.enable_gravity = False

            # Uncap maximum horizontal speed to enable dashing.
            # It will be reset once the player's velocity is 0
            self.run_max_speed = 300
            self.friction = 20

            self.player_velocity.y = 0
            self.player_velocity.x = 0
            # This is done to preserve the direction in the dash if the player isn'n moving, 
            # as when idle it fases the camera instead of some direction
            if self.last_direction == 1:
                self.player_velocity.x += self.dash_force
            if self.last_direction == -1:   
                self.player_velocity.x -= self.dash_force
            
            self.start_dash_cooldown_timer = True

            self.sfx_dash.play()
            if self.debug_level >= 1:
                print("Dashed")
    
    def death(self, play_sfx=True):
        if self.is_heart:
            self.player_position.x = self.where_is_heart[0]
            self.player_position.y = self.where_is_heart[1]
        else:
            # The default respawn position if there's no heart is the screen's center
            self.player_position.x = self.screen.get_width() / 2 - self.tile_size / 2
            self.player_position.y = self.screen.get_height() / 2
        
        self.player_velocity.y = 0
        self.player_velocity.x = 0
        self.run_max_speed = self.base_run_max_speed
        self.friction = self.base_friction
        
        self.is_jumped = True
        self.is_player_on_ground = False
        self.is_dashed = False
        self.is_in_dash = False
        self.enable_gravity = True

        self.start_coyote_timer = False
        self.start_coyote_timer_edge = False
        self.start_dash_cooldown_timer = False

        # No death sfx is played as the player enters a door
        # Bassically the death is triggered between the levels
        if play_sfx:
            self.sfx_death.play()
        
        if self.debug_level >= 1:
            print("Death")

    def collision_detection_horizontal(self):
        player_rect = pygame.Rect(self.player_position.x, self.player_position.y, self.tile_size, self.tile_size)
        for collision_box in self.collision_boxes:
            if player_rect.colliderect(collision_box):
                if self.player_velocity.x > 0:
                    self.player_position.x = collision_box.left - self.tile_size
                    self.player_velocity.x = 0
                elif self.player_velocity.x < 0:
                    self.player_position.x = collision_box.right
                    self.player_velocity.x = 0
    
    def collision_detection_vertical(self):
        player_rect = pygame.Rect(self.player_position.x, self.player_position.y, self.tile_size, self.tile_size)
        for collision_box in self.collision_boxes:
            if player_rect.colliderect(collision_box):
                if self.player_velocity.y > 0:
                    self.player_position.y = collision_box.top - self.tile_size
                    self.player_velocity.y = 0
                    self.is_jumped = False
                    self.is_used_double_jump = False
                    self.is_player_on_ground = True
                elif self.player_velocity.y < 0:
                    self.player_position.y = collision_box.bottom
                    self.player_velocity.y = 0
    
    def spikes_collision(self):
        player_rect = pygame.Rect(self.player_position.x, self.player_position.y, self.tile_size, self.tile_size)
        for collision_box in self.spikes:
            if player_rect.colliderect(collision_box):
                self.death()
                if self.debug_level >= 2:
                    print("Collided with spikes")

    def run(self):
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    pygame.mixer.music.stop()
                    pygame.time.wait(500)
                    if self.debug_level >= 1:
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
                            if self.debug_level >= 1:
                                print("Pause")
                            pygame.mixer.music.set_volume(0.05)
                    if event.key == pygame.K_m:
                        self.cycle_music()
                    
                    if not self.is_paused:
                        if event.key == pygame.K_r:
                            self.death()
                        if event.key == pygame.K_j:
                            if self.debug_level >= 1:
                                if self.is_double_jump:
                                    print("turned off wings")
                                else:    
                                    print("turned on wings")
                            self.is_double_jump = not self.is_double_jump
                        if event.key == pygame.K_LSHIFT:
                            # print("shift")
                            if not self.start_dash_cooldown_timer:
                                self.dash()
                        if event.key == pygame.K_SPACE:
                            if not self.is_jumped:
                                # Regular jump
                                if self.is_player_on_ground:
                                    self.jump()
                                # Coyote jump after stepping from an edge. 
                                elif self.start_coyote_timer_edge:
                                    # Essentially, if the player has stepped of an edge, this timer will be initiated, 
                                    # and if the player presses the space while it lasts, the jump will be triggered. 
                                    # This is done to make the gameplay smoother
                                    self.jump()
                                    if self.debug_level >= 1:
                                        print(f"coyote edge, with timer at {self.coyote_time_jump_countdown_edge}")
                                # Jump from using wings after falling
                                elif (not self.is_player_on_ground) and self.is_double_jump and (not self.is_used_double_jump):
                                    self.is_used_double_jump = True
                                    self.jump()
                                    if self.debug_level >= 1:
                                        print("wings down")
                            else:
                                # Wings jump (double jump)
                                if self.is_double_jump and not self.is_used_double_jump:
                                    self.is_used_double_jump = True
                                    self.jump()
                                    if self.debug_level >= 1:
                                        print("wings up (double jump)")
                                else:
                                    # Pressing space in the air with no wings left triggers a coyote timer.
                                    # If the timer is active the moment the player touches the ground again,
                                    # the jump will be triggered
                                    self.start_coyote_timer = True
                    # If paused
                    else:
                        self.pause_menu_action = True
                        self.menu_pressed_confirm = False
                        if event.key == pygame.K_s:
                            if not self.menu_selected_quit:
                                self.menu_selected_resume = False
                                self.menu_selected_quit = True
                                self.sfx_menu.play()
                        elif event.key == pygame.K_w:
                            if not self.menu_selected_resume:
                                self.menu_selected_resume = True
                                self.menu_selected_quit = False
                                self.sfx_menu.play()
                        elif event.key == pygame.K_SPACE:
                            self.menu_pressed_confirm = True
            
            # The code for drawing all the stuff on the screen when paused
            if self.is_paused:
                if self.pause_menu_action:
                    self.menu_select_surface.fill((0, 0, 0, 0))

                    if self.menu_pressed_confirm:
                        if self.menu_selected_resume:
                            self.is_paused = False
                            self.sfx_menu_select.play()
                            pygame.mixer.music.set_volume(0.2)
                            if self.debug_level >= 1:
                                print("Unpause")
                        elif self.menu_selected_quit:
                            self.is_running = False
                            self.sfx_quit.play()
                            pygame.mixer.music.stop()
                            # this delay is for the quit sfx to play
                            pygame.time.wait(250)
                            if self.debug_level >= 1:
                                print("Shut down.")
                    else:
                        if self.menu_selected_resume:
                            self.menu_select_surface.blit(
                                self.misc_sprite_menu_select, 
                                (self.SCREEN_WIDTH / 2 - self.resume.get_width() / 2 - 64, self.SCREEN_HEIGHT / 5 + self.resume.get_height() * 0.2)
                            )
                        elif self.menu_selected_quit:
                            self.menu_select_surface.blit(
                                self.misc_sprite_menu_select, 
                                (self.SCREEN_WIDTH / 2 - self.resume.get_width() / 2 - 64, self.SCREEN_HEIGHT / 5 + self.resume.get_height() * 0.2 + self.font_menu.get_height() * 1.2)
                            )

                    self.screen.fill((0, 0, 0))
                    self.screen.blit(self.level_surface, (0, 0))
                    self.screen.blit(self.player_surface, (0, 0))
                    self.screen.blit(self.menu_surface, (0, 0))
                    self.screen.blit(self.menu_select_surface, (0, 0))
                    self.pause_menu_action = False

            # And this will be ran when not paused
            else:
                self.is_player_moving = bool(abs(self.player_velocity.x))

                ### Select characher sprite for this frame
                if self.is_player_moving:
                    # Display sprite: run
                    if self.is_player_on_ground:
                        # increase the counter and mod it so it loops back to zero
                        self.sprite_frame_delay_counter_run = (self.sprite_frame_delay_counter_run + 1) % self.sprite_frame_delay_run
                        # Delay counter is at zero, this frame the run sprite will be updated
                        if self.sprite_frame_delay_counter_run == 0:
                            self.sprite_surface.fill((0, 0, 0, 0))
                            # Here the difference between two blits is the height offset. In the running animation tileset
                            # there are two sets of sprites, one below another, one facing right and the other one left
                            if self.player_velocity.x > 0:
                                self.sprite_surface.blit(
                                    self.player_tileset_run, 
                                    (0, 0), 
                                    (self.tile_size * self.sprite_counter_run, 0, self.tile_size, self.tile_size)
                                )
                            else:
                                self.sprite_surface.blit(
                                    self.player_tileset_run, 
                                    (0, 0), 
                                    (self.tile_size * self.sprite_counter_run, self.tile_size, self.tile_size, self.tile_size)
                                )
                            
                            self.sprite_counter_run = (self.sprite_counter_run + 1) % self.number_of_sprites_run
                    # Display sprite: jump moving
                    else:
                        self.sprite_surface.fill((0, 0, 0, 0))
                        if self.player_velocity.x > 0:
                            self.sprite_surface.blit(self.player_sprite_jump_moving, (0, 0))
                        else:
                            self.sprite_surface.blit(self.player_sprite_jump_moving_flipped, (0, 0))
                        self.sprite_frame_delay_counter_run = 0
                        self.sprite_counter_run = 0
                    
                    self.sprite_frame_delay_counter_idle = 0
                    self.sprite_counter_idle = 0
                
                # Player not moving
                else:
                    # Display sprite: idle
                    if self.is_player_on_ground:
                        self.sprite_frame_delay_counter_idle = (self.sprite_frame_delay_counter_idle + 1) % self.sprite_frame_delay_idle
                        if self.sprite_frame_delay_counter_idle == 0:
                            self.sprite_surface.fill((0, 0, 0, 0))
                            self.sprite_surface.blit(
                                self.player_tileset_idle, 
                                (0, 0), 
                                (self.sprite_counter_idle * self.tile_size, 0, self.tile_size, self.tile_size)
                            )
                            self.sprite_counter_idle = (self.sprite_counter_idle + 1) % self.number_of_sprites_idle
                    # Display sprite: jump static
                    else:
                        self.sprite_surface.fill((0, 0, 0, 0))
                        self.sprite_surface.blit(self.player_sprite_jump_static, (0, 0))
                        self.sprite_frame_delay_counter_idle = 0
                        self.sprite_counter_idle = 0

                    self.sprite_frame_delay_counter_run = 0
                    self.sprite_counter_run = 0
                    
                ### Coyote time on landing
                if self.start_coyote_timer:
                    if self.is_player_on_ground:
                        if self.debug_level >= 1:
                            print(f"coyote landing, with timer at {self.coyote_time_jump_countdown}")                            
                        self.jump()
                        self.start_coyote_timer = False
                        self.coyote_time_jump_countdown = self.coyote_time_jump_nof_frames
                    else:
                        # Decrease the timer if the player is still airborne, once it runs out, disable and reset it
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
                        self.is_dashed = False
                        self.start_dash_cooldown_timer = False
                        self.dash_cooldown_countdown = self.dash_cooldown_nof_frames
                        if self.debug_level >= 2:
                            print("Dash restored")

                # Get input keys
                keys = pygame.key.get_pressed()

                if not self.is_in_dash:
                    if keys[pygame.K_a]:
                        if self.player_velocity.x > -self.run_max_speed:
                            self.player_velocity.x -= self.run_speed
                    elif keys[pygame.K_d]:
                        if self.player_velocity.x < self.run_max_speed:
                            self.player_velocity.x += self.run_speed
               
                    # Apply friction if the player is moving without any movement keys pressed
                    else:
                        if self.player_velocity.x > 0:
                            self.player_velocity.x -= self.friction
                            if self.player_velocity.x < 0:
                                self.player_velocity.x = 0
                        elif self.player_velocity.x < 0:
                            self.player_velocity.x += self.friction
                            if self.player_velocity.x > 0:
                                self.player_velocity.x = 0
                
                else:
                    # Yes it's the same code
                    if self.player_velocity.x > 0:
                        self.player_velocity.x -= self.friction
                        if self.player_velocity.x < 0:
                            self.player_velocity.x = 0
                    elif self.player_velocity.x < 0:
                        self.player_velocity.x += self.friction
                        if self.player_velocity.x > 0:
                            self.player_velocity.x = 0
                    if self.debug_level >= 2:
                        print("input was blocked (in dash)")

                # Limit velocity
                if self.player_velocity.x > self.run_max_speed:
                    self.player_velocity.x = self.run_max_speed
                elif self.player_velocity.x < -self.run_max_speed:
                    self.player_velocity.x = -self.run_max_speed
                
                # Apply horizontal velocity to change the X position
                self.player_position.x += self.player_velocity.x * self.dt * 10

                if self.player_velocity.x > 0:
                    self.last_direction = 1
                elif self.player_velocity.x < 0:
                    self.last_direction = -1

                # This happens when the player was stopped by friction after the dash
                if self.is_in_dash and self.player_velocity.x == 0:
                    self.enable_gravity = True
                    self.is_dashed = False
                    self.is_in_dash = False
                    self.run_max_speed = self.base_run_max_speed
                    self.friction = self.base_friction
                    if self.debug_level >= 2:
                        print("Gravity on after dash")

                self.collision_detection_horizontal()

                # Apply gravity
                if self.enable_gravity:
                    # The player must always fall first, and then be lifted up again
                    # If it's not done, the game can't detect when he stepped of the platform
                    self.is_player_on_ground = False
                    self.player_velocity.y += self.gravity_force
                    # Limit fall velocity
                    if self.player_velocity.y >= self.terminal_velocity:
                        self.player_velocity.y = self.terminal_velocity
                
                # Apply vertical velocity to change the Y position
                self.player_position.y += self.player_velocity.y * self.dt * 10

                self.collision_detection_vertical()

                # This happens when the player has just stepped of the platform
                if self.previous_is_player_on_ground and not self.is_player_on_ground:
                    self.start_coyote_timer_edge = True
                self.previous_is_player_on_ground = self.is_player_on_ground

                self.spikes_collision()          
                    
                player_rect = pygame.Rect(self.player_position.x, self.player_position.y, self.tile_size, self.tile_size)
                if self.is_door:
                    if player_rect.colliderect(self.door_rect):
                        self.load_next_level()
                        self.death(play_sfx=False)
                        self.sfx_next_level.play()
                        if self.debug_level >= 2:
                            print("Collided with the door")

                # Prevent player from going offscreen
                if self.player_position.y > self.SCREEN_HEIGHT or self.player_position.y < 0 or self.player_position.x > self.SCREEN_WIDTH or self.player_position.x < 0 - 32:
                    self.death()

                self.screen.fill((0, 0, 0, 0))

                # Draw the player (the correct sprite is already drawn on the sprite surface)
                self.player_surface.fill((0, 0, 0, 0))
                self.player_surface.blit(self.sprite_surface, self.player_position)

                self.screen.blit(self.level_surface, (0, 0))
                self.screen.blit(self.player_surface, (0, 0))

                self.render_score()
                self.screen.blit(self.score_surface, (0, 0))

                self.timer += self.dt
                self.render_timer()
                self.screen.blit(self.timer_surface, (0, 0))

            pygame.display.update()

            # Get time between frames in seconds & fix fps to target fps
            self.dt = self.clock.tick(self.TARGET_FPS) / 1000

        pygame.quit()

if __name__ == "__main__":
    Game().run()
    sys.exit()
