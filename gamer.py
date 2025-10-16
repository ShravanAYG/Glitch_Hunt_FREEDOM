import pygame
import random
import imageio

pygame.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Shooter with Startup + Troll Event")

# Load images
player_img = pygame.image.load("player.png").convert_alpha()
enemy_img = pygame.image.load("enemy.png").convert_alpha()
friend_img = pygame.image.load("friend.png").convert_alpha()
bg_img = pygame.image.load("background.png").convert_alpha()
laser_img = pygame.image.load("laser.png").convert_alpha()
flag_img = pygame.image.load("flag.jpg").convert_alpha()  # startup background
eagle_img = pygame.image.load("eagle.jpg").convert_alpha()
troll_img = pygame.image.load("troll.png").convert_alpha()  # funny troll image

# Scale images
player_img = pygame.transform.scale(player_img, (171, 341))
enemy_img = pygame.transform.scale(enemy_img, (100, 50))
friend_img = pygame.transform.scale(friend_img, (100, 43))
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
laser_img = pygame.transform.scale(laser_img, (50, 150))
flag_img = pygame.transform.scale(flag_img, (WIDTH, HEIGHT))
eagle_img = pygame.transform.scale(eagle_img, (180, 130))
troll_img = pygame.transform.scale(troll_img, (200, 200))

# Load ben.gif frames
try:
    ben_gif = imageio.get_reader("ben.gif")
    ben_frames = [pygame.image.fromstring(frame.tobytes(), frame.shape[1::-1], "RGB") for frame in ben_gif]
except Exception as e:
    ben_frames = None
    print(f"Could not load ben.gif: {e}")

# Load laugh sound
try:
    laugh_sound = pygame.mixer.Sound("laugh.mp3")
except:
    laugh_sound = None
    print("laugh.mp3 not found — sound disabled")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Player
player_width, player_height = player_img.get_size()
player_x, player_y = WIDTH // 2 - player_width // 2, HEIGHT - 250
player_speed = 7

# Laser
laser_on = False

# Enemies & friends
enemies = []
friends = []
spawn_timer = 0

# Score
score = 0
previous_score = 0  # Track for troll trigger

# Enemy settings
ENEMY_MAX_HEALTH = 9

# -----------------------------
# STARTUP SCREEN VARIABLES
# -----------------------------
startup_active = True
eagle_x = -200
ben_timer = 0
ben_scale = 0.1
ben_started = False

# Startup timing
enlarge_duration = 48
stay_duration = 180
total_duration = enlarge_duration + stay_duration

# Troll popup variables
troll_active = False
troll_timer = 0
TROLL_DURATION = 120  # 2 seconds at 60 FPS

