import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Statue Cannon Defense - Twin Towers")

# Clock
clock = pygame.time.Clock()
FPS = 60

# TESTING MODE - Shows hitboxes
SHOW_HITBOXES = True

# Load corrected statue image
try:
    statue_img = pygame.image.load("corrected_statue.jpg").convert_alpha()
    statue_img = pygame.transform.scale(statue_img, (40, 40))
except:
    statue_img = None
    print("Statue image not found, using placeholder")

# Load twin towers background
try:
    bg_img = pygame.image.load("twin_towers.jpg").convert_alpha()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
except:
    bg_img = None
    print("Background image not found")

# Load M1 Abrams tank image
try:
    tank_img = pygame.image.load("m1_abrams.png").convert_alpha()
    tank_img = pygame.transform.scale(tank_img, (80, 50))
except:
    tank_img = None
    print("M1 Abrams image not found, using placeholder")

# Cannon position and angle
cannon_x, cannon_y = WIDTH // 2, HEIGHT - 50
cannon_angle = -math.pi / 2
cannon_speed = 7
barrel_length = 50

# Projectiles (Statue of Liberty ammo)
projectiles = []

# Planes (Boeing 737) from both sides
planes = []
spawn_timer = 0
plane_speed = 4

# Explosions
explosions = []

# Score
score = 0
game_active = True

# Pressure system for launch velocity
space_pressed = False
pressure = 0
max_pressure = 100

# Twin towers hitbox data
tower_hitboxes = [
    {"x": 150, "y": 150, "width": 80, "height": 350},  # Left tower
    {"x": 570, "y": 150, "width": 80, "height": 350}   # Right tower
]

# Draw M1 Abrams tank as cannon
def draw_cannon():
    global cannon_x, cannon_y, cannon_angle
    
    if tank_img:
        # Rotate tank based on barrel angle
        rotated_tank = pygame.transform.rotate(tank_img, math.degrees(-cannon_angle))
        rect = rotated_tank.get_rect(center=(int(cannon_x), int(cannon_y)))
        screen.blit(rotated_tank, rect)
    else:
        # Fallback: draw simple tank shape
        pygame.draw.rect(screen, (50, 100, 50), (cannon_x - 25, cannon_y - 15, 50, 30))
        pygame.draw.circle(screen, (60, 120, 60), (int(cannon_x), int(cannon_y)), 18)
    
    # Barrel
    barrel_end_x = cannon_x + barrel_length * math.cos(cannon_angle)
    barrel_end_y = cannon_y + barrel_length * math.sin(cannon_angle)
    pygame.draw.line(screen, (150, 150, 150), (cannon_x, cannon_y), (barrel_end_x, barrel_end_y), 10)

# Draw planes (Boeing 737)
def draw_plane(plane):
    x, y, direction, health = plane
    
    # Plane body
    color = (0, 100, 200) if health > 0 else (255, 0, 0)
    
    # Scale based on direction
    if direction == "left":
        points = [
            (x, y),
            (x + 60, y),
            (x + 55, y - 15),
            (x + 50, y),
            (x + 30, y - 10)
        ]
    else:  # right
        points = [
            (x, y),
            (x - 60, y),
            (x - 55, y - 15),
            (x - 50, y),
            (x - 30, y - 10)
        ]
    
    pygame.draw.polygon(screen, color, points)
    
    # Windows
    for i in range(4):
        if direction == "left":
            pygame.draw.circle(screen, (255, 255, 0), (int(x + 10 + i * 12), int(y - 5)), 2)
        else:
            pygame.draw.circle(screen, (255, 255, 0), (int(x - 10 - i * 12), int(y - 5)), 2)
    
    # Health indicator
    font = pygame.font.SysFont(None, 24)
    health_text = font.render(str(health), True, (255, 255, 255))
    screen.blit(health_text, (int(x - 10), int(y - 25)))
    
    # Hitbox (for testing)
    if SHOW_HITBOXES:
        pygame.draw.rect(screen, (255, 0, 255), (int(x - 40), int(y - 20), 80, 40), 1)

# Draw projectiles (Statue)
def draw_projectiles():
    for proj in projectiles:
        x, y, vx, vy = proj
        if statue_img:
            screen.blit(statue_img, (int(x - 20), int(y - 20)))
        else:
            pygame.draw.circle(screen, (255, 215, 0), (int(x), int(y)), 8)
        
        # Hitbox (for testing)
        if SHOW_HITBOXES:
            pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), 10, 1)

# Draw explosions
def draw_explosions():
    for exp in explosions:
        x, y, radius, life, max_life = exp
        alpha = int(255 * (1 - life / max_life))
        color = (255, int(165 * (1 - life / max_life)), 0)
        pygame.draw.circle(screen, color, (int(x), int(y)), int(radius))

