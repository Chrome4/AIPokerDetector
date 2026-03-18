import time
import keyboard
import tkinter as tk
import os
import sys
from ui.poker_ui import PokerUI
from core.detector import detect_cards
from core.gamestate import GameState
from core.evaluator import evaluate_hand
from core.montecarlo_winprob import MonteCarloWinProb
from core.next_card_chance import calculate_next_card_chance  # ✅ NEW IMPORT

# Disable Ultralytics Hub syncing
os.environ["YOLO_HUB_SYNC"] = "False"

def main_ui():
    game_state = GameState()

    # Create Tkinter window
    root = tk.Tk()
    ui = PokerUI(root)

    # Initialize new Monte Carlo system
    win_calc = MonteCarloWinProb(frame_delay=10, simulations=10000)

    # ✅ Define reset behavior (used by button and 'R' key)
    def reset_hand():
        game_state.reset()
        ui.update_cards([], [])
        ui.update_best_hand("None")
        ui.update_win_pct(0)
        ui.update_next_card_chance(0)  # ✅ Reset next card chance display

    # Connect button callback
    ui.reset_callback = reset_hand

    # Handle window close
    def on_closing():
        try:
            root.destroy()
        except:
            pass
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    def update_loop():
        # Detect cards and get frame
        detections, frame = detect_cards(display=True)

        # Process player detections
        for label, conf in detections.get("player", []):
            game_state.add_card(label, conf)

        # Process community detections
        for label, conf in detections.get("community", []):
            game_state.add_card(label, conf)

        # Update UI cards
        ui.update_cards(game_state.player_cards, game_state.community_cards)

        # Filter out None values
        player = [c for c in game_state.player_cards if c]
        community = [c for c in game_state.community_cards if c]
        combined = player + community

        # Only calculate if enough cards are locked and stable
        if win_calc.should_calculate(player, community):
            try:
                score, name = evaluate_hand(combined)
                ui.update_best_hand(name)

                win_pct = win_calc.calculate(
                    player,
                    community,
                    num_opponents=int(ui.player_count.get())
                )
                ui.update_win_pct(round(win_pct, 2))

                # ✅ Calculate next card improvement chance
                next_chance = calculate_next_card_chance(player, community)
                ui.update_next_card_chance(next_chance)

            except Exception:
                pass
        else:
            # Not enough info yet
            if len(combined) < 5 or len(player) < 2:
                ui.update_best_hand("None")
                ui.update_win_pct(0)
                ui.update_next_card_chance(0)

        # Auto-reset if cards disappear
        game_state.check_auto_reset(detections)

        # Update video frame in UI
        if frame is not None:
            ui.update_frame(frame)

        # ✅ Manual reset hotkey (R)
        if keyboard.is_pressed("r"):
            reset_hand()

        root.after(100, update_loop)

    # Start update loop
    update_loop()
    root.mainloop()

if __name__ == "__main__":
    main_ui()
