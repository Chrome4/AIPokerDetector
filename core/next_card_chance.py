from core.evaluator import evaluate_hand

CARD_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
CARD_SUITS = "CDHS"
ALL_CARDS = [r + s for r in CARD_RANKS for s in CARD_SUITS]

def calculate_next_card_chance(player_cards, community_cards):
    """
    Calculates probability (%) that the next card improves your current hand.
    """
    if len(player_cards) != 2 or len(community_cards) < 3 or len(community_cards) >= 5:
        return 0.0

    seen = set(player_cards + community_cards)
    deck = [c for c in ALL_CARDS if c not in seen]

    # Current score
    current_score, _ = evaluate_hand(player_cards + community_cards)

    improving = 0
    total = 0

    for card in deck:
        test_hand = player_cards + community_cards + [card]
        new_score, _ = evaluate_hand(test_hand)
        if new_score > current_score:
            improving += 1
        total += 1

    return round((improving / total) * 100, 2) if total > 0 else 0.0
