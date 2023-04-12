import random
import pygame
import math
from pygame.font import Font

# initialize Pygame
pygame.init()

# set the size of the window
WIDTH, HEIGHT = (1800, 800)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# set the position and velocity of the circle
circle_pos = [100, 250]
circle_radius = 50
circle_vel = [0.01, 0]

# set the length and angle of the lines
line_length = 50
line_angle = math.pi / 4  # 45 degrees
angle = 0
RED = pygame.Color("red")
clock = pygame.time.Clock()
startpoint = pygame.math.Vector2(320, 240)
endpoint = pygame.math.Vector2(170, 0)
running = True
mousex, mousey = 0, 0
x_pos = [WIDTH/2, HEIGHT/2]
y_angle = math.radians(random.uniform(-360, 360))
speed = 5
y_length = 75
STATUS_COLOR = (50, 255, 255)
y_pos = [x_pos[0] + y_length *
         math.cos(y_angle), x_pos[1] + y_length * math.sin(y_angle)]


def recalc(x_pos, y_angle):
    # calculate the endpoints of the lines
    y_pos = [x_pos[0] + y_length *
             math.cos(y_angle), x_pos[1] + y_length * math.sin(y_angle)]
    line_length = 50
    line_angle = math.radians(45)  # 20 degrees in radians
    line_pos1 = [x_pos[0] + line_length * math.cos(y_angle + line_angle),
                 x_pos[1] + line_length * math.sin(y_angle + line_angle)]

    line_pos2 = [x_pos[0] + line_length * math.cos(y_angle - line_angle),
                 x_pos[1] + line_length * math.sin(y_angle - line_angle)]
    return line_pos1, line_pos2, y_pos

# Startpunkt (x_pos) mit dem Richtungsvektor multiplizieren = neue Position


def move(x_pos, y_pos, y_angle):
    xd = ['', '']
    xd[0] = (y_pos[0] - x_pos[0]) * 0.05
    xd[1] = (y_pos[1] - x_pos[1]) * 0.05
    STATUS_COLOR = (50, 255, 255)
    x_pos_o = (x_pos[0] + (xd[0]*40), (x_pos[1] + (xd[1]*40)))
    if x_pos_o[0] < 0 or x_pos_o[0] > WIDTH:
        y_angle = (random.uniform(y_angle+0, y_angle+0.8))
        x_pos[0] = x_pos[0] - xd[0]
        STATUS_COLOR = (255, 0, 0)
        print("wall Verti")
    if x_pos_o[1] < 0 or x_pos_o[1] > HEIGHT:
        y_angle = (random.uniform(y_angle+0, y_angle+0.8))

        x_pos[1] = x_pos[1] - xd[1]
        print("wall Hori")
        STATUS_COLOR = (255, 0, 0)
    x_pos[0] = x_pos[0] + xd[0]
    x_pos[1] = x_pos[1] + xd[1]

    # x_pos = x_pos[0] * xd[0], x_pos[1] * xd[1]
    # print(f'x({round(x_pos[0])}, {round(x_pos[1])}) - y({round(y_pos[0])}, {round(y_pos[1])})')
    return x_pos, x_pos_o, STATUS_COLOR


def angle(A, B, aspectRatio):
    x = B[0] - A[0]
    y = B[1] - A[1]
    return math.atan2(-y, x / aspectRatio)


while running:
    line_pos1, line_pos2, y_pos = recalc(x_pos, y_angle)
    font = Font(None, 16)  # Create the font object here
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mousex, mousey = pygame.mouse.get_pos()
                print(mousex, mousey)

    y_angle = (random.uniform(y_angle-0.4, y_angle+0.4))
    # Update Antennas
    line_pos1, line_pos2, y_pos = recalc(x_pos, y_angle)

    # Update Ant
    xd, x_pos_o, STATUS_COLOR = move(x_pos, y_pos, y_angle)
    print(xd)

    # clear the screen
    screen.fill((255, 255, 255))

    # RED
    # pygame.draw.line(screen, (255, 0, 0), x_pos, y_pos, 2)
    # fontR = font.render(
    #    f'{round(y_pos[0]), round(y_pos[1])}', True, (120, 0, 0))
    # screen.blit(fontR, y_pos)
    # Purple
    pygame.draw.line(screen, STATUS_COLOR, x_pos, x_pos_o, 2)
    # BLUE
    pygame.draw.line(screen, (0, 0, 255), x_pos, line_pos1, 1)
    fontB = font.render(
        f'{round(line_pos1[0]), round(line_pos1[1])}', True, (0, 0, 120))
    screen.blit(fontB, line_pos1)

    # GREEN
    pygame.draw.line(screen, (0, 255, 0), x_pos, line_pos2, 1)
    fontG = font.render(
        f'{round(line_pos2[0]), round(line_pos2[1])}', True, (0, 120, 0))
    screen.blit(fontG, line_pos2)

    a1 = angle(x_pos, line_pos1, WIDTH/HEIGHT)
    a2 = angle(x_pos, line_pos2, WIDTH/HEIGHT)

    pygame.draw.arc(screen, (0, 0, 0),
                    (x_pos[0]-(50), x_pos[1]-(50), 50*2, 50*2), a1, a2)
    # update the display
    clock.tick(20)
    pygame.display.update()
