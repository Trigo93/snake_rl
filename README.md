
# Snake RL 🐍

This repository provides an implementation of the classic Snake game using Python and applies **reinforcement learning (RL)** to train an agent to play the game autonomously. The project uses **Q-learning** and **Deep Q Networks (DQNs)** to teach the snake agent how to maximize its score by eating food while avoiding collisions.

## Overview
The project consists of:
1. A basic **Snake game environment** built with Python.
2. A **reinforcement learning model** for training the snake agent to learn optimal moves.
3. Code for training, testing, and visualizing the trained agent's performance.

## Features
- **Classic Snake Game**: An implementation of the Snake game with adjustable game settings.
- **Reinforcement Learning Algorithms**:
  - Basic **Q-Learning** for tabular-based learning.
  - **Deep Q Networks (DQNs)** using neural networks for more complex state spaces.
- **Visualization**: Observe the agent playing the game during and after training.

## Getting Started

### Prerequisites
- **Python 3.7+**
- Required libraries:
  - `numpy`
  - `torch` (for Deep Q Networks)
  - `pygame` (for game rendering)
  - `matplotlib` (optional, for visualizations)

To install all dependencies, you can use:
```bash
pip install -r requirements.txt
```

### Installation
1. **Clone the Repository**
   ```bash
   git clone https://github.com/Trigo93/snake_rl.git
   cd snake_rl
   ```

2. **Set Up the Virtual Environment (optional)**
   It is recommended to use a virtual environment to manage dependencies.
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Game Rules
- The snake moves within a bounded area.
- The goal is to eat food that appears at random locations.
- Each time the snake eats food, its length increases by one segment.
- The game ends if the snake collides with the screen border or with its own body.

## How to Run the Game

To simply play the game manually, you can run:
```bash
python game.py
```

## Reinforcement Learning Training

### Q-Learning
Q-learning is used as a simple method to train the snake agent. The algorithm utilizes a table to store values for state-action pairs.
To train the agent with Q-learning:
```bash
python train_qlearning.py
```

### Deep Q Network (DQN)
For more complex environments where the state-action space is too large for a table, a DQN is used. It leverages a neural network to approximate Q-values for actions based on observed states.
To train the agent with DQN:
```bash
python train_dqn.py
```

### Configuration
You can adjust various parameters for the training by modifying the configuration in each training file, such as:
- Learning rate
- Discount factor (gamma)
- Exploration rate (epsilon)

## Project Structure

```
.
├── game.py                  # Main game code (for manual play)
├── snake.py                 # Snake class (handles game logic)
├── train_qlearning.py       # Q-learning training script
├── train_dqn.py             # DQN training script
├── models/                  # Directory for saved models
├── utils/                   # Helper functions and utilities
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

## Visualization
You can visualize the performance of the trained model by running:
```bash
python visualize.py
```
This script will load the trained model and render the game to show the agent’s performance.

## Future Improvements
Some potential areas for enhancement:
- Implement **Double DQN** or **Dueling DQN** for improved training stability.
- Add more complex reward functions to improve the agent’s strategic decision-making.
- Explore advanced RL algorithms like **A3C** or **PPO** for better performance.

## Contributing
Contributions are welcome! If you would like to contribute, please open a pull request or create an issue.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Inspired by the classic Snake game.
- Reinforcement Learning concepts based on standard Q-Learning and DQN implementations.

Enjoy the game and happy learning! 🚀
