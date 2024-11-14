"""! @file snake_ai.py
@brief Implementation of a Snake game AI using Q-learning.

This module implements an AI agent that learns to play the Snake game using Q-learning,
a model-free reinforcement learning algorithm. The agent learns to maximize its reward
by collecting food while avoiding collisions with walls and itself.

@author Tristan Mallet
@date November 2024
"""

import numpy as np
import random
import pygame
import argparse
import cv2
from datetime import datetime
import json
import snake

class SnakeAI(snake.Snake):
    """! @brief AI agent that learns to play Snake using Q-learning.
    
    This class extends the basic Snake game with Q-learning capabilities.
    The agent learns optimal actions based on state observations and rewards.
    """

    # Define possible actions
    STRAIGHT = 0  #!< Continue in current direction
    RIGHT = 1     #!< Turn right
    LEFT = 2      #!< Turn left

    class AlgoSettings:
        """! @brief Configuration settings for the Q-learning algorithm."""

        def __init__(self,
                     learning_rate=0.001,      #!< Rate at which the agent learns from new experiences
                     discount_factor=0.99,      #!< Weight given to future rewards vs immediate rewards
                     exploration_rate=1.0,      #!< Initial probability of taking random actions
                     exploration_decay=0.997,   #!< Rate at which exploration decreases
                     food_reward=150,          #!< Reward for collecting food
                     death_penalty=-150,       #!< Penalty for dying
                     distance_reward=2):        #!< Reward based on distance to food
            """! Initialize algorithm settings with default values."""
            self.learning_rate = learning_rate
            self.discount_factor = discount_factor
            self.exploration_rate = exploration_rate
            self.exploration_decay = exploration_decay
            self.food_reward = food_reward
            self.death_penalty = death_penalty
            self.distance_reward = distance_reward

    def __init__(self):
        """! Initialize the Snake AI agent."""
        # Initialize Q-learning parameters
        self.algo_settings = self.AlgoSettings()
        self.q_table = {}  #!< State-action value table

        self.reset()

    def reset(self):
        """! Reset the game state and learning parameters."""
        super().__init__()

        # Reset reward tracking
        self.food_distance = self.compute_food_distance()
        self.cumul_reward = 0
        self.last_action = "epsilon"

        self.displacement = np.array([0, -self.SNAKE_BLOCK])

    def compute_food_distance(self):
        """! Calculate Euclidean distance to food.
        @return float: Distance to food
        """
        return np.linalg.norm(self.food_position - self.position)

    def get_state(self, display=False):
        """! Get the current state representation.
        
        The state is represented as two bitfields:
        1. Food location relative to snake (4 bits)
        2. Danger locations (3 bits)
        
        @param display: Whether to print state information
        @return tuple: (food_bits, danger_bits)
        """
        # Bitfield masks for food positions
        FOOD_FRONT = 1 << 0   #!< 0b0001
        FOOD_BACK  = 1 << 1   #!< 0b0010
        FOOD_RIGHT = 1 << 2   #!< 0b0100
        FOOD_LEFT  = 1 << 3   #!< 0b1000

        # Bitfield masks for danger positions
        DANGER_STRAIGHT = 1 << 0   #!< 0b001
        DANGER_RIGHT    = 1 << 1   #!< 0b010
        DANGER_LEFT     = 1 << 2   #!< 0b100
    
        # Calculate normalized direction vectors
        direction = self.displacement / np.linalg.norm(self.displacement)
        food_vector = self.food_position - self.position
        food_distance = np.linalg.norm(food_vector)
        
        food_direction = food_vector / food_distance if food_distance != 0 else np.array([0, 0])
            
        # Calculate relative food position using dot and cross products
        forward_component = np.dot(direction, food_direction)
        right_component = np.cross(direction, food_direction)
        
        # Build food position bitfield
        food_bits = 0
        if forward_component > 0:
            food_bits |= FOOD_FRONT
        else:
            food_bits |= FOOD_BACK
        if right_component > 0:
            food_bits |= FOOD_RIGHT
        else:
            food_bits |= FOOD_LEFT
            
        # Build danger detection bitfield
        danger_bits = 0
        if self._is_danger(self.displacement):
            danger_bits |= DANGER_STRAIGHT
        if self._is_danger(self._turn_right()):
            danger_bits |= DANGER_RIGHT
        if self._is_danger(self._turn_left()):
            danger_bits |= DANGER_LEFT

        if display:
            self._display_state_info(food_bits, danger_bits)

        return (food_bits, danger_bits)

    def _display_state_info(self, food_bits, danger_bits):
        """! Helper method to display state information.
        @param food_bits: Bitfield representing food positions
        @param danger_bits: Bitfield representing danger positions
        """
        print("Food positions:")
        print(f"  Front: {'Yes' if food_bits & (1 << 0) else 'No'}")
        print(f"  Back:  {'Yes' if food_bits & (1 << 1) else 'No'}")
        print(f"  Right: {'Yes' if food_bits & (1 << 2) else 'No'}")
        print(f"  Left:  {'Yes' if food_bits & (1 << 3) else 'No'}")
        
        print("\nDanger positions:")
        print(f"  Straight: {'Yes' if danger_bits & (1 << 0) else 'No'}")
        print(f"  Right:    {'Yes' if danger_bits & (1 << 1) else 'No'}")
        print(f"  Left:     {'Yes' if danger_bits & (1 << 2) else 'No'}")

    def _turn_right(self):
        """! Calculate displacement vector for right turn.
        @return ndarray: New displacement vector
        """
        return np.array([-self.displacement[1], self.displacement[0]])

    def _turn_left(self):
        """! Calculate displacement vector for left turn.
        @return ndarray: New displacement vector
        """
        return np.array([self.displacement[1], -self.displacement[0]])

    def _apply_action(self, action):
        """! Apply the chosen action to update snake's direction.
        @param action: The action to apply (STRAIGHT, RIGHT, or LEFT)
        """
        if action == self.RIGHT:
            self.displacement = self._turn_right()
        elif action == self.LEFT:
            self.displacement = self._turn_left()

    def _is_danger(self, direction):
        """! Check if moving in given direction leads to collision.
        @param direction: Direction vector to check
        @return bool: True if danger detected, False otherwise
        """
        test_pos = self.position + direction
        # Check wall collision
        if (test_pos[0] < 0 or test_pos[0] >= self.SCREEN_WIDTH
                or test_pos[1] < 0 or test_pos[1] >= self.SCREEN_HEIGHT):
            return True

        # Check self collision
        return any(np.array_equal(test_pos, segment) for segment in self.snake_list[:-1])

    def choose_action(self, state):
        """! Select action using epsilon-greedy strategy.
        
        Either explores randomly or exploits learned Q-values.
        
        @param state: Current state tuple
        @return int: Chosen action (STRAIGHT, RIGHT, or LEFT)
        """
        if random.random() < self.algo_settings.exploration_rate:
            self.last_action = "epsilon"
            return random.choice([self.STRAIGHT, self.RIGHT, self.LEFT])

        self.last_action = "q_table"
        state_key = str(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {
                self.STRAIGHT: 0,
                self.RIGHT: 0,
                self.LEFT: 0
            }

        return max(self.q_table[state_key], key=self.q_table[state_key].get)

    def record_frame(self, mode):
        """! Capture current game frame for video recording.
        @param mode: Pygame display surface
        @return ndarray: Frame data in BGR format
        """
        frame_data = pygame.surfarray.array3d(mode)
        frame_data = frame_data.swapaxes(0, 1)
        return cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)

    def create_video(self, frames, filename, fps=10):
        """! Create video from recorded frames.
        @param frames: List of frame data
        @param filename: Output video filename
        @param fps: Frames per second
        """
        if not frames:
            return
        
        height, width = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        
        for frame in frames:
            out.write(frame)
        out.release()

    def train(self, num_episodes=100, display=False):
        """! Train the agent using Q-learning.
        
        @param num_episodes: Number of training episodes
        @param display: Whether to display the game
        @return tuple: (Q-table, list of scores)
        """
        scores = []
        
        if display:
            pygame.init()
            pygame.display.set_caption('Training')
            font = pygame.font.SysFont("bahnschrift", 25)
            mode = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        for episode in range(num_episodes):
            # Setup display for final episode
            if (episode == num_episodes - 1) and not display:
                pygame.init()
                pygame.display.set_caption('Training')
                font = pygame.font.SysFont("bahnschrift", 25)
                mode = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                frames = []

            self.reset()

            while not self.game_over:
                # Get current state and choose action
                current_state = self.get_state()
                action = self.choose_action(current_state)

                # Execute action and observe results
                self._apply_action(action)
                self.process()

                # Update Q-learning parameters
                new_state = self.get_state()
                reward = self._calculate_reward()
                self.cumul_reward += reward

                self._update_q_table(current_state, action, reward, new_state)

                # Handle display and recording
                if display or (episode == num_episodes - 1):
                    self.display_training(font, mode)
                    if (episode == num_episodes - 1):
                        frames.append(self.record_frame(mode))

            # Record and display episode statistics
            score = self.snake_length - 1
            scores.append(score)

            print(f"Episode {episode} done: Score = {score}, last cumulative reward = {self.cumul_reward}, "
                  f"exploration rate = {self.algo_settings.exploration_rate}, last action: {self.last_action}")

            if episode % 10 == 0:
                avg_score = sum(scores[-10:]) / min(10, len(scores))
                print(f"Avg Score (last 10) = {avg_score:.1f}")

            # Update exploration rate
            self.algo_settings.exploration_rate *= self.algo_settings.exploration_decay
        
        # Save final episode video
        if frames:
            timestamp = datetime.now().strftime("%d_%H%M%S")
            self.create_video(frames, f'last_game_{timestamp}.mp4')

        return self.q_table, scores

    def _calculate_reward(self):
        """! Calculate the reward for the current state.
        
        Rewards are assigned based on:
        - Death: Large negative penalty
        - Eating food: Large positive reward
        - Moving: Small reward/penalty based on change in distance to food
        
        @return float: Calculated reward value
        """
        food_distance = self.compute_food_distance()
        
        if self.game_over:
            return self.algo_settings.death_penalty
        
        if self.is_eating:
            return self.algo_settings.food_reward
                
        # Calculate reward based on whether snake moved closer to or further from food
        distance_delta = self.food_distance - food_distance
        reward = distance_delta * self.algo_settings.distance_reward
        
        self.food_distance = food_distance
        return reward

    def _update_q_table(self, state, action, reward, next_state):
        """! Update Q-values using the Q-learning update rule.
        
        Q(s,a) = Q(s,a) + α * (R + γ * max(Q(s',a')) - Q(s,a))
        where:
        - α is the learning rate
        - γ is the discount factor
        - R is the reward
        - s' is the next state
        - a' is the next action
        
        @param state: Current state tuple
        @param action: Action taken
        @param reward: Reward received
        @param next_state: Resulting state tuple
        """
        state_key = str(state)
        next_state_key = str(next_state)

        # Initialize Q-values if states haven't been seen before
        if state_key not in self.q_table:
            self.q_table[state_key] = {
                self.STRAIGHT: 0,
                self.RIGHT: 0,
                self.LEFT: 0
            }

        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {
                self.STRAIGHT: 0,
                self.RIGHT: 0,
                self.LEFT: 0
            }

        # Apply Q-learning update rule
        current_q = self.q_table[state_key][action]
        max_next_q = max(self.q_table[next_state_key].values())
        new_q = current_q + self.algo_settings.learning_rate * (
            reward + self.algo_settings.discount_factor * max_next_q -
            current_q)

        self.q_table[state_key][action] = new_q

    def display_training(self, font, mode):
        """! Display the current game state during training.
        
        @param font: Pygame font object for score display
        @param mode: Pygame display surface
        """
        # Define colors
        WHITE = (255, 255, 255)  #!< Color for snake head
        BLACK = (0, 0, 0)        #!< Color for snake body and score
        RED = (213, 50, 80)      #!< Color for food
        BLUE = (50, 153, 213)    #!< Color for background

        def display_score(score, mode):
            """! Helper function to display the current score.
            @param score: Current game score
            @param mode: Pygame display surface
            """
            value = font.render("Your Score: " + str(score), True, BLACK)
            mode.blit(value, [0, 0])

        def draw_snake(mode):
            """! Helper function to draw the snake.
            @param mode: Pygame display surface
            """
            # Draw snake body segments in black
            for segment in self.snake_list[:-1]:
                pygame.draw.rect(mode, BLACK, [
                    segment[0], segment[1], self.SNAKE_BLOCK, self.SNAKE_BLOCK
                ])
            # Draw snake head in white
            pygame.draw.rect(mode, WHITE, [
                self.snake_list[-1][0], self.snake_list[-1][1],
                self.SNAKE_BLOCK, self.SNAKE_BLOCK
            ])

        # Update display
        mode.fill(BLUE)
        pygame.draw.rect(mode, RED, [
            self.food_position[0], self.food_position[1], self.SNAKE_BLOCK,
            self.SNAKE_BLOCK
        ])
        draw_snake(mode)
        display_score(self.snake_length - 1, mode)
        pygame.display.update()


