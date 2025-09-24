import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
DARK_RED = (139, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
LIGHT_GREEN = (144, 238, 144)

# Player constants
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 5
JUMP_STRENGTH = -15
GRAVITY = 0.8
GROUND_Y = SCREEN_HEIGHT - 100

# Bullet constants
BULLET_WIDTH = 10
BULLET_HEIGHT = 5
BULLET_SPEED = 7

# Enemy constants
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 60

# Player health constants
MAX_HEALTH = 100
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
DAMAGE_PER_HIT = 25


def load_sound_effect(filename):
    """Load a sound effect from file with error handling"""
    try:
        sound = pygame.mixer.Sound(filename)
        return sound
    except pygame.error as e:
        print(f"Could not load sound {filename}: {e}")
        # Return a silent sound as fallback
        return pygame.mixer.Sound(buffer=b'\x00\x00' * 1000)


def create_simple_beep(frequency=440, duration=0.1):
    """Create a simple beep for background music fallback"""
    # Create a simple sound buffer with basic wave pattern
    sample_rate = 22050
    frames = int(duration * sample_rate)
    
    # Create alternating high/low pattern for beep effect
    sound_data = bytearray()
    for i in range(frames):
        # Simple square wave approximation
        wave_cycle = i % int(sample_rate / frequency)
        if wave_cycle < int(sample_rate / frequency / 2):
            sound_data.extend([127, 0])  # High
        else:
            sound_data.extend([0, 127])  # Low
    
    return pygame.mixer.Sound(buffer=bytes(sound_data))


def create_music_track():
    """Create a simple background music loop"""
    # Create a longer, softer beep for background
    return create_simple_beep(220, 2.0)  # Low A note for 2 seconds


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vel_y = 0
        self.on_ground = False
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Health system
        self.health = MAX_HEALTH
        self.max_health = MAX_HEALTH
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.hit_flash = False
        
        # Animation properties
        self.animation_timer = 0
        self.blink_timer = 0
        self.is_blinking = False
        
        # Movement animation
        self.bob_offset = 0
        self.facing_right = True
    
    def update(self):
        # Handle gravity
        if not self.on_ground:
            self.vel_y += GRAVITY
        
        # Update position
        self.y += self.vel_y
        
        # Check if player hits the ground
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Handle invulnerability frames
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.hit_flash = False
        
        # Update animations
        self.animation_timer += 1
        self.blink_timer += 1
        
        # Bobbing animation when on ground
        if self.on_ground:
            self.bob_offset = math.sin(self.animation_timer * 0.1) * 2
        
        # Random blinking
        if self.blink_timer > 120:  # Blink every 2 seconds
            if random.random() < 0.1:  # 10% chance to blink
                self.is_blinking = True
                self.blink_timer = 0
        
        if self.is_blinking and self.blink_timer > 10:  # Blink duration
            self.is_blinking = False
        
        # Update rect for collision detection
        self.rect.x = self.x
        self.rect.y = self.y
    
    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
    
    def move_left(self):
        if self.x > 0:
            self.x -= PLAYER_SPEED
            self.facing_right = False
    
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += PLAYER_SPEED
            self.facing_right = True
    
    def take_damage(self, damage):
        """Handle player taking damage"""
        if not self.invulnerable:
            self.health -= damage
            self.invulnerable = True
            self.invulnerable_timer = 60  # 1 second of invulnerability at 60 FPS
            self.hit_flash = True
            if self.health < 0:
                self.health = 0
            return True
        return False
    
    def draw(self, screen):
        draw_y = self.y + self.bob_offset
        
        # Flashing effect when hit
        if self.hit_flash and (self.invulnerable_timer // 5) % 2:
            return  # Skip drawing to create flashing effect
        
        # Draw shadow
        shadow_y = GROUND_Y - 5
        pygame.draw.ellipse(screen, GRAY, (self.x + 5, shadow_y, self.width - 10, 8))
        
        # Draw body (main rectangle with rounded corners effect)
        body_rect = pygame.Rect(self.x, draw_y, self.width, self.height)
        body_color = DARK_RED if self.hit_flash else DARK_BLUE
        inner_color = RED if self.hit_flash else BLUE
        pygame.draw.rect(screen, body_color, body_rect)
        pygame.draw.rect(screen, inner_color, (self.x + 2, draw_y + 2, self.width - 4, self.height - 4))
        
        # Draw belt
        pygame.draw.rect(screen, BROWN, (self.x, draw_y + self.height // 2 - 3, self.width, 6))
        
        # Draw arms
        arm_color = LIGHT_BLUE if not self.on_ground else BLUE
        pygame.draw.circle(screen, arm_color, (self.x - 5, draw_y + 20), 8)
        pygame.draw.circle(screen, arm_color, (self.x + self.width + 5, draw_y + 20), 8)
        
        # Draw legs
        leg_width = 8
        leg_height = 15
        # Left leg
        pygame.draw.rect(screen, DARK_BLUE, (self.x + 8, draw_y + self.height - 2, leg_width, leg_height))
        # Right leg
        pygame.draw.rect(screen, DARK_BLUE, (self.x + 24, draw_y + self.height - 2, leg_width, leg_height))
        
        # Draw feet
        pygame.draw.ellipse(screen, BLACK, (self.x + 6, draw_y + self.height + 10, 12, 6))
        pygame.draw.ellipse(screen, BLACK, (self.x + 22, draw_y + self.height + 10, 12, 6))
        
        # Draw head (larger circle)
        head_x = self.x + self.width // 2
        head_y = draw_y - 10
        pygame.draw.circle(screen, PINK, (head_x, head_y), 15)
        pygame.draw.circle(screen, LIGHT_BLUE, (head_x, head_y), 13)
        
        # Draw hair
        hair_points = [
            (head_x - 12, head_y - 8),
            (head_x - 8, head_y - 15),
            (head_x - 2, head_y - 12),
            (head_x + 2, head_y - 15),
            (head_x + 8, head_y - 12),
            (head_x + 12, head_y - 8)
        ]
        pygame.draw.polygon(screen, BROWN, hair_points)
        
        # Draw eyes
        eye_color = WHITE if not self.is_blinking else LIGHT_BLUE
        if self.facing_right:
            pygame.draw.circle(screen, eye_color, (head_x - 5, head_y - 2), 3)
            pygame.draw.circle(screen, eye_color, (head_x + 5, head_y - 2), 3)
            if not self.is_blinking:
                pygame.draw.circle(screen, BLACK, (head_x - 4, head_y - 2), 2)
                pygame.draw.circle(screen, BLACK, (head_x + 6, head_y - 2), 2)
        else:
            pygame.draw.circle(screen, eye_color, (head_x - 5, head_y - 2), 3)
            pygame.draw.circle(screen, eye_color, (head_x + 5, head_y - 2), 3)
            if not self.is_blinking:
                pygame.draw.circle(screen, BLACK, (head_x - 6, head_y - 2), 2)
                pygame.draw.circle(screen, BLACK, (head_x + 4, head_y - 2), 2)
        
        # Draw mouth
        if self.on_ground:
            # Happy mouth
            pygame.draw.arc(screen, BLACK, (head_x - 6, head_y + 2, 12, 8), 0, math.pi, 2)
        else:
            # Surprised mouth (jumping)
            pygame.draw.circle(screen, BLACK, (head_x, head_y + 5), 2)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.shoot_timer = 0
        self.shoot_delay = 90  # Frames between shots
        
        # Animation properties
        self.animation_timer = 0
        self.eye_glow = 0
        self.breathing_offset = 0
        self.charging_shot = False
        self.charge_timer = 0
        
    def update(self):
        self.shoot_timer += 1
        self.animation_timer += 1
        
        # Breathing animation
        self.breathing_offset = math.sin(self.animation_timer * 0.05) * 3
        
        # Eye glow effect
        self.eye_glow = (math.sin(self.animation_timer * 0.1) + 1) * 0.5
        
        # Charging shot animation
        if self.shoot_timer >= self.shoot_delay - 30:
            self.charging_shot = True
            self.charge_timer += 1
        else:
            self.charging_shot = False
            self.charge_timer = 0
        
    def should_shoot(self):
        if self.shoot_timer >= self.shoot_delay:
            self.shoot_timer = 0
            return True
        return False
    
    def draw(self, screen):
        draw_y = self.y + self.breathing_offset
        
        # Draw shadow
        shadow_y = GROUND_Y - 5
        pygame.draw.ellipse(screen, GRAY, (self.x + 5, shadow_y, self.width - 10, 8))
        
        # Draw spikes on back (menacing look)
        spike_points = []
        for i in range(5):
            spike_x = self.x + self.width + (i * 4)
            spike_y = draw_y + 10 + (i * 8)
            spike_points.extend([
                (spike_x, spike_y),
                (spike_x + 8, spike_y + 4),
                (spike_x, spike_y + 8)
            ])
        
        for i in range(0, len(spike_points), 3):
            if i + 2 < len(spike_points):
                pygame.draw.polygon(screen, DARK_RED, spike_points[i:i+3])
        
        # Draw main body with armor-like segments
        body_rect = pygame.Rect(self.x, draw_y, self.width, self.height)
        pygame.draw.rect(screen, DARK_RED, body_rect)
        pygame.draw.rect(screen, RED, (self.x + 3, draw_y + 3, self.width - 6, self.height - 6))
        
        # Draw armor segments
        for i in range(3):
            segment_y = draw_y + 10 + (i * 15)
            pygame.draw.rect(screen, DARK_RED, (self.x + 5, segment_y, self.width - 10, 3))
        
        # Draw claws/arms
        claw_color = ORANGE if self.charging_shot else DARK_RED
        # Left claw
        claw_points_left = [
            (self.x - 10, draw_y + 15),
            (self.x - 20, draw_y + 10),
            (self.x - 15, draw_y + 20),
            (self.x - 18, draw_y + 25),
            (self.x - 5, draw_y + 22)
        ]
        pygame.draw.polygon(screen, claw_color, claw_points_left)
        
        # Draw cannon arm (right side)
        cannon_width = 15
        cannon_height = 8
        cannon_x = self.x - cannon_width
        cannon_y = draw_y + self.height // 2 - cannon_height // 2
        pygame.draw.rect(screen, GRAY, (cannon_x, cannon_y, cannon_width, cannon_height))
        
        # Cannon muzzle
        muzzle_color = YELLOW if self.charging_shot else GRAY
        pygame.draw.circle(screen, muzzle_color, (cannon_x, cannon_y + cannon_height // 2), 4)
        
        # Charging effect
        if self.charging_shot:
            charge_intensity = self.charge_timer / 30.0
            charge_size = int(6 + charge_intensity * 10)
            pygame.draw.circle(screen, YELLOW, (cannon_x, cannon_y + cannon_height // 2), charge_size, 2)
            pygame.draw.circle(screen, ORANGE, (cannon_x, cannon_y + cannon_height // 2), charge_size - 2, 1)
        
        # Draw legs with mechanical joints
        leg_width = 12
        leg_height = 18
        # Left leg
        pygame.draw.rect(screen, DARK_RED, (self.x + 8, draw_y + self.height - 2, leg_width, leg_height))
        pygame.draw.circle(screen, GRAY, (self.x + 14, draw_y + self.height + 8), 3)  # joint
        # Right leg
        pygame.draw.rect(screen, DARK_RED, (self.x + 30, draw_y + self.height - 2, leg_width, leg_height))
        pygame.draw.circle(screen, GRAY, (self.x + 36, draw_y + self.height + 8), 3)  # joint
        
        # Draw mechanical feet
        pygame.draw.rect(screen, BLACK, (self.x + 6, draw_y + self.height + 14, 16, 4))
        pygame.draw.rect(screen, BLACK, (self.x + 28, draw_y + self.height + 14, 16, 4))
        
        # Draw head (robotic/helmet style)
        head_x = self.x + self.width // 2
        head_y = draw_y - 12
        
        # Helmet outline
        pygame.draw.circle(screen, BLACK, (head_x, head_y), 18)
        pygame.draw.circle(screen, DARK_RED, (head_x, head_y), 16)
        pygame.draw.circle(screen, RED, (head_x, head_y), 14)
        
        # Helmet details
        pygame.draw.rect(screen, BLACK, (head_x - 12, head_y - 8, 24, 3))
        pygame.draw.rect(screen, GRAY, (head_x - 10, head_y - 7, 20, 1))
        
        # Glowing evil eyes
        eye_base_color = (255, int(255 * self.eye_glow), 0)  # Yellow to orange glow
        eye_outer_color = (255, int(200 * self.eye_glow), 0)
        
        # Left eye
        pygame.draw.circle(screen, eye_base_color, (head_x - 6, head_y - 2), 5)
        pygame.draw.circle(screen, eye_outer_color, (head_x - 6, head_y - 2), 3)
        pygame.draw.circle(screen, RED, (head_x - 6, head_y - 2), 1)
        
        # Right eye
        pygame.draw.circle(screen, eye_base_color, (head_x + 6, head_y - 2), 5)
        pygame.draw.circle(screen, eye_outer_color, (head_x + 6, head_y - 2), 3)
        pygame.draw.circle(screen, RED, (head_x + 6, head_y - 2), 1)
        
        # Menacing mouth/vent
        mouth_points = [
            (head_x - 8, head_y + 6),
            (head_x + 8, head_y + 6),
            (head_x + 6, head_y + 10),
            (head_x - 6, head_y + 10)
        ]
        pygame.draw.polygon(screen, BLACK, mouth_points)
        
        # Antenna/horns
        pygame.draw.polygon(screen, DARK_RED, [
            (head_x - 12, head_y - 12),
            (head_x - 16, head_y - 20),
            (head_x - 8, head_y - 15)
        ])
        pygame.draw.polygon(screen, DARK_RED, [
            (head_x + 12, head_y - 12),
            (head_x + 16, head_y - 20),
            (head_x + 8, head_y - 15)
        ])


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.trail_positions = []  # For bullet trail effect
        self.glow_timer = 0
    
    def update(self):
        # Add current position to trail
        self.trail_positions.append((self.x + self.width//2, self.y + self.height//2))
        
        # Keep only last 8 positions for trail
        if len(self.trail_positions) > 8:
            self.trail_positions.pop(0)
        
        self.x -= BULLET_SPEED
        self.rect.x = self.x
        self.glow_timer += 1
    
    def is_off_screen(self):
        return self.x < -self.width
    
    def draw(self, screen):
        # Draw trail effect
        for i, pos in enumerate(self.trail_positions[:-1]):
            alpha = (i + 1) / len(self.trail_positions)  # Fade effect
            trail_size = int(2 + alpha * 3)
            trail_color = (255, int(255 * alpha), int(100 * alpha))  # Yellow to orange fade
            pygame.draw.circle(screen, trail_color, pos, trail_size)
        
        # Draw main bullet with glow effect
        glow_intensity = (math.sin(self.glow_timer * 0.3) + 1) * 0.5
        
        # Outer glow
        glow_size = int(8 + glow_intensity * 4)
        glow_color = (255, int(200 + glow_intensity * 55), int(glow_intensity * 100))
        pygame.draw.circle(screen, glow_color, (self.x + self.width//2, self.y + self.height//2), glow_size, 2)
        
        # Inner bullet core
        pygame.draw.ellipse(screen, YELLOW, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, WHITE, (self.x + 1, self.y + 1, self.width - 2, self.height - 2))
        
        # Bullet tip effect
        tip_color = (255, 255, 200)
        pygame.draw.circle(screen, tip_color, (self.x + self.width//2, self.y + self.height//2), 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bullet Dodge Game")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player = Player(50, GROUND_Y - PLAYER_HEIGHT)
        self.enemy = Enemy(SCREEN_WIDTH - 80, GROUND_Y - ENEMY_HEIGHT)
        self.bullets = []
        
        # Game state
        self.score = 0
        self.game_over = False
        self.game_started = False
        
        # Sound effects
        self.shoot_sound = create_sound_effect(800, 0.1, 0.3)  # High pitched shoot sound
        self.hit_sound = create_sound_effect(200, 0.2, 0.4)    # Lower pitched hit sound
        
        # Background music
        self.background_music = create_music_track()
        self.music_playing = False
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
    
    def start_background_music(self):
        """Start playing background music at 20% volume"""
        if not self.music_playing:
            # Set volume to 20% of normal volume
            self.background_music.set_volume(0.2)
            # Play the music on loop (-1 means infinite loop)
            pygame.mixer.Sound.play(self.background_music, loops=-1)
            self.music_playing = True
    
    def stop_background_music(self):
        """Stop background music"""
        pygame.mixer.stop()
        self.music_playing = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if not self.game_started and event.key == pygame.K_SPACE:
                    self.game_started = True
                    self.start_background_music()
                elif self.game_over and event.key == pygame.K_r:
                    self.restart_game()
                elif self.game_started and not self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
        
        return True
    
    def handle_input(self):
        if not self.game_started or self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
    
    def update(self):
        if not self.game_started or self.game_over:
            return
        
        # Update player
        self.player.update()
        
        # Update enemy
        self.enemy.update()
        
        # Enemy shooting
        if self.enemy.should_shoot():
            bullet_x = self.enemy.x
            bullet_y = self.enemy.y + self.enemy.height // 2
            self.bullets.append(Bullet(bullet_x, bullet_y))
            # Play shoot sound effect
            self.shoot_sound.play()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        # Check collisions
        for bullet in self.bullets[:]:
            if self.player.rect.colliderect(bullet.rect):
                if self.player.take_damage(DAMAGE_PER_HIT):
                    self.hit_sound.play()
                self.bullets.remove(bullet)
        
        # Check if player is dead
        if self.player.health <= 0:
            self.game_over = True
            self.stop_background_music()
        
        # Increase score
        self.score += 1
        
        # Increase difficulty over time
        if self.score % 300 == 0 and self.enemy.shoot_delay > 30:
            self.enemy.shoot_delay -= 5
    
    def draw(self):
        # Draw gradient background
        for y in range(SCREEN_HEIGHT):
            color_intensity = y / SCREEN_HEIGHT
            sky_color = (
                int(135 + color_intensity * 120),  # Light blue to white
                int(206 + color_intensity * 49),
                int(235 + color_intensity * 20)
            )
            pygame.draw.line(self.screen, sky_color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw ground with texture
        pygame.draw.rect(self.screen, LIGHT_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        pygame.draw.rect(self.screen, GREEN, (0, GROUND_Y, SCREEN_WIDTH, 10))  # Grass line
        
        # Draw some ground details
        for i in range(0, SCREEN_WIDTH, 40):
            # Small grass tufts
            pygame.draw.line(self.screen, GREEN, (i + 5, GROUND_Y), (i + 8, GROUND_Y - 3), 2)
            pygame.draw.line(self.screen, GREEN, (i + 15, GROUND_Y), (i + 18, GROUND_Y - 4), 2)
            pygame.draw.line(self.screen, GREEN, (i + 25, GROUND_Y), (i + 28, GROUND_Y - 2), 2)
        
        if not self.game_started:
            # Start screen
            title_text = self.big_font.render("BULLET DODGE", True, BLACK)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(title_text, title_rect)
            
            instruction_text = self.font.render("Press SPACE to start", True, BLACK)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(instruction_text, instruction_rect)
            
            controls_text = self.font.render("Controls: SPACE = Jump, A/D or Arrow Keys = Move", True, BLACK)
            controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(controls_text, controls_rect)
            
        elif self.game_over:
            # Game over screen
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, game_over_rect)
            
            score_text = self.font.render(f"Final Score: {self.score}", True, BLACK)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.font.render("Press R to restart", True, BLACK)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)
            
        else:
            # Game playing
            self.player.draw(self.screen)
            self.enemy.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, BLACK)
            self.screen.blit(score_text, (10, 10))
            
            # Draw health bar
            self.draw_health_bar()
        
        pygame.display.flip()
    
    def draw_health_bar(self):
        """Draw the player's health bar"""
        # Health bar position (top right area)
        health_bar_x = SCREEN_WIDTH - HEALTH_BAR_WIDTH - 20
        health_bar_y = 15
        
        # Calculate health percentage
        health_percentage = self.player.health / self.player.max_health
        current_health_width = int(HEALTH_BAR_WIDTH * health_percentage)
        
        # Health bar background (black border)
        pygame.draw.rect(self.screen, BLACK, 
                        (health_bar_x - 2, health_bar_y - 2, 
                         HEALTH_BAR_WIDTH + 4, HEALTH_BAR_HEIGHT + 4))
        
        # Health bar background (gray)
        pygame.draw.rect(self.screen, GRAY, 
                        (health_bar_x, health_bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        
        # Health bar fill (color changes based on health level)
        if health_percentage > 0.6:
            health_color = GREEN
        elif health_percentage > 0.3:
            health_color = YELLOW
        else:
            health_color = RED
        
        if current_health_width > 0:
            pygame.draw.rect(self.screen, health_color, 
                            (health_bar_x, health_bar_y, current_health_width, HEALTH_BAR_HEIGHT))
        
        # Health text label
        health_text = self.font.render("Health", True, BLACK)
        self.screen.blit(health_text, (health_bar_x, health_bar_y - 25))
        
        # Health value text
        health_value_text = self.font.render(f"{self.player.health}/{self.player.max_health}", True, BLACK)
        self.screen.blit(health_value_text, (health_bar_x, health_bar_y + HEALTH_BAR_HEIGHT + 5))
    
    def restart_game(self):
        self.player = Player(50, GROUND_Y - PLAYER_HEIGHT)
        self.enemy = Enemy(SCREEN_WIDTH - 80, GROUND_Y - ENEMY_HEIGHT)
        self.bullets = []
        self.score = 0
        self.game_over = False
        self.game_started = True
        self.start_background_music()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
    
