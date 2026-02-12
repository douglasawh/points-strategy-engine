import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Callable


# =========================
# Core Data Models
# =========================

@dataclass
class Currency:
    name: str
    transfer_partners: List[str]


@dataclass
class CreditCard:
    name: str
    currency: str
    signup_bonus: int
    annual_fee: int
    earning_rate: float  # points per dollar
    spend_assumption: float  # yearly spend


@dataclass
class Redemption:
    name: str
    program: str
    points_required: int
    cash_price: float
    availability_probability: float  # modeled uncertainty


@dataclass
class Strategy:
    name: str
    cards: List[CreditCard]


# =========================
# Tokyo 2027 Goal Modeling
# =========================

TOKYO_FLIGHT_ANA = Redemption(
    name="ANA Business via Transfer",
    program="ANA",
    points_required=150000,
    cash_price=6000,
    availability_probability=0.6
)

TOKYO_FLIGHT_DELTA = Redemption(
    name="Delta One Direct MSP-HND",
    program="Delta",
    points_required=320000,
    cash_price=6000,
    availability_probability=0.75
)

TOKYO_HOTEL_PARK_HYATT = Redemption(
    name="Park Hyatt Tokyo 5 Nights",
    program="Hyatt",
    points_required=175000,
    cash_price=3500,
    availability_probability=0.7
)

TOKYO_HOTEL_ANDAZ = Redemption(
    name="Andaz Tokyo 5 Nights",
    program="Hyatt",
    points_required=140000,
    cash_price=3000,
    availability_probability=0.8
)


ALL_REDEMPTIONS = [
    TOKYO_FLIGHT_ANA,
    TOKYO_FLIGHT_DELTA,
    TOKYO_HOTEL_PARK_HYATT,
    TOKYO_HOTEL_ANDAZ
]


# =========================
# Strategy Definitions
# =========================

CHASE_SAPPHIRE = CreditCard(
    name="Chase Sapphire Preferred",
    currency="Ultimate Rewards",
    signup_bonus=60000,
    annual_fee=95,
    earning_rate=1.5,
    spend_assumption=20000
)

AMEX_PLAT = CreditCard(
    name="Amex Platinum",
    currency="Membership Rewards",
    signup_bonus=80000,
    annual_fee=695,
    earning_rate=1.2,
    spend_assumption=20000
)

DELTA_RESERVE = CreditCard(
    name="Delta Reserve",
    currency="Delta",
    signup_bonus=70000,
    annual_fee=550,
    earning_rate=1.3,
    spend_assumption=20000
)


STRATEGIES = [
    Strategy("Chase + Hyatt Focus", [CHASE_SAPPHIRE]),
    Strategy("Amex + ANA Focus", [AMEX_PLAT]),
    Strategy("Delta Loyalty Focus", [DELTA_RESERVE]),
    Strategy("Hybrid Chase + Amex", [CHASE_SAPPHIRE, AMEX_PLAT]),
]


# =========================
# Engine Logic
# =========================

YEARS_UNTIL_TRIP = 2


def simulate_points(strategy: Strategy):
    balances = {}

    for card in strategy.cards:
        earned = (
            card.signup_bonus +
            card.earning_rate * card.spend_assumption * YEARS_UNTIL_TRIP
        )

        balances.setdefault(card.currency, 0)
        balances[card.currency] += earned

    return balances


def redemption_value(redemption: Redemption):
    return redemption.cash_price / redemption.points_required


def simulate_redemption_success(redemption: Redemption):
    return random.random() < redemption.availability_probability


def strategy_simulation(strategy: Strategy, simulations=1000):
    total_value = 0
    success_count = 0
    total_fees = sum(card.annual_fee * YEARS_UNTIL_TRIP for card in strategy.cards)

    for _ in range(simulations):
        balances = simulate_points(strategy)
        simulation_value = 0
        success = True

        for redemption in ALL_REDEMPTIONS:
            if simulate_redemption_success(redemption):
                simulation_value += redemption.cash_price
            else:
                success = False

        total_value += simulation_value

        if success:
            success_count += 1

    expected_value = total_value / simulations
    success_probability = success_count / simulations

    utility_score = expected_value - total_fees

    return {
        "strategy": strategy.name,
        "expected_value": round(expected_value, 2),
        "success_probability": round(success_probability, 3),
        "fees": total_fees,
        "utility_score": round(utility_score, 2)
    }


# =========================
# Run Engine
# =========================

def run_engine():
    print("\n=== Tokyo 2027 Strategy Simulation ===\n")

    results = []

    for strategy in STRATEGIES:
        result = strategy_simulation(strategy, simulations=2000)
        results.append(result)

    results.sort(key=lambda x: x["utility_score"], reverse=True)

    for r in results:
        print(f"Strategy: {r['strategy']}")
        print(f"  Expected Trip Value: ${r['expected_value']}")
        print(f"  Success Probability: {r['success_probability']*100}%")
        print(f"  Total Fees: ${r['fees']}")
        print(f"  Utility Score: {r['utility_score']}")
        print("-" * 40)


if __name__ == "__main__":
    run_engine()

