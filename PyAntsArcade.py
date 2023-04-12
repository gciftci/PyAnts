import random
import arcade
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FOOD_SIZE = 15
NEST_SIZE = 10
FOOD_COLOR = arcade.color.GREEN
NEST_COLOR = arcade.color.BROWN
ANT_COLOR = arcade.color.BLACK
LOOKING_FOR_FOOD_COLOR = arcade.color.BLUE
FOUND_FOOD_COLOR = arcade.color.ORANGE
TRAIL_DECAY_RATE = 0.0005
ANT_SIZE = 5


def check_for_collision(circle1, circle2):
    dx = circle1.center_x - circle2.center_x
    dy = circle1.center_y - circle2.center_y
    distance = math.sqrt(dx * dx + dy * dy)
    return distance < (circle1.width / 2 + circle2.width / 2)


class Nest:
    def __init__(self):
        self.center_x = random.randrange(NEST_SIZE, SCREEN_WIDTH - NEST_SIZE)
        self.center_y = random.randrange(NEST_SIZE, SCREEN_HEIGHT - NEST_SIZE)
        self.width = NEST_SIZE
        self.height = NEST_SIZE
        self.color = NEST_COLOR

    def draw(self):
        arcade.draw_circle_filled(
            self.center_x, self.center_y, self.width/2, self.color)


class Food:
    def __init__(self):
        self.center_x = random.randrange(FOOD_SIZE, SCREEN_WIDTH - FOOD_SIZE)
        self.center_y = random.randrange(FOOD_SIZE, SCREEN_HEIGHT - FOOD_SIZE)
        self.width = FOOD_SIZE
        self.height = FOOD_SIZE
        self.color = FOOD_COLOR

    def draw(self):
        arcade.draw_circle_filled(
            self.center_x, self.center_y, self.width/2, self.color)


class Ant(arcade.Sprite):
    def __init__(self, nest):
        super().__init__()
        self.center_x = nest.center_x
        self.center_y = nest.center_y
        self.width = 2
        self.height = 2
        self.color = ANT_COLOR
        self.direction = random.uniform(0, 2 * 3.141592653589793)
        self.speed = 3
        self.trail = []
        self.found_food = False

    def update(self):
        if self.found_food:
            self.follow_trail()
        else:
            self.wander()

    def wander(self):
        if random.random() < 0.2:
            self.direction += random.uniform(-0.5, 0.5)
        self.center_x += self.speed * math.cos(self.direction)
        self.center_y += self.speed * math.sin(self.direction)
        self.center_x = max(ANT_SIZE, min(
            SCREEN_WIDTH - ANT_SIZE, self.center_x))
        self.center_y = max(ANT_SIZE, min(
            SCREEN_HEIGHT - ANT_SIZE, self.center_y))
        self.leave_trail(LOOKING_FOR_FOOD_COLOR)

    def follow_trail(self):
        if self.trail:
            self.direction = math.atan2(
                self.trail[-1][1] - self.center_y, self.trail[-1][0] - self.center_x)
            self.center_x += self.speed * math.cos(self.direction)
            self.center_y += self.speed * math.sin(self.direction)
            self.center_x = max(ANT_SIZE, min(
                SCREEN_WIDTH - ANT_SIZE, self.center_x))
            self.center_y = max(ANT_SIZE, min(
                SCREEN_HEIGHT - ANT_SIZE, self.center_y))
            self.leave_trail(FOUND_FOOD_COLOR)

    def leave_trail(self, color):
        self.trail.append((self.center_x, self.center_y, color))

        # Decay old parts of the trail
        i = 0
        while i < len(self.trail):
            x, y, c = self.trail[i]
            new_c = (
                max(0, int(c[0] * (1 - TRAIL_DECAY_RATE))),
                max(0, int(c[1] * (1 - TRAIL_DECAY_RATE))),
                max(0, int(c[2] * (1 - TRAIL_DECAY_RATE))),
            )
            self.trail[i] = (x, y, new_c)
            if sum(new_c) < 0.1:
                self.trail.pop(i)
            else:
                i += 1

    def draw(self):
        arcade.draw_circle_filled(
            self.center_x, self.center_y, self.width/2, self.color)


class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Ants")
        self.ant_list = arcade.SpriteList()
        self.nest = Nest()

        self.food_list = []
        # Create 5 random food sources
        for _ in range(5):
            food = Food()
            while check_for_collision(self.nest, food):
                food = Food()
            self.food_list.append(food)

        for _ in range(10):
            ant = Ant(self.nest)
            self.ant_list.append(ant)

    def setup(self):
        # Set up your game here
        pass

    def on_draw(self):
        arcade.start_render()

        self.nest.draw()
        for food in self.food_list:
            food.draw()

        for ant in self.ant_list:
            for x, y, color in ant.trail:
                arcade.draw_circle_filled(x, y, ANT_SIZE / 2, color)

        for ant in self.ant_list:
            ant.draw()

    def update(self, delta_time):
        self.all_sprites_list.update()
        for ant in self.ant_list:
            if not ant.found_food:
                for food in self.food_list:
                    if arcade.check_for_collision(ant, food):
                        ant.found_food = True
                        ant.trail = []
                        ant.color = FOUND_FOOD_COLOR
                        break
                else:
                    for other_ant in self.ant_list:
                        if (
                            other_ant != ant
                            and other_ant.found_food
                            and other_ant.trail
                            and arcade.check_for_collision(
                                ant, other_ant.trail[-1][3]
                            )
                        ):
                            ant.found_food = True
                            ant.trail = []
                            ant.color = FOUND_FOOD_COLOR
                            break
        for ant in self.ant_list:
            if ant.found_food and arcade.check_for_collision(ant, self.nest):
                ant.found_food = False
                ant.trail = []
                ant.color = ANT_COLOR


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
