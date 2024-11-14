"""! @file snake_game.py
@brief Implementation of the Snake game visualization using Pygame.

This module extends the base Snake game implementation with a graphical interface,
handling user input, rendering, and game loop management. It provides a playable
Snake game with score display and game over functionality.

@author Tristan Mallet
@date November 2024
"""

import pygame
from collections import deque
import numpy as np
import snake

# Initialize Pygame
pygame.init()
pygame.display.set_caption('Snake Game by Tito')

# Game display configuration
FONT_STYLE = pygame.font.SysFont("bahnschrift", 25)  #!< Default font for text rendering

# Color definitions for rendering
WHITE = (255, 255, 255)    #!< Color for snake head
YELLOW = (255, 255, 102)   #!< Unused but available for customization
BLACK = (0, 0, 0)          #!< Color for snake body and text
RED = (213, 50, 80)        #!< Color for food and game over message
GREEN = (0, 255, 0)        #!< Unused but available for customization
BLUE = (50, 153, 213)      #!< Color for background


class SnakeGame(snake.Snake):
    """! @brief Class implementing the graphical interface for Snake game.
    
    This class extends the base Snake implementation with:
    - Pygame-based visualization
    - Keyboard input handling
    - Score display
    - Game over screen
    - Game loop management
    """

    def __init__(self, render=None):
        """! Initialize the graphical Snake game instance.
        
        Sets up:
        - Pygame display window
        - Game clock for consistent speed
        - Input buffer for smooth controls
        - Initial game state from parent class
        
        @param render Optional parameter for rendering configuration (unused)
        """
        super().__init__()
        self.display = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.close_window = False    #!< Flag to control game window closure
        self.key_buffer = deque()    #!< Buffer for keyboard input processing

    def display_score(self, score):
        """! Render the current score on screen.
        
        Displays the player's current score in the top-left corner.
        
        @param score Current game score to display
        """
        value = FONT_STYLE.render("Your Score: " + str(score), True, BLACK)
        self.display.blit(value, [0, 0])

    def draw_snake(self):
        """! Render the snake on screen.
        
        Draws the snake with:
        - Black rectangles for body segments
        - White rectangle for head
        - Each segment sized according to SNAKE_BLOCK
        """
        for segment in self.snake_list[:-1]:
            pygame.draw.rect(self.display, BLACK, 
                           [segment[0], segment[1], self.SNAKE_BLOCK, self.SNAKE_BLOCK])
        # Draw snake head in white for visibility
        pygame.draw.rect(self.display, WHITE, 
                        [self.snake_list[-1][0], self.snake_list[-1][1], 
                         self.SNAKE_BLOCK, self.SNAKE_BLOCK])

    def display_message(self, msg, color):
        """! Display a centered message on screen.
        
        Used for game over and other important messages.
        
        @param msg Text message to display
        @param color RGB tuple defining text color
        """
        mesg = FONT_STYLE.render(msg, True, color)
        self.display.blit(mesg, [self.SCREEN_WIDTH / 6, self.SCREEN_HEIGHT / 3])

    def handle_events(self):
        """! Process Pygame events.
        
        Handles:
        - Window close requests
        - Keyboard input events
        Events are stored in key_buffer for later processing.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_window = True
            if event.type == pygame.KEYDOWN:
                self.key_buffer.append(event.key)

    def process_key_buffer(self):
        """! Process buffered keyboard inputs.
        
        Handles directional inputs with constraints:
        - Cannot reverse direction (e.g., right to left)
        - Updates displacement vector based on input
        - Processes one input per game tick
        """
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
        """! Main game loop.
        
        Manages the game flow including:
        - Game over state handling
        - Event processing
        - Game state updates
        - Screen rendering
        - Frame rate control
        """
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

            # Render game state
            self.display.fill(BLUE)
            pygame.draw.rect(self.display, RED, 
                           [self.food_position[0], self.food_position[1], 
                            self.SNAKE_BLOCK, self.SNAKE_BLOCK])
            self.draw_snake()
            self.display_score(self.snake_length - 1)
            
            pygame.display.update()
            self.clock.tick(self.SNAKE_SPEED)

        pygame.quit()
        quit()


if __name__ == "__main__":
    game = SnakeGame()
    game.play()