if __name__ == "__main__":
    """! Main entry point for training the Snake AI.
    
    Command line arguments:
    - episodes (-e): Number of training episodes (default: 1000)
    - display (-d): Flag to show training visualization
    
    Outputs:
    - snake_q_table.json: Saved Q-table
    - training_progress.png: Plot of training progress (if matplotlib available)
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog='Snake RL Training',
        description='Q-Learning algorithm to learn Snake')
    parser.add_argument('-e', '--episodes', type=int, default=1000)
    parser.add_argument('-d', '--display', action='store_true')
    args = parser.parse_args()
    
    # Train the agent
    snake_ai = SnakeAI()
    q_table, scores = snake_ai.train(num_episodes=args.episodes, display=args.display)

    # Save Q-table to JSON file
    with open('snake_q_table.json', 'w') as f:
        json.dump(
            {
                k: {str(k2): v2
                    for k2, v2 in v.items()}
                for k, v in q_table.items()
            }, f)

    try:
        import matplotlib.pyplot as plt
        
        # Calculate adaptive window size for moving average
        data_length = len(scores)
        window_size = min(100, data_length // 10)  # Use 10% of data length or 100, whichever is smaller
        window_size = max(2, window_size)  # Ensure window size is at least 2

        # Calculate moving average of scores
        scores_array = np.array(scores)
        moving_avg = np.convolve(scores_array, np.ones(window_size)/window_size, mode='valid')

        # Create and save training progress plot
        plt.figure(figsize=(10, 6))
        
        # Plot raw scores with low opacity
        plt.plot(scores, label='Raw Scores', alpha=0.3, color='blue')

        # Plot moving average with high opacity
        plt.plot(range(window_size-1, len(scores)), 
                moving_avg, 
                label=f'Moving Average ({window_size} episodes)',
                color='red',
                linewidth=2)

        plt.title('Training Progress')
        plt.xlabel('Episode')
        plt.ylabel('Score')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('training_progress.png')
    except ImportError:
        print("matplotlib not installed - skipping progress plot")
