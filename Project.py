
import pygame
import time
import random

pygame.font.init()
pygame.init()


Width, Height = 1000, 750
WIN = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Space Shooter")


redship = pygame.image.load("pixel_ship_red_small.png")
greenship = pygame.image.load("pixel_ship_green_small.png")
blueship = pygame.image.load("pixel_ship_blue_small.png")
enemyshipmap = {
    "red": redship,
    "green": greenship,
    "blue": blueship
}


playership = pygame.image.load("player_ship.png")

redlaser = pygame.image.load("pixel_laser_red.png")
greenlaser = pygame.image.load("pixel_laser_green.png")
bluelaser = pygame.image.load("pixel_laser_blue.png")
playerlaser = pygame.image.load("player_laser.png")
enemylasermap = {
    "red": redlaser,
    "green": greenlaser,
    "blue": bluelaser
}

background = pygame.transform.scale(pygame.image.load("background.png"), (Width, Height))

playermap = {
    "img": playership,
    "laser_img": playerlaser,
    "x": 300,
    "y": 630,
    "health": 100,
    "max_health": 100,
    "lasers": [],
    "cooldown_counter": 0,
    "mask": pygame.mask.from_surface(playership)
}

ENEMIES = []
plasers = []
elasers = []

def collide(obj1, obj2):
    offset_x = obj2['x'] - obj1['x']
    offset_y = obj2['y'] - obj1['y']
    return obj1['mask'].overlap(obj2['mask'], (offset_x, offset_y)) != None


