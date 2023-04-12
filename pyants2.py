import pygame as pg
import numpy as np
import random

pg.init()

# Set up constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_ANTS = 50
PHEROMONE_SIZE = 10
PHEROMONE_DECAY_RATE = 0.05
ANT_SPEED = 2

# Set up Pygame window
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Ant Colony Optimization Visualization")

# Set up pheromone grid
pheromone_grid = np.zeros(
    (SCREEN_WIDTH // PHEROMONE_SIZE, SCREEN_HEIGHT // PHEROMONE_SIZE))

# Define Ant class


class Ant(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.Surface((10, 10))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=pos)
        self.direction = random.uniform(0, 2*np.pi)
        self.pheromone_strength = 1

    def update(self):
        # Move ant based on direction and speed
        x, y = self.rect.center
        x += ANT_SPEED * np.cos(self.direction)
        y += ANT_SPEED * np.sin(self.direction)
        self.rect.center = (x, y)

        # Leave pheromone trail behind
        i, j = int(x // PHEROMONE_SIZE), int(y // PHEROMONE_SIZE)
        if i >= 0 and i < SCREEN_WIDTH // PHEROMONE_SIZE and j >= 0 and j < SCREEN_HEIGHT // PHEROMONE_SIZE:
            pheromone_grid[i, j] += self.pheromone_strength

        # Follow pheromone trail
        x, y = self.rect.center
        i, j = int(x // PHEROMONE_SIZE), int(y // PHEROMONE_SIZE)
        neighbors = [(i+di, j+dj) for di in range(-1, 2) for dj in range(-1, 2)
                     if i+di >= 0 and i+di < SCREEN_WIDTH // PHEROMONE_SIZE and j+dj >= 0 and j+dj < SCREEN_HEIGHT // PHEROMONE_SIZE]
        neighbor_strengths = [pheromone_grid[i+di, j+dj]
                              for di, dj in neighbors]
        if neighbor_strengths:
            max_strength = max(neighbor_strengths)
            max_indices = [k for k, v in enumerate(
                neighbor_strengths) if v == max_strength]
            chosen_index = random.choice(max_indices)
            chosen_direction = np.arctan2(
                neighbors[chosen_index][1] - j, neighbors[chosen_index][0] - i)
            self.direction = chosen_direction

        # Reduce pheromone strength over time
        self.pheromone_strength -= PHEROMONE_DECAY_RATE
        self.pheromone_strength = max(self.pheromone_strength, 0)


# Create group of ants
all_ants = pg.sprite.Group()
for i in range(NUM_ANTS):
    ant = Ant((random.randint(0, SCREEN_WIDTH),
              random.randint(0, SCREEN_HEIGHT)))
    all_ants.add(ant)

# Main game loop
running = True
clock = pg.time.Clock()
while running:
    # Handle events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False

    # spawn food
    if not food and randint(0, 200) == 5:
        x = randint(10, WIDTH-10)
        y = randint(10, HEIGHT-10)
        food = Food((x, y))
        allsprites.add(food)
        foods.add(food)

    # update all entities
    for ant in ants:
        ant.update(dt)
        # check if ant collides with food
        if food and pg.sprite.collide_circle(ant, food):
            food.pickup()
            food = None

    # draw background and pheromone grid
    screen.fill((10, 10, 10))
    pheroSurface = pherogrid.update(dt)
    screen.blit(pg.transform.scale(pheroSurface, (WIDTH, HEIGHT)), (0, 0))

    # draw all entities
    allsprites.draw(screen)

    # update display
    if SHOWFPS:
        fps = font.render(str(int(clock.get_fps())), True, pg.Color('white'))
        screen.blit(fps, (50, 50))
    pg.display.update()
    # wait for next tick
    clock.tick(FPS)

# clean up
pg.quit()

if name == 'main':
    main()
