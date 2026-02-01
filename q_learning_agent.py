import numpy as np
import random

class QLearningAgent:
    def __init__(self, state_size, action_size):
        self.q_table = np.zeros(state_size + (action_size,))
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2
        self.action_size = action_size

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, self.action_size - 1)
        return np.argmax(self.q_table[state])

    def update(self, state, action, reward, next_state):
        best_next = np.max(self.q_table[next_state])
        self.q_table[state][action] += self.alpha * (
            reward + self.gamma * best_next - self.q_table[state][action]
        )
