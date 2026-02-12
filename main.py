import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

# =========================
# Config
# =========================

MONTHS = 24
AIRLINE_REQUIRED = 150000
HYATT_REQUIRED = 150000
TOKYO_VALUE = 9000

GAMMA = 0.95
LR = 0.001
BATCH_SIZE = 64
MEMORY_SIZE = 50000
EPISODES = 1500
EPSILON_START = 1.0
EPSILON_END = 0.05
EPSILON_DECAY = 0.995
TARGET_UPDATE = 20

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# Card Definitions
# =========================

CARDS = {
    "chase": {"signup_bonus": 60000, "monthly": 2500, "fee": 95, "airline": True, "hyatt": True},
    "amex": {"signup_bonus": 80000, "monthly": 2000, "fee": 695, "airline": True, "hyatt": False},
    "delta": {"signup_bonus": 70000, "monthly": 2200, "fee": 550, "airline": False, "hyatt": False},
    "citi": {"signup_bonus": 0, "monthly": 300, "fee": 595, "airline": True, "hyatt": False},
}

ACTIONS = ["nothing", "chase", "amex", "delta", "cancel_citi"]
ACTION_SIZE = len(ACTIONS)

# =========================
# Environment
# =========================

class TravelEnv:

    def reset(self):
        self.month = 0
        self.cards = {"chase": 0, "amex": 0, "delta": 0, "citi": 1}
        self.points = {"chase": 0, "amex": 0, "delta": 0, "citi": 100000}
        return self._get_state()

    def _get_state(self):
        airline = sum(self.points[k] for k in self.points if CARDS[k]["airline"])
        hyatt = sum(self.points[k] for k in self.points if CARDS[k]["hyatt"])

        return np.array([
            self.month / MONTHS,
            airline / 300000,
            hyatt / 300000,
            self.cards["chase"],
            self.cards["amex"],
            self.cards["delta"],
            self.cards["citi"],
        ], dtype=np.float32)

    def step(self, action):

        reward = 0
        name = ACTIONS[action]

        # Apply
        if name in ["chase", "amex", "delta"]:
            if self.cards[name] == 0:
                self.cards[name] = 1
                self.points[name] += CARDS[name]["signup_bonus"]

        # Cancel Citi
        if name == "cancel_citi":
            self.cards["citi"] = 0

        # Monthly earn & fees
        for k in self.cards:
            if self.cards[k]:
                self.points[k] += CARDS[k]["monthly"]
                reward -= CARDS[k]["fee"] / 12

        self.month += 1
        done = self.month >= MONTHS

        if done:
            airline = sum(self.points[k] for k in self.points if CARDS[k]["airline"])
            hyatt = sum(self.points[k] for k in self.points if CARDS[k]["hyatt"])

            if airline >= AIRLINE_REQUIRED and hyatt >= HYATT_REQUIRED:
                reward += TOKYO_VALUE
            else:
                reward -= 3000

        return self._get_state(), reward, done


# =========================
# Neural Network
# =========================

class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_size)
        )

    def forward(self, x):
        return self.net(x)


# =========================
# Agent
# =========================

class Agent:

    def __init__(self, state_size, action_size):
        self.model = DQN(state_size, action_size).to(DEVICE)
        self.target = DQN(state_size, action_size).to(DEVICE)
        self.target.load_state_dict(self.model.state_dict())

        self.memory = deque(maxlen=MEMORY_SIZE)
        self.optimizer = optim.Adam(self.model.parameters(), lr=LR)
        self.epsilon = EPSILON_START

    def act(self, state):
        if random.random() < self.epsilon:
            return random.randrange(ACTION_SIZE)

        state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            q_values = self.model(state)
        return torch.argmax(q_values).item()

    def remember(self, transition):
        self.memory.append(transition)

    def replay(self):
        if len(self.memory) < BATCH_SIZE:
            return

        batch = random.sample(self.memory, BATCH_SIZE)

        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.tensor(states).to(DEVICE)
        actions = torch.tensor(actions).unsqueeze(1).to(DEVICE)
        rewards = torch.tensor(rewards).unsqueeze(1).to(DEVICE)
        next_states = torch.tensor(next_states).to(DEVICE)
        dones = torch.tensor(dones).unsqueeze(1).to(DEVICE)

        q_values = self.model(states).gather(1, actions)
        next_q = self.target(next_states).max(1)[0].unsqueeze(1)
        target = rewards + GAMMA * next_q * (1 - dones)

        loss = nn.MSELoss()(q_values, target.detach())

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target(self):
        self.target.load_state_dict(self.model.state_dict())


# =========================
# Training
# =========================

def train():

    env = TravelEnv()
    agent = Agent(state_size=7, action_size=ACTION_SIZE)

    for episode in range(EPISODES):

        state = env.reset()
        done = False

        while not done:
            action = agent.act(state)
            next_state, reward, done = env.step(action)

            agent.remember((state, action, reward, next_state, done))
            agent.replay()

            state = next_state

        if episode % TARGET_UPDATE == 0:
            agent.update_target()

        agent.epsilon = max(EPSILON_END, agent.epsilon * EPSILON_DECAY)

        if episode % 100 == 0:
            print(f"Episode {episode}, Epsilon {agent.epsilon:.3f}")

    print("Training complete.")
    return agent


# =========================
# Evaluate
# =========================

def evaluate(agent):

    env = TravelEnv()
    state = env.reset()
    done = False

    print("\n=== Learned Policy ===\n")

    while not done:
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(DEVICE)
        action = torch.argmax(agent.model(state_tensor)).item()

        print(f"Month {env.month} -> {ACTIONS[action]}")
        state, reward, done = env.step(action)

    print("\nFinal Points:", env.points)


# =========================
# Run
# =========================

if __name__ == "__main__":
    agent = train()
    evaluate(agent)