# -----------------------------
# STARTUP SCREEN FUNCTION
# -----------------------------
def draw_startup_screen():
    global eagle_x, ben_timer, ben_scale, ben_started, startup_active

    # Draw flag background
    screen.blit(flag_img, (0, 0))

    # Move eagle
    eagle_x += 5
    if eagle_img:
        screen.blit(eagle_img, (int(eagle_x), 150))

    # Draw "CAWWWWW" trailing text
    font_large = pygame.font.SysFont(None, 72, bold=True)
    caw_text = font_large.render("CAWWWWW", True, (255, 255, 255))
    screen.blit(caw_text, (int(eagle_x - 200), 170))

    # When eagle passes right edge, start ben animation
    if eagle_x > WIDTH and not ben_started:
        ben_started = True
        ben_timer = 0

    # Show ben.gif animation
    if ben_started and ben_frames:
        ben_timer += 1
        if ben_timer <= enlarge_duration:
            progress = ben_timer / enlarge_duration
            ben_scale = 0.1 + (progress * 0.9)
        else:
            ben_scale = 1.0

        frame_idx = (ben_timer // 5) % len(ben_frames)
        ben_frame = ben_frames[frame_idx]
        original_w, original_h = ben_frame.get_size()
        new_w = int(original_w * ben_scale)
        new_h = int(original_h * ben_scale)
        ben_scaled = pygame.transform.scale(ben_frame, (new_w, new_h))
        ben_x = WIDTH // 2 - new_w // 2
        ben_y = 100
        screen.blit(ben_scaled, (ben_x, ben_y))

        if ben_timer > enlarge_duration:
            font_hello = pygame.font.SysFont(None, 48)
            hello_text = font_hello.render("Hello There", True, (255, 255, 255))
            text_x = WIDTH // 2 - hello_text.get_width() // 2
            screen.blit(hello_text, (text_x, ben_y + new_h + 20))

        if ben_timer > total_duration:
            startup_active = False

    pygame.display.flip()

# -----------------------------
# TROLL POPUP FUNCTION
# -----------------------------
def draw_troll_popup():
    """Show troll face + laughing text"""
    screen.blit(bg_img, (0, 0))
    troll_x = WIDTH // 2 - troll_img.get_width() // 2
    troll_y = HEIGHT // 2 - troll_img.get_height() // 2
    screen.blit(troll_img, (troll_x, troll_y))

    font = pygame.font.SysFont(None, 72, bold=True)
    text = font.render("HAHAHA!", True, (255, 0, 0))
    text_x = WIDTH // 2 - text.get_width() // 2
    screen.blit(text, (text_x, troll_y + troll_img.get_height() + 20))
    pygame.display.flip()

# -----------------------------
# MAIN GAME LOOP
# -----------------------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not startup_active:
                laser_on = True
            elif startup_active and event.key == pygame.K_SPACE:
                startup_active = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                laser_on = False

    # Startup screen
    if startup_active:
        draw_startup_screen()
        continue

    # Troll popup
    if troll_active:
        draw_troll_popup()
        troll_timer += 1
        if troll_timer > TROLL_DURATION:
            troll_timer = 0
            troll_active = False
        continue

    # -----------------------------
    # GAME LOGIC
    # -----------------------------
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

    # Spawn enemies/friends
    spawn_timer += 1
    if spawn_timer > 50:
        spawn_timer = 0
        if random.random() < 0.7:
            enemies.append([0, random.randint(50, HEIGHT - 150), ENEMY_MAX_HEALTH])
        else:
            friends.append([0, random.randint(50, HEIGHT - 150)])

    # Move enemies/friends
    for e in enemies:
        e[0] += 4
    for f in friends:
        f[0] += 3

    # Laser collision
    if laser_on:
        laser_x = player_x + player_width // 2 - laser_img.get_width() // 2 + 100
        for y in range(player_y, -laser_img.get_height(), -laser_img.get_height()):
            screen.blit(laser_img, (laser_x, y))
        laser_rect = pygame.Rect(laser_x, 0, laser_img.get_width(), player_y + player_height)

        for e in enemies[:]:
            enemy_rect = pygame.Rect(e[0], e[1], enemy_img.get_width(), enemy_img.get_height())
            if laser_rect.colliderect(enemy_rect):
                e[2] -= 1
                if e[2] <= 0:
                    enemies.remove(e)
                    score += 1

        for f in friends[:]:
            friend_rect = pygame.Rect(f[0], f[1], friend_img.get_width(), friend_img.get_height())
            if laser_rect.colliderect(friend_rect):
                friends.remove(f)
                score -= 1

    # Penalize escaped enemies
    for e in enemies[:]:
        if e[0] > WIDTH:
            enemies.remove(e)
            score -= 1

    # Remove off-screen friends
    friends = [f for f in friends if f[0] < WIDTH]

    # -----------------------------
    # TROLL TRIGGER CHECK
    # -----------------------------
    if previous_score == 1 and score == 0 and not troll_active:
        troll_active = True
        troll_timer = 0
        if laugh_sound:
            laugh_sound.play()

    previous_score = score

    # -----------------------------
    # DRAW EVERYTHING
    # -----------------------------
    screen.blit(bg_img, (0, 0))

    if laser_on:
        for y in range(player_y, -laser_img.get_height(), -laser_img.get_height()):
            screen.blit(laser_img, (player_x - laser_img.get_width() // 2 + 73, y))

    screen.blit(player_img, (player_x, player_y))

    for e in enemies:
        screen.blit(enemy_img, (e[0], e[1]))
        bar_width = enemy_img.get_width()
        bar_height = 5
        health_ratio = e[2] / ENEMY_MAX_HEALTH
        pygame.draw.rect(screen, (255, 0, 0), (e[0], e[1]-10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (e[0], e[1]-10, bar_width*health_ratio, bar_height))

    for f in friends:
        screen.blit(friend_img, (f[0], f[1]))

    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()

