import pygame
import random
import array  # Added for sound generation
import math   # Added for sound generation

# Initialize Pygame
pygame.init()

# --- Sound Engine Setup (No Media Files) ---
SOUND_ENABLED = False
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    SOUND_ENABLED = True
except pygame.error as e:
    print(f"Warning: Pygame mixer could not be initialized. Sound will be disabled. Error: {e}")
    SOUND_ENABLED = False

def generate_square_wave_bytes(freq_hz, duration_ms, volume=0.1, sample_rate=22050):
    if not SOUND_ENABLED or duration_ms <= 0:
        return b''
    num_samples = int(sample_rate * duration_ms / 1000.0)
    if num_samples == 0:
        return b''
    wave_data = array.array('h')
    max_amplitude = int(32767 * max(0.0, min(1.0, volume)))
    if freq_hz <= 0:
        for _ in range(num_samples):
            wave_data.append(0)
        return wave_data.tobytes()
    samples_per_cycle = float(sample_rate) / freq_hz
    half_cycle_samples = samples_per_cycle / 2.0
    for i in range(num_samples):
        if (i % samples_per_cycle) < half_cycle_samples:
            sample = max_amplitude
        else:
            sample = -max_amplitude
        wave_data.append(sample)
    return wave_data.tobytes()

class DummySound:
    def play(self):
        pass

if SOUND_ENABLED:
    paddle_hit_sound_bytes = generate_square_wave_bytes(freq_hz=880, duration_ms=40, volume=0.07)
    paddle_hit_sound = pygame.mixer.Sound(buffer=paddle_hit_sound_bytes) if paddle_hit_sound_bytes else DummySound()
    wall_hit_sound_bytes = generate_square_wave_bytes(freq_hz=659, duration_ms=40, volume=0.07)
    wall_hit_sound = pygame.mixer.Sound(buffer=wall_hit_sound_bytes) if wall_hit_sound_bytes else DummySound()
    score_sound_bytes = generate_square_wave_bytes(freq_hz=1047, duration_ms=120, volume=0.09)
    score_sound = pygame.mixer.Sound(buffer=score_sound_bytes) if score_sound_bytes else DummySound()
else:
    paddle_hit_sound = DummySound()
    wall_hit_sound = DummySound()
    score_sound = DummySound()

# --- Constants ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 15
PADDLE_SPEED = 7
BALL_SPEED_X_INITIAL = 5
BALL_SPEED_Y_INITIAL = 5
WINNING_SCORE = 5

# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Purrfect Pong! Meow!")
clock = pygame.time.Clock()

# --- Fonts ---
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)
font_smaller = pygame.font.Font(None, 28)
font_tiny = pygame.font.Font(None, 24)

