from core.win_probability_threaded import simulate_win_probability

class MonteCarloWinProb:
    """
    Optimized Monte Carlo win probability calculator.
    Runs only once after cards are locked and stable for X frames.
    """

    def __init__(self, frame_delay=10, simulations=10000):
        """
        Args:
            frame_delay (int): Frames to wait after detecting a new card before recalculating.
            simulations (int): Number of Monte Carlo simulations to run.
        """
        self.last_locked_count = 0
        self.frame_counter = 0
        self.frame_delay = frame_delay
        self.simulations = simulations
        self.last_result = 0.0

    def should_calculate(self, player_cards, community_cards):
        """Returns True if enough cards are locked and stable long enough to calculate win probability."""
        locked_count = len([c for c in player_cards + community_cards if c])

        # Reset counter on new card detection
        if locked_count != self.last_locked_count:
            self.last_locked_count = locked_count
            self.frame_counter = 0
            return False

        # Only calculate if we have 5+ cards
        if locked_count >= 5:
            self.frame_counter += 1
            if self.frame_counter >= self.frame_delay:
                self.frame_counter = 0
                return True

        return False

    def calculate(self, player_cards, community_cards, num_opponents=6):
        """Runs the Monte Carlo simulation once and stores the result."""
        self.last_result = simulate_win_probability(
            player_cards,
            community_cards,
            num_opponents=num_opponents,
            simulations=self.simulations
        )
        return self.last_result
