import random
import numpy as np

class Snake:
    """
    @brief A class representing the Snake game logic.

    The Snake class manages the snake's movement, growth, and interaction with food, as well as collision detection
    within a bounded game area.

    @details
    This class is responsible for controlling the snake's position, updating its length, creating food at random
    positions, and checking for collisions (both with the screen borders and with its own body).
    """

    # Game Settings
    SCREEN_WIDTH = 800   # The width of the game screen.
    SCREEN_HEIGHT = 600  # The height of the game screen.
    SNAKE_BLOCK = 10     # The size of each block representing a segment of the snake's body.
    SNAKE_SPEED = 15     # The speed of the snake, determining how fast it moves per tick.

    def __init__(self):
        """
        @brief Initializes a new instance of the Snake class.

        @details
        Sets up initial parameters for the game, including the snake's starting position,
        length, and the location of the first food item.
        """
        self.game_over = False               # Indicates whether the game is over due to a collision.
        self.snake_list = []                 # List storing the positions of each segment of the snake's body.
        self.snake_length = 1                # Initial length of the snake.
        self.position = np.array([self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2]) # The snake's current position on the screen.
        self.create_food()                   # Generates the first food position on the screen.
        self.displacement = np.zeros(2,)     # The current direction and speed of the snake's movement.

    def update_snake_position(self):
        """
        @brief Updates the snake's position based on its current displacement.

        @details
        Adds the displacement vector to the snake's current position, moving it
        in the specified direction.
        """
        self.position += self.displacement

    def check_collisions(self):
        """
        @brief Checks for collisions with screen borders or the snake's own body.

        @details
        Sets the `game_over` flag to True if the snake's head moves out of bounds or if it
        collides with its own body.
        """
        if (self.position[0] >= self.SCREEN_WIDTH
            or self.position[0] < 0
            or self.position[1] >= self.SCREEN_HEIGHT
            or self.position[1] < 0):
            self.game_over = True
            print("Game over: Screen border")

        for segment in self.snake_list[:-1]:
            if np.array_equal(segment, self.position):
                self.game_over = True
                print("Game over: Own body crash")

    def update_snake_list(self):
        """
        @brief Updates the list of the snake's body segments.

        @details
        Adds the snake's current head position to the list and removes the oldest position
        if the list exceeds the snake's length, ensuring it remains the correct length.
        """
        self.snake_list.append([self.position[0], self.position[1]])
        if len(self.snake_list) > self.snake_length:
            del self.snake_list[0]

    def create_food(self):
        """
        @brief Generates a new position for the food on the screen.

        @details
        Places the food at a random location within the screen bounds, snapping to
        the grid defined by `SNAKE_BLOCK` to align with the snake's movement.
        """
        self.food_position = np.array((
            round(random.randrange(0, self.SCREEN_WIDTH - self.SNAKE_BLOCK) / 10.0) * 10.0,
            round(random.randrange(0, self.SCREEN_HEIGHT - self.SNAKE_BLOCK) / 10.0) * 10.0
        ))

    def eat_food(self):
        """
        @brief Checks if the snake's head is at the food's position, indicating it has eaten the food.

        @details
        If the snake eats the food, its length increases by one segment, and new food is created.
        """
        if np.array_equal(self.position, self.food_position):
            self.snake_length += 1
            self.create_food()

    def process(self):
        """
        @brief Processes a single game tick.

        @details
        Updates the snake's position, checks for collisions, updates the snake's body segments, and
        checks if the snake has eaten the food. This method encapsulates the main game logic for each step.
        """
        self.update_snake_position()
        self.check_collisions()
        self.update_snake_list()
        self.eat_food()
