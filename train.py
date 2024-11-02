import numpy as np
import random
import pygame

import snake

class SnakeAI(snake.Snake):
    # Define actions
    STRAIGHT = 0
    RIGHT = 1
    LEFT = 2

    def __init__(self, learning_rate=0.1, discount_factor=0.99, exploration_rate=1.0):
        super().__init__()
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table = {}
        
        # Initialize with upward movement
        self.displacement = np.array([0, -self.SNAKE_BLOCK])

    def get_state(self):
        head = self.position
        food = self.food_position
        
        # Get food direction relative to snake's orientation
        food_vector = food - head
        current_direction = self.displacement / self.SNAKE_BLOCK  # Normalize
        
        # Calculate relative food direction using dot and cross products
        relative_x = np.dot(food_vector, current_direction)
        relative_y = np.cross(current_direction, food_vector)
        
        food_front = 1 if relative_x > 0 else 0
        food_right = 1 if relative_y > 0 else 0
        food_left = 1 if relative_y < 0 else 0
        
        # Danger detection in snake's reference frame
        danger_straight = self._is_danger(self.displacement)
        danger_right = self._is_danger(self._rotate_right(self.displacement))
        danger_left = self._is_danger(self._rotate_left(self.displacement))
        
        return (food_front, food_right, food_left,
                int(danger_straight), int(danger_right), int(danger_left))

    def _rotate_left(self, direction):
        return np.array([-direction[1], direction[0]])

    def _rotate_right(self, direction):
        return np.array([direction[1], -direction[0]])

    def _apply_action(self, action):
        if action == self.RIGHT:
            self.displacement = self._rotate_right(self.displacement)
        elif action == self.LEFT:
            self.displacement = self._rotate_left(self.displacement)

    def _is_danger(self, direction):
        test_pos = self.position + direction
        # Check wall collision
        if (test_pos[0] < 0 or test_pos[0] >= self.SCREEN_WIDTH or 
            test_pos[1] < 0 or test_pos[1] >= self.SCREEN_HEIGHT):
            return True
        
        # Check self collision
        for segment in self.snake_list[:-1]:
            if np.array_equal(test_pos, segment):
                return True
        return False

    def choose_action(self, state):
        # Epsilon-greedy action selection
        if random.random() < self.exploration_rate:
            return random.choice([self.STRAIGHT, self.RIGHT, self.LEFT])
        
        state_key = str(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {
                self.STRAIGHT: 0,
                self.RIGHT: 0,
                self.LEFT: 0
            }
        
        return max(self.q_table[state_key], key=self.q_table[state_key].get)

    def train(self, num_episodes=100, display=False):
        best_score = 0
        scores = []

        if display:
            # Initialize Pygame
            pygame.init()
            pygame.display.set_caption('Training')
            font = pygame.font.SysFont("bahnschrift", 25)
            mode = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        for episode in range(num_episodes):
            self.__init__()
            print("Episode", episode, " ...")
            
            while not self.game_over:
                current_state = self.get_state()
                action = self.choose_action(current_state)
                
                # Store previous length to detect if food was eaten
                prev_length = self.snake_length
                
                # Execute action
                self._apply_action(action)
                self.process()
                
                # Get new state and calculate reward
                new_state = self.get_state()
                reward = self._calculate_reward(prev_length)
                
                # Update Q-table
                self._update_q_table(current_state, action, reward, new_state)
                
                # Decay exploration rate
                self.exploration_rate = max(0.01, self.exploration_rate * 0.995)
                
                if display:
                    self.display_training(font, mode)
            
            score = self.snake_length - 1
            scores.append(score)
            
            if score > best_score:
                best_score = score
                print(f"New best score! Episode {episode}: Score = {score}")
            elif episode % 10 == 0:
                avg_score = sum(scores[-10:]) / min(10, len(scores))
                print(f"Episode {episode}: Score = {score}, Avg Score (last 10) = {avg_score:.1f}")

        return self.q_table, scores

    def _calculate_reward(self, prev_length):
        if self.game_over:
            return -10  # Death penalty
        elif self.snake_length > prev_length:
            return 10   # Food reward
        else:
            return -0.01  # Small step penalty

    def _update_q_table(self, state, action, reward, next_state):
        state_key = str(state)
        next_state_key = str(next_state)
        
        # Initialize Q-values if not exist
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
        
        # Q-learning update
        current_q = self.q_table[state_key][action]
        max_next_q = max(self.q_table[next_state_key].values())
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        
        self.q_table[state_key][action] = new_q

    def display_training(self, font, mode):
        WHITE = (255, 255, 255)
        YELLOW = (255, 255, 102)
        BLACK = (0, 0, 0)
        RED = (213, 50, 80)
        GREEN = (0, 255, 0)
        BLUE = (50, 153, 213)
    
        def display_score(score, mode):
            value = font.render("Your Score: " + str(score), True, BLACK)
            mode.blit(value, [0, 0])

        def draw_snake(mode):
            for segment in self.snake_list[:-1]:
                pygame.draw.rect(mode, BLACK, [segment[0], segment[1], self.SNAKE_BLOCK, self.SNAKE_BLOCK])
            # self.Snake head is white
            pygame.draw.rect(mode, WHITE, [self.snake_list[-1][0], self.snake_list[-1][1], self.SNAKE_BLOCK, self.SNAKE_BLOCK])
                        
        mode.fill(BLUE)
        pygame.draw.rect(mode, RED, [self.food_position[0], self.food_position[1], self.SNAKE_BLOCK, self.SNAKE_BLOCK])
        draw_snake(mode)
        display_score(self.snake_length - 1, mode)
        pygame.display.update()


# Usage
if __name__ == "__main__":
    snake_ai = SnakeAI()
    q_table, scores = snake_ai.train()
    
    # Save Q-table
    import json
    with open('snake_q_table.json', 'w') as f:
        json.dump({k: {str(k2): v2 for k2, v2 in v.items()} for k, v in q_table.items()}, f)
    
    # Optionally plot training progress
    try:
        import matplotlib.pyplot as plt
        plt.plot(scores)
        plt.title('Training Progress')
        plt.xlabel('Episode')
        plt.ylabel('Score')
        plt.savefig('training_progress.png')
    except ImportError:
        print("matplotlib not installed - skipping progress plot")