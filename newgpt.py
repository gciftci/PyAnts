import itertools
import pygame
import random
import math

SCREEN = (2000, 1000)
FPS = 60
NEST_RADIUS = 40
FOOD_SOURCE_COUNT = 5
FOOD_SOURCE_RADIUS = 15
ANTS_COUNT = 100
ANT_SPEED = 5
ANT_TURN_RATE = 0.1
ANT_RND_RATE = 0.2
ANT_VIEW_DISTANCE = 25
ANT_COLOR = (255, 255, 255)
ANT_RADIUS = 5
PHEROMONE_DECAY_RATE = 2
PHEROMONE_SIZE = 1

pygame.init()
screen = pygame.display.set_mode(SCREEN)
clock = pygame.time.Clock()


class Ant:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.carrying_food = False

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, ANT_COLOR, (self.x, self.y), ANT_RADIUS)

    def update(self, food_sources, pheromone_grid, quadtree):
        self.move()
        self.follow_pheromone(pheromone_grid)
        self.deposit_pheromone(pheromone_grid)
        self.check_food_sources(food_sources, quadtree)

    def move(self):
        dx = ANT_SPEED * math.cos(self.angle)
        dy = ANT_SPEED * math.sin(self.angle)

        self.x += dx
        self.y += dy

        self.x = max(0, min(self.x, SCREEN[0]))
        self.y = max(0, min(self.y, SCREEN[1]))

    def follow_pheromone(self, pheromone_grid):
        pheromone_level = pheromone_grid.get_pheromone_at(self.x, self.y)
        if pheromone_level > 0:
            random_turn = random.uniform(-ANT_TURN_RATE, ANT_TURN_RATE)
        else:
            random_turn = random.uniform(-ANT_RND_RATE, ANT_RND_RATE)

        self.angle += random_turn

    def deposit_pheromone(self, pheromone_grid):
        if self.carrying_food:
            pheromone_grid.deposit(self.x, self.y, 1)

    def check_food_sources(self, food_sources, quadtree):
        for food, food_rect in quadtree.retrieve(pygame.Rect(
            self.x - ANT_RADIUS, self.y - ANT_RADIUS, 2 * ANT_RADIUS,
                2 * ANT_RADIUS)):
            food_distance = math.sqrt(
                (self.x - food.x) ** 2 + (self.y - food.y) ** 2)
            if food_distance <= food.radius and not self.carrying_food:
                self.carrying_food = True
                return

        nest_distance = math.sqrt(
            (self.x - nest.x) ** 2 + (self.y - nest.y) ** 2)
        if nest_distance <= nest.radius and self.carrying_food:
            self.carrying_food = False


class Quadtree:
    def __init__(self, x, y, width, height, max_depth, max_items):
        self.bounds = pygame.Rect(x, y, width, height)
        self.max_depth = max_depth
        self.max_items = max_items
        self.items = []
        self.children = []

    def insert(self, item, rect):
        if not self.bounds.colliderect(rect):
            return False
        if len(self.children) == 0 and (len(self.items) < self.max_items or
                                        self.max_depth <= 0):
            self.items.append((item, rect))
            return True
        if len(self.children) == 0:
            self._subdivide()
        return any(child.insert(item, rect) for child in self.children)

    def retrieve(self, rect):
        if not self.bounds.colliderect(rect):
            return []
        items = self.items.copy()
        if len(self.children) > 0:
            for child in self.children:
                items.extend(child.retrieve(rect))
        return items

    def _subdivide(self):
        x, y, width, height = self.bounds
        half_width, half_height = width // 2, height // 2
        self.children = [
            Quadtree(x, y, half_width, half_height,
                     self.max_depth - 1, self.max_items),
            Quadtree(x + half_width, y, half_width, half_height,
                     self.max_depth - 1, self.max_items),
            Quadtree(x, y + half_height, half_width, half_height,
                     self.max_depth - 1, self.max_items),
            Quadtree(x + half_width, y + half_height, half_width,
                     half_height, self.max_depth - 1, self.max_items)
        ]
        for item, rect in self.items:
            for child in self.children:
                if child.insert(item, rect):
                    break
        self.items.clear()


class FoodSource:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = FOOD_SOURCE_RADIUS

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, (255, 255, 0),
                           (self.x, self.y), self.radius)


class Nest:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = NEST_RADIUS

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)


class PheromoneGrid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size
        self.grid = [[0 for _ in range(self.grid_height)]
                     for _ in range(self.grid_width)]

    def update(self):
        self.evaporate(PHEROMONE_DECAY_RATE)

    def draw(self, screen):
        for x, y in itertools.product(range(self.grid_width), range(self.grid_height)):
            cell_value = self.grid[x][y]
            if cell_value > 0:
                rect = pygame.Rect(x * self.cell_size, y *
                                   self.cell_size, self.cell_size, self.cell_size)
                color = (0, 255, 0, min(255, int(cell_value * 255)))
                pygame.draw.rect(screen, color, rect, 0)

    def deposit(self, x, y, amount):
        grid_x, grid_y = self._convert_to_grid_coordinates(x, y)
        self.grid[grid_x][grid_y] += amount

    def get_pheromone_at(self, x, y):
        grid_x, grid_y = self._convert_to_grid_coordinates(x, y)
        return self.grid[grid_x][grid_y]

    def evaporate(self, factor):
        for x, y in itertools.product(range(self.grid_width),
                                      range(self.grid_height)):
            self.grid[x][y] *= (1 - factor)

    def _convert_to_grid_coordinates(self, x, y):
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        grid_x = max(0, min(grid_x, self.grid_width - 1))
        grid_y = max(0, min(grid_y, self.grid_height - 1))
        return grid_x, grid_y


def main():
    nest_coords = (SCREEN[0] // 2, SCREEN[1] // 2)
    global nest
    nest = Nest(*nest_coords)
    food_sources = [FoodSource(random.randint(100, SCREEN[0] - 100),
                               random.randint(100, SCREEN[1] - 100))
                    for _ in range(FOOD_SOURCE_COUNT)]
    quadtree = Quadtree(0, 0, SCREEN[0], SCREEN[1], 4, 4)
    for food in food_sources:
        food_rect = pygame.Rect(
            food.x - food.radius, food.y - food.radius,
            2 * food.radius, 2 * food.radius)
    quadtree.insert(food, food_rect)
    ants = [Ant(*nest_coords) for _ in range(ANTS_COUNT)]
    pheromone_grid = PheromoneGrid(SCREEN[0], SCREEN[1], PHEROMONE_SIZE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        nest.draw(screen)
        for food in food_sources:
            food.draw(screen)

        for ant in ants:
            ant.update(food_sources, pheromone_grid, quadtree)
            ant.draw(screen)
        pheromone_grid.evaporate(PHEROMONE_DECAY_RATE)
        pheromone_grid.update()
        pheromone_grid.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
