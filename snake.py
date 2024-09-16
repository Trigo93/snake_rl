import pygame
import random
from collections import deque
import numpy as np

# Initialize Pygame
pygame.init()

# Define Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Game Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SNAKE_BLOCK = 10
SNAKE_SPEED = 15

# Fonts
FONT_STYLE = pygame.font.SysFont("bahnschrift", 25)

class SnakeGame:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake Game by Tito')
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.game_close = False
        self.snake_list = []
        self.snake_length = 1
        self.position = np.array([SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2])
        self.create_food()
        self.displacement = np.zeros(2,)
        self.key_buffer = deque()

    def display_score(self, score):
        value = FONT_STYLE.render("Your Score: " + str(score), True, BLACK)
        self.display.blit(value, [0, 0])

    def draw_snake(self):
        for segment in self.snake_list[:-1]:
            pygame.draw.rect(self.display, BLACK, [segment[0], segment[1], SNAKE_BLOCK, SNAKE_BLOCK])
        # Snake head is white
        pygame.draw.rect(self.display, WHITE, [self.snake_list[-1][0], self.snake_list[-1][1], SNAKE_BLOCK, SNAKE_BLOCK])

    def display_message(self, msg, color):
        mesg = FONT_STYLE.render(msg, True, color)
        self.display.blit(mesg, [SCREEN_WIDTH / 6, SCREEN_HEIGHT / 3])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                self.key_buffer.append(event.key)

    def process_key_buffer(self):
        if self.key_buffer:
            key = self.key_buffer.popleft()
            if key == pygame.K_LEFT and self.displacement[0] == 0:
                self.displacement[0] = -SNAKE_BLOCK
                self.displacement[1] = 0
            elif key == pygame.K_RIGHT and self.displacement[0] == 0:
                self.displacement[0] = SNAKE_BLOCK
                self.displacement[1] = 0
            elif key == pygame.K_UP and self.displacement[1] == 0:
                self.displacement[0] = 0
                self.displacement[1] = -SNAKE_BLOCK
            elif key == pygame.K_DOWN and self.displacement[1] == 0:
                self.displacement[0] = 0
                self.displacement[1] = SNAKE_BLOCK

    def update_snake_position(self):
        self.position += self.displacement

    def check_collisions(self):
        if (self.position[0] >= SCREEN_WIDTH
            or self.position[0] < 0
            or self.position[1] >= SCREEN_HEIGHT
            or self.position[1] < 0):
            self.game_close = True

        for segment in self.snake_list[:-1]:
            if np.array_equal(segment, self.position):
                self.game_close = True

    def update_snake_list(self):
        self.snake_list.append([self.position[0], self.position[1]])
        if len(self.snake_list) > self.snake_length:
            del self.snake_list[0]

    def create_food(self):
        self.food_position = np.array((round(random.randrange(0, SCREEN_WIDTH - SNAKE_BLOCK) / 10.0) * 10.0, round(random.randrange(0, SCREEN_HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0))

    def eat_food(self):
        if np.array_equal(self.position, self.food_position):
            self.snake_length += 1
            self.create_food()

    def game_loop(self):
        while not self.game_over:

            while self.game_close:
                self.display.fill(BLUE)
                self.display_message("You Lost! Press Q-Quit or C-Play Again", RED)
                self.display_score(self.snake_length - 1)
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.game_over = True
                            self.game_close = False
                        if event.key == pygame.K_c:
                            self.__init__()
                            self.game_loop()

            self.handle_events()
            self.update_snake_position()
            self.check_collisions()
            self.display.fill(BLUE)
            pygame.draw.rect(self.display, RED, [self.food_position[0], self.food_position[1], SNAKE_BLOCK, SNAKE_BLOCK])
            self.update_snake_list()
            self.draw_snake()
            self.display_score(self.snake_length - 1)

            self.process_key_buffer()

            pygame.display.update()
            self.eat_food()
            self.clock.tick(SNAKE_SPEED)

        pygame.quit()
        quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.game_loop()