def shoot(shooter, laser_img, laser_list, offset_x=0, offset_y=0):
    if shooter['cooldown_counter'] == 0:
        laser_width = laser_img.get_width()
        laser = {
            "img": laser_img,
            "x": shooter['x'] + (shooter['img'].get_width() // 2) - (laser_width // 2) + offset_x, # Center the laser to the ship
            "y": shooter['y'] + offset_y,
            "mask": pygame.mask.from_surface(laser_img)
        }
        laser_list.append(laser)
        shooter['cooldown_counter'] = 1

def move_lasers(laser_list, vel):
    to_remove = []
    for laser in laser_list:
        laser['y'] += vel
        # Check if laser has got out of screen
        if not (laser['y'] <= Height and laser['y'] >= 0):
            to_remove.append(laser)
    
    # Remove lasers that has gone out of screen
    for laser in to_remove:
        if laser in laser_list:
            laser_list.remove(laser)

def cooldown(shooter, cooldown=30):
    if shooter['cooldown_counter'] >= cooldown:
        shooter['cooldown_counter'] = 0
    elif shooter['cooldown_counter'] > 0:
        shooter['cooldown_counter'] += 1

def makelaser(window, laser):
    window.blit(laser['img'], (laser['x'], laser['y']))

def makeship(window, ship):
    window.blit(ship['img'], (ship['x'], ship['y']))

def draw_healthbar(window, ship):
    # Red background for total health
    pygame.draw.rect(
        window, (255,0,0),
        (ship['x'], ship['y'] + ship['img'].get_height() + 10, ship['img'].get_width(), 10)
    )
    # Green foreground for current health
    current_health_width = ship['img'].get_width() * (ship['health'] / ship['max_health'])
    pygame.draw.rect(
        window, (0,255,0),
        (ship['x'], ship['y'] + ship['img'].get_height() + 10, current_health_width, 10)
    )


def redraw_window(lives, level, kills, main_font, lost_font, lost):
    global playermap

    WIN.blit(background, (0,0))

    # Draw text
    lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
    level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
    kills_label = main_font.render(f"Kills: {kills}", 1, (255,255,255))

    WIN.blit(lives_label, (10, 10))
    WIN.blit(level_label, (Width - level_label.get_width() - 10, 10))
    WIN.blit(kills_label, (10, 60))

    # Draw Enemies
    for enemy in ENEMIES:
        makeship(WIN, enemy)
    
    # Draw Player
    makeship(WIN, playermap)
    draw_healthbar(WIN, playermap)

    # Draw Lasers
    for laser in plasers:
        makelaser(WIN, laser)
    for laser in elasers:
        makelaser(WIN, laser)

    if lost:
        lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
        levellab=main_font.render(f"You Reached level {level}",2,(255,255,255))
        killslab = main_font.render(f"Total Kills: {kills}", 2, (255,255,255))
        WIN.blit(lost_label, (Width/2 - lost_label.get_width()/2, 260))
        WIN.blit(levellab, (Width/2 - levellab.get_width()/2, 340))
        WIN.blit(killslab, (Width/2 - killslab.get_width()/2, 410))  


    pygame.display.update()


def main():
    global ENEMIES, plasers, elasers
    global playermap

    run = True
    FPS = 60
    level = 0
    lives = 5
    kills = 0 
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    wave_length = 5
    enemy_vel = 1
    player_vel = 5
    laser_vel = 5 # Used for player , enemies 

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    # Reset Player State for a new game
    playermap['health'] = playermap['max_health']
    playermap['x'] = 300
    playermap['y'] = 630
    playermap['lasers'] = []
    ENEMIES = []
    plasers = []
    elasers = []

    while run:
        clock.tick(FPS)
        redraw_window(lives, level, kills, main_font, lost_font, lost)

        #Game If Over Check 
        if lives <= 0 or playermap['health'] <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        #Spawning Enemies
        if len(ENEMIES) == 0:
            level += 1
            wave_length += 2
            for i in range(wave_length):
                color = random.choice(["red", "blue", "green"])
                img = enemyshipmap[color]
                enemymap = {
                    "img": img,
                    "laser_img": enemylasermap[color],
                    "x": random.randrange(50, Width - 100),
                    "y": random.randrange(-1500, -100),
                    "color": color,
                    "health": 100,
                    "cooldown_counter": 0,
                    "mask": pygame.mask.from_surface(img)
                }
                ENEMIES.append(enemymap)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()
        ship_width = playermap['img'].get_width()
        ship_height = playermap['img'].get_height()
        
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and playermap['x'] - player_vel > 0: # left
            playermap['x'] -= player_vel
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and playermap['x'] + player_vel + ship_width < Width: # right
            playermap['x'] += player_vel
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and playermap['y'] - player_vel > 0: # up
            playermap['y'] -= player_vel
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and playermap['y'] + player_vel + ship_height + 15 < Height: # down
            playermap['y'] += player_vel
        if keys[pygame.K_SPACE]:
            shoot(playermap, playermap['laser_img'], plasers, offset_y=-10) # Player laser shoots from the top

        # Update Cooldowns
        cooldown(playermap)
        for enemy in ENEMIES:
            cooldown(enemy)

        enemies_to_remove = []
        for enemy in ENEMIES:
            enemy['y'] += enemy_vel # Move enemy down

            # Enemy shooting
            if random.randrange(0, int((2-0.05*level) * FPS)) == 1: # 2-0.05*level*FPS is roughly a 2-second average cooldown which decraases with each level
                shoot(enemy, enemy['laser_img'], elasers, offset_y=enemy['img'].get_height()) # Enemy laser shoots from the bottom

            # Collision: Enemy and Player
            if collide(enemy, playermap):
                playermap['health'] -= 10
                enemies_to_remove.append(enemy)

            # Enemy passes bottom of screen
            elif enemy['y'] + enemy['img'].get_height() > Height:
                lives -= 1
                enemies_to_remove.append(enemy)

        # Remove dead/off-screen enemies
        for enemy in enemies_to_remove:
            if enemy in ENEMIES:
                ENEMIES.remove(enemy)
                


        move_lasers(elasers, laser_vel+2*level) # Enemy lasers move down so positive vel
        
        enemy_lasers_to_remove = []
        for laser in elasers:
            if collide(laser, playermap):
                playermap['health'] -= 10
                enemy_lasers_to_remove.append(laser)
        
        for laser in enemy_lasers_to_remove:
            if laser in elasers:
                elasers.remove(laser)



        move_lasers(plasers, -laser_vel) # Player lasers move up so negative vel

        player_lasers_to_remove = []
        enemies_hit = []

        for laser in plasers:
            for enemy in ENEMIES:
                if collide(laser, enemy):
                    enemies_hit.append(enemy)
                    player_lasers_to_remove.append(laser)
                    break # Laser hits only one enemy
        
        # Remove hit enemies and lasers
        for enemy in enemies_hit:
            if enemy in ENEMIES:
                ENEMIES.remove(enemy)
                kills += 1 
        for laser in player_lasers_to_remove:
            if laser in plasers:
                plasers.remove(laser)

    # Resetting global lists for next game if called from main_menu
    plasers = []
    elasers = []
    ENEMIES = []


def main_menu():
    pygame.display.set_caption("Space Shooter Game")  # set window title

    title_font = pygame.font.SysFont("comicsans", 72, bold=True)
    button_font = pygame.font.SysFont("comicsans", 40)

    # button sizes
    button_width = 260
    button_height = 70

    # create rects
    play_button = pygame.Rect(0, 0, button_width, button_height)
    play_button.center = (Width // 2, Height // 2)

    quit_button = pygame.Rect(0, 0, button_width, button_height)
    quit_button.center = (Width // 2, Height // 2 + 100)

    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        # background
        WIN.blit(background, (0, 0))

        # dark overlay 
        overlay = pygame.Surface((Width, Height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        WIN.blit(overlay, (0, 0))

        # title text
        title_label = title_font.render("Space Shooter Game", True, (255, 255, 255))
        WIN.blit(
            title_label,
            (Width // 2 - title_label.get_width() // 2, Height // 2 - 180),
        )


        # button colors 
        def draw_button(rect, text):
            if rect.collidepoint(mouse_pos):
                color = (80, 80, 200)       # hover color
            else:
                color = (40, 40, 120)       # normal color

            pygame.draw.rect(WIN, color, rect, border_radius=18)
            pygame.draw.rect(WIN, (255, 255, 255), rect, 2, border_radius=18)

            label = button_font.render(text, True, (255, 255, 255))
            WIN.blit(
                label,
                (
                    rect.centerx - label.get_width() // 2,
                    rect.centery - label.get_height() // 2,
                ),
            )

        # draw buttons
        draw_button(play_button, "Play")
        draw_button(quit_button, "Quit")

        pygame.display.update()

        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button.collidepoint(event.pos):
                    main()          
                if quit_button.collidepoint(event.pos):
                    run = False

    pygame.quit()

main_menu()



