import time
import keyboard
from core.detector import detect_cards
from core.gamestate import GameState
from core.evaluator import evaluate_hand

def main():
    game_state = GameState()

    print("🔹 PokerBot Started - Press 'R' to reset hand.")
    print("Watching screen for card detections...\n")

    try:
        while True:
            # Manual reset
            if keyboard.is_pressed("r"):
                print("♻️ Resetting Game State for next hand...")
                game_state.reset()
                time.sleep(0.3)

            detected = detect_cards(display=True)

            # Add detected cards
            for label, conf in detected.get("player", []):
                game_state.add_card(label, conf)
            for label, conf in detected.get("community", []):
                game_state.add_card(label, conf)

            # Print current state
            print(f"[ Player: {game_state.player_cards} ] [ Community: {game_state.community_cards} ]")

            # Evaluate best hand if we have at least 5 cards
            combined = [c for c in (game_state.player_cards + game_state.community_cards) if c]
            if len(combined) >= 5:
                score, name = evaluate_hand(combined)
                print(f"🔹 Best Hand: {name}")

            # Auto-reset if no detections
            total_detected = len(detected.get("player", [])) + len(detected.get("community", []))
            game_state.check_auto_reset(total_detected)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🛑 Exiting PokerBot.")

if __name__ == "__main__":
    main()
