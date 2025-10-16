import pygame
import random

pygame.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Shooter with Enemy Health")

# Load images
player_img = pygame.image.load("player.png").convert_alpha()
enemy_img = pygame.image.load("enemy.png").convert_alpha()
friend_img = pygame.image.load("friend.png").convert_alpha()
bg_img = pygame.image.load("background.png").convert_alpha()
laser_img = pygame.image.load("laser.png").convert_alpha()

# Scale images
player_img = pygame.transform.scale(player_img, (171, 341))
enemy_img = pygame.transform.scale(enemy_img, (100, 50))
friend_img = pygame.transform.scale(friend_img, (100, 43))
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
laser_img = pygame.transform.scale(laser_img, (50, 150))  # laser tile width x height
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
enemies = []  # each enemy: [x, y, health]
friends = []  # each friend: [x, y]
spawn_timer = 0

# Score
score = 0

# Enemy settings
ENEMY_MAX_HEALTH = 9

# Game loop
running = True
while running:
    clock.tick(FPS)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                laser_on = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                laser_on = False

    # Player movement
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
    # Center laser on player
        laser_x = player_x + player_width // 2 - laser_img.get_width() // 2 + 100

    # Tile laser from top of player to top of screen
        for y in range(player_y, -laser_img.get_height(), -laser_img.get_height()):
            screen.blit(laser_img, (laser_x, y))

    # Collision rectangle for laser
        laser_rect = pygame.Rect(laser_x, 0, laser_img.get_width(), player_y + player_height)



        # Hit enemies
        for e in enemies[:]:
            enemy_rect = pygame.Rect(e[0], e[1], enemy_img.get_width(), enemy_img.get_height())
            if laser_rect.colliderect(enemy_rect):
                e[2] -= 1  # reduce health by 1 per frame laser touches
                if e[2] <= 0:
                    enemies.remove(e)
                    score += 1

        # Hit friends
        for f in friends[:]:
            friend_rect = pygame.Rect(f[0], f[1], friend_img.get_width(), friend_img.get_height())
            if laser_rect.colliderect(friend_rect):
                # Optional: remove friend if you want
                friends.remove(f)
                score -= 1  # penalty for hitting friends

    # Penalize enemies reaching right edge
    for e in enemies[:]:
        if e[0] > WIDTH:
            enemies.remove(e)
            score -= 1  # negative points for letting enemy escape

    # Remove off-screen friends
    friends = [f for f in friends if f[0] < WIDTH]

    # Draw background
    screen.blit(bg_img, (0, 0))

    # Draw laser
    if laser_on:
        for y in range(player_y, -laser_img.get_height(), -laser_img.get_height()):
            screen.blit(laser_img, (player_x - laser_img.get_width() // 2 + 73 , y))

    # Draw player
    screen.blit(player_img, (player_x, player_y))

    # Draw enemies & health bars
    for e in enemies:
        screen.blit(enemy_img, (e[0], e[1]))
        # draw health bar above enemy
        bar_width = enemy_img.get_width()
        bar_height = 5
        health_ratio = e[2] / ENEMY_MAX_HEALTH
        pygame.draw.rect(screen, (255,0,0), (e[0], e[1]-10, bar_width, bar_height))  # background
        pygame.draw.rect(screen, (0,255,0), (e[0], e[1]-10, bar_width*health_ratio, bar_height))  # current health

    # Draw friends
    for f in friends:
        screen.blit(friend_img, (f[0], f[1]))

    # Draw score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()