# Twin towers hitbox (background)
def draw_twin_towers():
    if bg_img:
        screen.blit(bg_img, (0, 0))
    else:
        # Draw background
        screen.fill((135, 206, 235))
        
        # Twin towers
        pygame.draw.rect(screen, (139, 134, 128), (150, 150, 80, 350))
        pygame.draw.rect(screen, (139, 134, 128), (570, 150, 80, 350))
        
        # Windows
        for i in range(20):
            for j in range(2):
                pygame.draw.rect(screen, (135, 206, 235), (160 + i * 8, 160 + i * 15, 4, 4))
                pygame.draw.rect(screen, (135, 206, 235), (580 + i * 8, 160 + i * 15, 4, 4))
    
    # Draw hitboxes (for testing)
    if SHOW_HITBOXES:
        for tower in tower_hitboxes:
            pygame.draw.rect(screen, (255, 0, 0), (tower["x"], tower["y"], tower["width"], tower["height"]), 2)

# Check if plane hits tower
def check_tower_collision(x, y):
    for tower in tower_hitboxes:
        if (tower["x"] < x < tower["x"] + tower["width"] and 
            tower["y"] < y < tower["y"] + tower["height"]):
            return True
    return False

# Game loop
running = True
while running:
    clock.tick(FPS)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                space_pressed = True
            if event.key == pygame.K_h:
                SHOW_HITBOXES = not SHOW_HITBOXES
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and space_pressed and game_active:
                # Fire projectile with pressure-based velocity
                velocity_multiplier = 1 + (pressure / max_pressure) * 1.5  # 1x to 2.5x
                proj_vx = 8 * velocity_multiplier * math.cos(cannon_angle)
                proj_vy = 8 * velocity_multiplier * math.sin(cannon_angle)
                projectiles.append([cannon_x + barrel_length * math.cos(cannon_angle),
                                   cannon_y + barrel_length * math.sin(cannon_angle),
                                   proj_vx, proj_vy])
                space_pressed = False
                pressure = 0

    # Cannon movement and aiming
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and cannon_x > 20:
        cannon_x -= cannon_speed
    if keys[pygame.K_RIGHT] and cannon_x < WIDTH - 20:
        cannon_x += cannon_speed
    if keys[pygame.K_UP] and cannon_angle > -math.pi / 2 - 0.5:
        cannon_angle -= 0.05
    if keys[pygame.K_DOWN] and cannon_angle < -0.1:
        cannon_angle += 0.05
    
    # Increase pressure while space is held
    if space_pressed and pressure < max_pressure:
        pressure += 2

    # Spawn planes
    spawn_timer += 1
    if spawn_timer > 70 and game_active:
        spawn_timer = 0
        if random.random() > 0.5:
            # From left
            planes.append([0, random.randint(50, 250), "right", 2])
        else:
            # From right
            planes.append([WIDTH, random.randint(50, 250), "left", 2])

    # Move planes
    for plane in planes[:]:
        x, y, direction, health = plane
        if direction == "right":
            x += plane_speed
        else:
            x -= plane_speed
        
        # Check tower collision
        if check_tower_collision(x, y):
            explosions.append([x, y, 50, 30, 30])
            planes.remove(plane)
            continue
        
        plane[0] = x
        if x < -100 or x > WIDTH + 100:
            planes.remove(plane)

    # Move projectiles and apply gravity
    for proj in projectiles[:]:
        x, y, vx, vy = proj
        y += vy
        vy += 0.3  # gravity
        x += vx
        
        if y > HEIGHT or x < -50 or x > WIDTH + 50:
            projectiles.remove(proj)
            continue
        
        proj[0] = x
        proj[1] = y
        proj[3] = vy
        
        # Check collision with planes
        for plane in planes[:]:
            px, py, direction, health = plane
            dist = math.hypot(x - px, y - py)
            if dist < 40:
                explosions.append([px, py, 40, 25, 25])
                plane[3] -= 1
                if plane[3] <= 0:
                    planes.remove(plane)
                    score += 10
                if proj in projectiles:
                    projectiles.remove(proj)
                break

    # Update explosions
    for exp in explosions[:]:
        x, y, radius, life, max_life = exp
        life -= 1
        exp[3] = life
        if life <= 0:
            explosions.remove(exp)

    # Game over condition
    if len(planes) > 5:
        game_active = False

    # Draw everything
    draw_twin_towers()
    draw_cannon()
    draw_projectiles()
    
    for plane in planes:
        draw_plane(plane)
    
    draw_explosions()

    # Draw score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Draw controls
    font_small = pygame.font.SysFont(None, 24)
    controls = font_small.render("Arrow Keys: Move/Aim | SPACE: Shoot (Hold for Power) | H: Toggle Hitboxes", True, (255, 255, 255))
    screen.blit(controls, (10, HEIGHT - 30))

    # Draw pressure bar
    if space_pressed:
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 50
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * (pressure / max_pressure), bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        pressure_text = font_small.render(f"Power: {int(pressure)}%", True, (255, 255, 0))
        screen.blit(pressure_text, (bar_x, bar_y - 25))

    if not game_active:
        font_large = pygame.font.SysFont(None, 48)
        game_over_text = font_large.render("GAME OVER!", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 50))

    pygame.display.flip()

pygame.quit()

