import pygame
from collections import deque
import numpy as np

import snake

# Initialize Pygame
pygame.init()
pygame.display.set_caption('Snake Game by Tito')

# Fonts
FONT_STYLE = pygame.font.SysFont("bahnschrift", 25)

# Define Colors for rendering
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

class SnakeGame(snake.Snake):

    def __init__(self, render=None):
        super().__init__()
        self.display = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.close_window = False
        self.key_buffer = deque()

    def display_score(self, score):
        value = FONT_STYLE.render("Your Score: " + str(score), True, BLACK)
        self.display.blit(value, [0, 0])

    def draw_snake(self):
        for segment in self.snake_list[:-1]:
            pygame.draw.rect(self.display, BLACK, [segment[0], segment[1], self.SNAKE_BLOCK, self.SNAKE_BLOCK])
        # self.Snake head is white
        pygame.draw.rect(self.display, WHITE, [self.snake_list[-1][0], self.snake_list[-1][1], self.SNAKE_BLOCK, self.SNAKE_BLOCK])

    def display_message(self, msg, color):
        mesg = FONT_STYLE.render(msg, True, color)
        self.display.blit(mesg, [self.SCREEN_WIDTH / 6, self.SCREEN_HEIGHT / 3])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_window = True
            if event.type == pygame.KEYDOWN:
                self.key_buffer.append(event.key)

    def process_key_buffer(self):
        if self.key_buffer:
            key = self.key_buffer.popleft()
            if key == pygame.K_LEFT and self.displacement[0] == 0:
                self.displacement[0] = -self.SNAKE_BLOCK
                self.displacement[1] = 0
            elif key == pygame.K_RIGHT and self.displacement[0] == 0:
                self.displacement[0] = self.SNAKE_BLOCK
                self.displacement[1] = 0
            elif key == pygame.K_UP and self.displacement[1] == 0:
                self.displacement[0] = 0
                self.displacement[1] = -self.SNAKE_BLOCK
            elif key == pygame.K_DOWN and self.displacement[1] == 0:
                self.displacement[0] = 0
                self.displacement[1] = self.SNAKE_BLOCK

    def play(self):
        while not self.close_window:

            while self.game_over:
                self.display.fill(BLUE)
                self.display_message("You Lost! Press Q-Quit or C-Play Again", RED)
                self.display_score(self.snake_length - 1)
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.close_window = True
                            self.game_over = False
                        if event.key == pygame.K_c:
                            self.__init__()
                            self.play()

            self.handle_events()
            self.process_key_buffer()

            self.process()

            self.display.fill(BLUE)
            pygame.draw.rect(self.display, RED, [self.food_position[0], self.food_position[1], self.SNAKE_BLOCK, self.SNAKE_BLOCK])
            self.draw_snake()
            self.display_score(self.snake_length - 1)

            pygame.display.update()
            self.clock.tick(self.SNAKE_SPEED)

        pygame.quit()
        quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.play()