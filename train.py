from environment import StudyEnvironment
from q_learning_agent import QLearningAgent

env = StudyEnvironment()
agent = QLearningAgent(state_size=(3, 3), action_size=3)

episodes = 500
rewards_per_episode = []

for ep in range(episodes):
    state = env.reset()
    total_reward = 0
    done = False

    while not done:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)
        agent.update(state, action, reward, next_state)
        state = next_state
        total_reward += reward

    rewards_per_episode.append(total_reward)

print("Training completed.")
