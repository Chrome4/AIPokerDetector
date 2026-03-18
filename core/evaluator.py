from itertools import combinations

CARD_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
CARD_SUITS = "CDHS"

RANK_VALUES = {r: i + 2 for i, r in enumerate(CARD_RANKS)}

# ✅ Cache for hand evaluations (key = tuple of sorted cards)
HAND_CACHE = {}

def card_value(card):
    """Convert card label (e.g., '10C') to its rank value."""
    rank = card[:-1]
    return RANK_VALUES[rank]

def is_straight(ranks):
    """Check if ranks form a straight (including wheel A-2-3-4-5)."""
    unique_ranks = sorted(set(ranks))
    if len(unique_ranks) < 5:
        return False
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i + 4] - unique_ranks[i] == 4:
            return True
    if {14, 2, 3, 4, 5}.issubset(unique_ranks):
        return True
    return False

def evaluate_five(cards):
    """Return tuple(rank_score, name) for a 5-card hand."""
    ranks = sorted([card_value(c) for c in cards], reverse=True)
    suits = [c[-1] for c in cards]
    flush = len(set(suits)) == 1
    straight = is_straight(ranks)

    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1
    sorted_counts = sorted(rank_counts.values(), reverse=True)

    # Hand rankings
    if straight and flush:
        if ranks[0] == 14 and min(ranks) == 10:
            return (10, "Royal Flush")
        return (9, "Straight Flush")
    if sorted_counts == [4, 1]:
        return (8, "Four of a Kind")
    if sorted_counts == [3, 2]:
        return (7, "Full House")
    if flush:
        return (6, "Flush")
    if straight:
        return (5, "Straight")
    if sorted_counts == [3, 1, 1]:
        return (4, "Three of a Kind")
    if sorted_counts == [2, 2, 1]:
        return (3, "Two Pair")
    if sorted_counts == [2, 1, 1, 1]:
        return (2, "One Pair")
    return (1, "High Card")

def evaluate_hand(cards):
    """
    Evaluate the best possible 5-card hand from given cards.
    Uses caching to avoid recomputing identical hands.
    """
    if len(cards) < 5:
        return (0, "Not enough cards")

    # ✅ Sort cards for deterministic cache key
    key = tuple(sorted(cards))
    if key in HAND_CACHE:
        return HAND_CACHE[key]

    best_score = (0, "High Card")
    for combo in combinations(cards, 5):
        score = evaluate_five(combo)
        if score[0] > best_score[0]:
            best_score = score

    HAND_CACHE[key] = best_score
    return best_score
