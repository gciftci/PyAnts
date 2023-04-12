
import numpy as np
import pygame
import sys
import math

WIDTH = 800
HEIGHT = 600
N_FOOD = 5
FOOD_SIZE = 15
N_ANT = 50
ANT_SIZE = 5
LOOKING_FOR_FOOD_COLOR = (0, 0, 255, 200)
GOT_FOOD_COLOR = (0, 255, 0, 200)
NEST_COLOR = (255, 255, 255)
FOOD_COLOR = (255, 165, 0)
BG_COLOR = (0, 0, 0)
FPS = 60
DECAY_RATE = 0.95
FOOD_THRESHOLD = 3
HOME_THRESHOLD = 50
DESIRED_DIR_CHANGE_PROB = 0.05
FOOD_PHEROMONE_STRENGTH = 1
HOME_PHEROMONE_STRENGTH = 5


class Ant:
    def __init__(self, x, y, nest):
        self.x = x
        self.y = y
        self.direction = np.random.rand(2) - 0.5
        self.direction /= np.linalg.norm(self.direction)
        self.speed = np.random.uniform(0.5, 2)
        self.nest = nest
        self.has_food = False

    def update(self, food, food_pheromone, home_pheromone, looking_for_food_pheromone, got_food_pheromone):
        if self.has_food:
            self.follow_pheromone(home_pheromone, got_food_pheromone)
            if self.nest.distance(self) < HOME_THRESHOLD:
                self.has_food = False
        else:
            self.detect_food(food)
            self.follow_pheromone(looking_for_food_pheromone, food_pheromone)
        self.leave_pheromone_trail(
            got_food_pheromone if self.has_food else looking_for_food_pheromone
        )

    def detect_food(self, food):
        for f in food:
            if self.distance(f) < FOOD_THRESHOLD:
                self.direction = (f.pos() - self.pos()) / \
                    np.linalg.norm(f.pos() - self.pos())
                self.has_food = True
                food.remove(f)
                break

    def follow_pheromone(self, pheromone1, pheromone2):
        if np.random.rand() < DESIRED_DIR_CHANGE_PROB:
            self.direction = np.random.rand(2) - 0.5
            self.direction /= np.linalg.norm(self.direction)
        pos = self.pos()
        if self.has_food:
            direction = self.nest.pos() - pos
            direction /= np.linalg.norm(direction)
            desired_dir = direction + pheromone2.value_at(pos) * direction
        else:
            desired_dir = self.direction + \
                pheromone1.value_at(pos) * self.direction
        self.direction = desired_dir / np.linalg.norm(desired_dir)
        self.x += self.speed * self.direction[0]
        self.y += self.speed * self.direction[1]

    def leave_pheromone_trail(self, pheromone):
        pheromone.add_pheromone(
            self.x,
            self.y,
            HOME_PHEROMONE_STRENGTH if self.has_food else FOOD_PHEROMONE_STRENGTH,
        )

    def pos(self):
        return np.array([self.x, self.y])

    def distance(self, other):
        return np.linalg.norm(self.pos() - other.pos())


class Nest:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def pos(self):
        return np.array([self.x, self.y])

    def distance(self, other):
        return np.linalg.norm(self.pos() - other.pos())


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def pos(self):
        return np.array([self.x, self.y])

    def draw(self, screen):
        pygame.draw.circle(screen, FOOD_COLOR, (int(
            self.x), int(self.y)), FOOD_SIZE // 2)


class PheromoneGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.zeros((width, height))

    def add_pheromone(self, x, y, strength):
        i = math.floor(x)
        j = math.floor(y)
        if i >= 0 and i < self.width and j >= 0 and j < self.height:
            self.grid[i, j] += strength

    def value_at(self, pos):
        i = math.floor(pos[0])
        j = math.floor(pos[1])
        return self.grid[i, j]

    def decay(self):
        self.grid *= DECAY_RATE


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.nest = Nest(np.random.uniform(0, WIDTH),
                         np.random.uniform(0, HEIGHT))
        self.food = [Food(np.random.uniform(0, WIDTH),
                          np.random.uniform(0, HEIGHT)) for _ in range(N_FOOD)]
        self.ants = [Ant(self.nest.x, self.nest.y, self.nest)
                     for _ in range(N_ANT)]
        self.looking_for_food_pheromone = PheromoneGrid(HEIGHT, WIDTH)
        self.got_food_pheromone = PheromoneGrid(HEIGHT, WIDTH)
        self.food_pheromone = PheromoneGrid(HEIGHT, WIDTH)
        self.home_pheromone = PheromoneGrid(HEIGHT, WIDTH)
        self.ant_counts = PheromoneGrid(HEIGHT, WIDTH)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self):
        for ant in self.ants:
            ant.update(self.food, self.food_pheromone, self.home_pheromone,
                       self.looking_for_food_pheromone, self.got_food_pheromone)
            self.ant_counts.add_pheromone(ant.x, ant.y, 1)
        self.food_pheromone.decay()
        self.home_pheromone.decay()
        self.looking_for_food_pheromone.decay()
        self.got_food_pheromone.decay()

    def draw(self):
        self.screen.fill(BG_COLOR)
        for f in self.food:
            f.draw(self.screen)
        pygame.draw.circle(self.screen, NEST_COLOR, (int(
            self.nest.x), int(self.nest.y)), ANT_SIZE // 2)
        for ant in self.ants:
            color = GOT_FOOD_COLOR if ant.has_food else LOOKING_FOR_FOOD_COLOR
            pygame.draw.circle(self.screen, color,
                               (int(ant.x), int(ant.y)), ANT_SIZE // 2)
        pygame.display.flip()


if __name__ == '__main__':
    App().run()