# --- Game Objects ---
# Player 1 (left paddle)
player1_paddle = pygame.Rect(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
player1_score = 0
player1_color = BLUE

# Player 2 (right paddle)
player2_paddle = pygame.Rect(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
player2_score = 0
player2_color = RED

# Ball
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_speed_x, ball_speed_y = (0,0) # Initialized by reset_match_state
ball_color = WHITE # Added this line

# --- Game States ---
GAME_START = 0
GAME_PLAYING = 1
GAME_OVER = 2
GAME_PAUSED = 3
CONFIRM_RESTART_FROM_PAUSE = 4
CONFIRM_MAIN_MENU_FROM_PAUSE = 5
game_state = GAME_START
winner = ""

# --- Helper Functions ---
def draw_paddle(surface, color, rect):
    pygame.draw.rect(surface, color, rect)

def draw_ball(surface, color, rect):
    pygame.draw.ellipse(surface, color, rect)

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def draw_net(surface, color, width, height):
    for i in range(0, height, 15):
        pygame.draw.rect(surface, color, (width // 2 - 1, i, 2, 10))

def reset_ball_position_and_speed():
    global ball_speed_x, ball_speed_y
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    direction_x = random.choice([-1, 1])
    direction_y = random.choice([-1, 1])
    ball_speed_x = BALL_SPEED_X_INITIAL * direction_x
    ball_speed_y = BALL_SPEED_Y_INITIAL * direction_y
    return ball_speed_x, ball_speed_y


def reset_match_state():
    global player1_score, player2_score, ball_speed_x, ball_speed_y, winner
    player1_score = 0
    player2_score = 0
    ball_speed_x, ball_speed_y = reset_ball_position_and_speed()
    player1_paddle.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
    player2_paddle.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
    player1_paddle.x = 50
    player2_paddle.x = SCREEN_WIDTH - 50 - PADDLE_WIDTH
    winner = ""

reset_match_state() # Initialize ball speed and other states at the very beginning

# --- Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == GAME_START:
                if event.key == pygame.K_SPACE:
                    reset_match_state()
                    game_state = GAME_PLAYING
                elif event.key == pygame.K_ESCAPE: # Option to quit from start screen
                    running = False
            
            elif game_state == GAME_PLAYING:
                if event.key == pygame.K_ESCAPE:
                    game_state = GAME_PAUSED
            
            elif game_state == GAME_PAUSED:
                if event.key == pygame.K_SPACE:
                    game_state = GAME_PLAYING
                elif event.key == pygame.K_r:
                    game_state = CONFIRM_RESTART_FROM_PAUSE
                elif event.key == pygame.K_m:
                    game_state = CONFIRM_MAIN_MENU_FROM_PAUSE
                elif event.key == pygame.K_q:
                    running = False
            
            elif game_state == CONFIRM_RESTART_FROM_PAUSE:
                if event.key == pygame.K_y:
                    reset_match_state()
                    game_state = GAME_PLAYING
                elif event.key == pygame.K_n:
                    game_state = GAME_PAUSED
            
            elif game_state == CONFIRM_MAIN_MENU_FROM_PAUSE:
                if event.key == pygame.K_y:
                    reset_match_state() # Reset score for new game from main menu
                    game_state = GAME_START
                elif event.key == pygame.K_n:
                    game_state = GAME_PAUSED

            elif game_state == GAME_OVER:
                if event.key == pygame.K_y:
                    reset_match_state()
                    game_state = GAME_PLAYING
                elif event.key == pygame.K_m:
                    reset_match_state() # Reset for main menu
                    game_state = GAME_START
                elif event.key == pygame.K_n:
                    running = False

    if game_state == GAME_PLAYING:
        # --- Player Input ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player1_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s]:
            player1_paddle.y += PADDLE_SPEED
        if keys[pygame.K_UP]:
            player2_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN]:
            player2_paddle.y += PADDLE_SPEED

        # Keep paddles on screen
        player1_paddle.top = max(0, player1_paddle.top)
        player1_paddle.bottom = min(SCREEN_HEIGHT, player1_paddle.bottom)
        player2_paddle.top = max(0, player2_paddle.top)
        player2_paddle.bottom = min(SCREEN_HEIGHT, player2_paddle.bottom)

        # --- Ball Movement ---
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball collision with top/bottom walls
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball_speed_y *= -1
            wall_hit_sound.play()

        # Ball collision with paddles
        collided_p1 = ball.colliderect(player1_paddle)
        collided_p2 = ball.colliderect(player2_paddle)

        if collided_p1 or collided_p2:
            ball_speed_x *= -1
            paddle_hit_sound.play()
            ball_speed_x *= 1.05 # Increase speed
            ball_speed_y *= 1.05 # Increase speed

            if collided_p1:
                ball.left = player1_paddle.right # Prevent sticking
            elif collided_p2:
                ball.right = player2_paddle.left # Prevent sticking
        
        # Ball goes out of bounds (scoring)
        if ball.left <= 0:
            player2_score += 1
            score_sound.play()
            if player2_score >= WINNING_SCORE:
                winner = "Player 2"
                game_state = GAME_OVER
            else:
                reset_ball_position_and_speed() # Only reset ball, not full match state
        elif ball.right >= SCREEN_WIDTH:
            player1_score += 1
            score_sound.play()
            if player1_score >= WINNING_SCORE:
                winner = "Player 1"
                game_state = GAME_OVER
            else:
                reset_ball_position_and_speed() # Only reset ball

    # --- Drawing ---
    screen.fill(BLACK)

    if game_state == GAME_START:
        draw_text(screen, "Purrfect Pong!", font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(screen, "Press SPACE to Start", font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "P1: W/S, P2: Up/Down", font_smaller, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
        draw_text(screen, f"First to {WINNING_SCORE} points wins!", font_smaller, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 - 10)
        draw_text(screen, "ESC to Pause during game", font_tiny, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 5 // 6 - 20)
        draw_text(screen, "ESC here to Quit", font_tiny, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 5 // 6 + 10)


    elif game_state == GAME_PLAYING:
        draw_net(screen, WHITE, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_paddle(screen, player1_color, player1_paddle)
        draw_paddle(screen, player2_color, player2_paddle)
        draw_ball(screen, ball_color, ball)
        draw_text(screen, str(player1_score), font_large, WHITE, SCREEN_WIDTH // 4, 50)
        draw_text(screen, str(player2_score), font_large, WHITE, SCREEN_WIDTH * 3 // 4, 50)

    elif game_state == GAME_OVER:
        line_spacing = 60
        start_y = SCREEN_HEIGHT // 3 - 40
        draw_text(screen, f"{winner} Wins!", font_large, WHITE, SCREEN_WIDTH // 2, start_y)
        draw_text(screen, f"{player1_score} - {player2_score}", font_medium, WHITE, SCREEN_WIDTH // 2, start_y + line_spacing)
        draw_text(screen, "Play Again? (Y)", font_small, WHITE, SCREEN_WIDTH // 2, start_y + line_spacing * 2.5)
        draw_text(screen, "Main Menu (M)", font_small, WHITE, SCREEN_WIDTH // 2, start_y + line_spacing * 3.5)
        draw_text(screen, "Quit (N)", font_small, WHITE, SCREEN_WIDTH // 2, start_y + line_spacing * 4.5)

    elif game_state == GAME_PAUSED:
        # Optionally draw the game state underneath faintly
        draw_net(screen, WHITE, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_paddle(screen, player1_color, player1_paddle)
        draw_paddle(screen, player2_color, player2_paddle)
        draw_ball(screen, ball_color, ball)
        draw_text(screen, str(player1_score), font_large, WHITE, SCREEN_WIDTH // 4, 50)
        draw_text(screen, str(player2_score), font_large, WHITE, SCREEN_WIDTH * 3 // 4, 50)
        
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Semi-transparent black
        screen.blit(overlay, (0,0))

        line_spacing = 50
        start_y = SCREEN_HEIGHT // 2 - line_spacing * 1.5
        draw_text(screen, "Game Paused", font_medium, WHITE, SCREEN_WIDTH // 2, start_y)
        draw_text(screen, "SPACE to Resume", font_small, WHITE, SCREEN_WIDTH // 2, start_y + line_spacing * 1)
        draw_text(screen, "R for Restart Options", font_small, WHITE, SCREEN_WIDTH // 2, start_y + line_spacing * 2)
        draw_text(screen, "M for Main Menu Options", font_small, WHITE, SCREEN_WIDTH // 2, start_y + line_spacing * 3)
        draw_text(screen, "Q to Quit Game", font_small, WHITE, SCREEN_WIDTH // 2, start_y + line_spacing * 4)

    elif game_state == CONFIRM_RESTART_FROM_PAUSE:
        draw_text(screen, "Restart Current Match?", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
        draw_text(screen, "(Y) Yes / (N) No", font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)

    elif game_state == CONFIRM_MAIN_MENU_FROM_PAUSE:
        draw_text(screen, "Return to Main Menu?", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        draw_text(screen, "(Current game will be lost)", font_smaller, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 -10)
        draw_text(screen, "(Y) Yes / (N) No", font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
