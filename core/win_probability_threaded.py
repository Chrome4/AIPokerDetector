import random
from core.evaluator import evaluate_hand

CARD_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
CARD_SUITS = "CDHS"
ALL_CARDS = [r + s for r in CARD_RANKS for s in CARD_SUITS]


def simulate_win_probability(player_cards, community_cards, num_opponents=3, simulations=10000, progress_callback=None):
    """
    Monte Carlo win rate simulation.
    Simulates random outcomes to estimate win % for given hole cards.

    Args:
        player_cards (list): Player's 2 hole cards (e.g., ['AS', 'KH']).
        community_cards (list): Known community cards (0–5 cards).
        num_opponents (int): Number of opponents to simulate against.
        simulations (int): Number of random simulations to run.
        progress_callback (function, optional): Optional external progress reporter.

    Returns:
        float: Estimated win percentage (0–100).
    """
    if len(player_cards) < 2:
        return 0.0

    known_cards = set(player_cards + community_cards)
    deck = [c for c in ALL_CARDS if c not in known_cards]

    wins = 0

    for _ in range(simulations):
        random.shuffle(deck)

        # Draw remaining community cards
        needed = 5 - len(community_cards)
        sim_community = community_cards + deck[:needed]

        # Opponent hands
        idx = needed
        opponents = []
        for _ in range(num_opponents):
            opponents.append([deck[idx], deck[idx + 1]])
            idx += 2

        # Evaluate player hand
        my_score, _ = evaluate_hand(player_cards + sim_community)

        # Evaluate all opponents
        best_opp_score = 0
        for opp in opponents:
            score, _ = evaluate_hand(opp + sim_community)
            if score > best_opp_score:
                best_opp_score = score

        if my_score >= best_opp_score:
            wins += 1

    return round((wins / simulations) * 100, 2)
