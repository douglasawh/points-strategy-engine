import random
import numpy as np
from collections import defaultdict

# =========================
# Config
# =========================

MONTHS = 24
DISCOUNT = 0.95
ALPHA = 0.1
EPSILON = 0.2
EPISODES = 70000

AIRLINE_REQUIRED = 150000
HYATT_REQUIRED = 150000
TOKYO_VALUE = 9000

# =========================
# Card Definitions
# =========================

CARDS = {
    "chase": {
        "signup_bonus": 60000,
        "monthly_earn": 2500,
        "annual_fee": 95,
        "airline_transfer": True,
        "hyatt_transfer": True
    },
    "amex": {
        "signup_bonus": 80000,
        "monthly_earn": 2000,
        "annual_fee": 695,
        "airline_transfer": True,
        "hyatt_transfer": False
    },
    "delta": {
        "signup_bonus": 70000,
        "monthly_earn": 2200,
        "annual_fee": 550,
        "airline_transfer": False,
        "hyatt_transfer": False
    },
    "citi": {
        "signup_bonus": 0,
        "monthly_earn": 300,  # LOW ongoing usage
        "annual_fee": 595,
        "airline_transfer": True,
        "hyatt_transfer": False
    }
}

ACTIONS = ["nothing", "chase", "amex", "delta", "cancel_citi"]

# =========================
# Environment
# =========================

class TravelEnv:

    def reset(self):
        self.month = 0

        self.cards = {
            "chase": False,
            "amex": False,
            "delta": False,
            "citi": True
        }

        self.points = {
            "chase": 0,
            "amex": 0,
            "delta": 0,
            "citi": 100000  # Existing balance
        }

        return self.get_state()

    def get_state(self):
        return (
            self.month,
            int(self.cards["chase"]),
            int(self.cards["amex"]),
            int(self.cards["delta"]),
            int(self.cards["citi"])
        )

    def step(self, action):

        reward = 0
        action_name = ACTIONS[action]

        # Apply for new card
        if action_name in ["chase", "amex", "delta"]:
            if not self.cards[action_name]:
                self.cards[action_name] = True
                self.points[action_name] += CARDS[action_name]["signup_bonus"]

        # Cancel Citi
        if action_name == "cancel_citi":
            self.cards["citi"] = False

        # Monthly earnings + fees
        for card_name, owned in self.cards.items():
            if owned:
                self.points[card_name] += CARDS[card_name]["monthly_earn"]
                reward -= CARDS[card_name]["annual_fee"] / 12

        self.month += 1
        done = self.month >= MONTHS

        if done:

            airline_points = sum(
                self.points[k]
                for k in self.points
                if CARDS[k]["airline_transfer"]
            )

            hyatt_points = sum(
                self.points[k]
                for k in self.points
                if CARDS[k]["hyatt_transfer"]
            )

            success = airline_points >= AIRLINE_REQUIRED and hyatt_points >= HYATT_REQUIRED

            if success:
                reward += TOKYO_VALUE
            else:
                reward -= 3000

        return self.get_state(), reward, done


# =========================
# Q Learning
# =========================

Q = defaultdict(lambda: np.zeros(len(ACTIONS)))

def choose_action(state):
    if random.random() < EPSILON:
        return random.randint(0, len(ACTIONS) - 1)
    return np.argmax(Q[state])


def train():

    env = TravelEnv()

    for episode in range(EPISODES):
        state = env.reset()
        done = False

        while not done:
            action = choose_action(state)
            next_state, reward, done = env.step(action)

            best_next = np.max(Q[next_state])

            Q[state][action] += ALPHA * (
                reward + DISCOUNT * best_next - Q[state][action]
            )

            state = next_state

    print("Training complete.\n")


# =========================
# Evaluate Learned Policy
# =========================

def evaluate():

    env = TravelEnv()
    state = env.reset()
    done = False

    print("=== Learned Strategy ===\n")

    while not done:
        action = np.argmax(Q[state])
        print(f"Month {state[0]} -> {ACTIONS[action]}")
        state, reward, done = env.step(action)

    print("\nFinal Balances:")
    for k, v in env.points.items():
        print(k, int(v))

    airline_points = sum(
        env.points[k]
        for k in env.points
        if CARDS[k]["airline_transfer"]
    )

    hyatt_points = sum(
        env.points[k]
        for k in env.points
        if CARDS[k]["hyatt_transfer"]
    )

    print("\nAirline Eligible Points:", int(airline_points))
    print("Hyatt Eligible Points:", int(hyatt_points))

    if airline_points >= AIRLINE_REQUIRED and hyatt_points >= HYATT_REQUIRED:
        print("\nTokyo is achievable!")
    else:
        print("\nTokyo NOT achievable.")


if __name__ == "__main__":
    train()
    evaluate()

