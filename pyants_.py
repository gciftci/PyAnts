import itertools
import pygame
import numpy as np
from math import radians, cos, sin, degrees
from random import randint
import random
from pygame.font import Font

WIDTH = 1200
HEIGHT = 800
FPS = 60
PRATIO = 5
ANTS = 1
PHEROMONE_SIZE = 10
FOOD_COUNT = 10
FOOD_QUANT = 33
pygame.init()
clock = pygame.time.Clock()
# Set up Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Colony Optimization Visualization")

# Set up pheromone grid
pheromone_grid = np.zeros(
    (WIDTH // PHEROMONE_SIZE, HEIGHT // PHEROMONE_SIZE))


class Ant(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10)).convert()
        self.image.fill((100, 42, 42))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.angle = randint(0, 360)
        self.desired_direction = pygame.Vector2(
            cos(radians(self.angle)), sin(radians(self.angle)))
        self.state = "searching"  # Add state attribute

    def update(self):
        self.rect.x += self.desired_direction.x * 2
        self.rect.y += self.desired_direction.y * 2
        # Add randomness to the angle
        self.angle += randint(-10, 10)

        if self.rect.x < 0:
            self.rect.x = 0
            self.angle = randint(0, 360)
        elif self.rect.x > WIDTH:
            self.rect.x = WIDTH
            self.angle = randint(0, 360)

        if self.rect.y < 0:
            self.rect.y = 0
            self.angle = randint(0, 360)
        elif self.rect.y > HEIGHT:
            self.rect.y = HEIGHT
            self.angle = randint(0, 360)

        self.desired_direction = pygame.Vector2(
            cos(radians(self.angle)), sin(radians(self.angle)))

    # Add methods to Ant class
    def move_towards(self, pheromone_map, color):
        print("Ant position: ", self.rect.x, self.rect.y)
        # Get pheromone map for the specified color
        if color == "blue":
            pheromone_trails = pheromone_map["looking"]
        else:
            pheromone_trails = pheromone_map["found"]

        # Check the strength of the pheromone trail in the neighboring cells
        max_strength = 0
        best_direction = None
        for dx, dy in itertools.product(range(-1, 2), range(-1, 2)):
            x = self.rect.x + dx
            y = self.rect.y + dy
            strength = pheromone_trails.get((x, y), 0)
            if strength > max_strength:
                max_strength = strength
                best_direction = pygame.Vector2(dx, dy)

        # If a pheromone trail is detected, update the desired direction
        if best_direction:
            print("Best direction before normalize: ", best_direction)
            self.desired_direction = best_direction.normalize()
            print("Moving: ", self.desired_direction)
        else:
            print("No best direction found")

    def detect_food(self, food_sources):
        for food in food_sources:
            dx = self.rect.centerx - food.x
            dy = self.rect.centery - food.y
            distance = (dx**2 + dy**2)**0.5
            if distance <= food.quantity:
                food.quantity -= 1
                return True
        return False

    def at_nest(self, nest):
        dx = self.rect.centerx - nest.x
        dy = self.rect.centery - nest.y
        distance = (dx**2 + dy**2)**0.5
        return distance <= 20


class PheromoneTrail:
    def __init__(self, x, y, strength, color):
        self.x = x
        self.y = y
        self.strength = strength
        self.color = color


class Nest:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Food:
    def __init__(self, x, y, quantity=20):
        self.x = x
        self.y = y
        self.quantity = quantity


def create_environment():
    environment = []
    for _ in range(FOOD_COUNT):
        x = random.randint(FOOD_QUANT, WIDTH - FOOD_QUANT)
        y = random.randint(FOOD_QUANT, HEIGHT - FOOD_QUANT)
        environment.append(Food(x, y, FOOD_QUANT))
    return environment


def update_ants(ants, pheromone_trails, food_sources, nest):
    for ant in ants:
        if ant.state == "searching":
            ant.move_towards(pheromone_trails, "green")
            if ant.detect_food(food_sources):
                ant.state = "returning"
                pheromone_trails["found"][(ant.rect.x, ant.rect.y)] = 255
            else:
                pheromone_trails["looking"][(ant.rect.x, ant.rect.y)] = 255
        else:
            ant.move_towards(pheromone_trails, "blue")
            if ant.at_nest(nest):
                ant.state = "searching"
                pheromone_trails["looking"][(ant.rect.x, ant.rect.y)] = 255
            else:
                pheromone_trails["found"][(ant.rect.x, ant.rect.y)] = 255


def main():
    # Draw Enviroment
    environment = create_environment()

    # Set up nest
    nest = Nest(WIDTH // 2, HEIGHT // 2)

    # Draw Ants
    ants = pygame.sprite.Group()
    for _ in range(ANTS):
        ant = Ant((WIDTH // 2, HEIGHT // 2))
        ants.add(ant)

    # Draw PheroGrid
    pheromone_map = {
        "looking": {},
        "found": {},
    }

    # Draw FPS COunter
    font = Font(None, 24)  # Create the font object here

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        # Update and draw pheromone map
        for key in pheromone_map:
            for (x, y), value in pheromone_map[key].items():
                pheromone_map[key][(x, y)] = max(0, value - 0.7)
                if value > 0:
                    if key == "looking":
                        pygame.draw.circle(screen, (0, 0, value), (x, y), 1)
                    elif key == "found":
                        pygame.draw.circle(screen, (0, value, 0), (x, y), 1)

        # Draw food
        font = pygame.font.Font(None, 20)
        for food in environment:
            radius = food.quantity
            pygame.draw.circle(screen, (0, 255, 0),
                               (int(food.x), int(food.y)), radius)
            text = font.render(str(food.quantity), True, (255, 0, 0))
            text_rect = text.get_rect(center=(food.x, food.y))
            screen.blit(text, text_rect)
        # Draw Nest
        pygame.draw.circle(screen, (255, 0, 0), (WIDTH // 2, HEIGHT // 2), 20)

        # Call update_ants function
        update_ants(ants, pheromone_map, environment, nest)
        # Update and draw ants
        ants.update()
        ants.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
