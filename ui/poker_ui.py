import tkinter as tk 
from tkinter import ttk
from PIL import Image, ImageTk, Image
import cv2
import os

CARD_IMAGE_PATH = "ui/cards"
CARD_SIZE = (20, 50)
CARD_SLOT_SIZE = (CARD_SIZE[0] + 4, CARD_SIZE[1] + 4)
TABLE_BG = os.path.abspath("ui/assets/table_bg.png")

class PokerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("♠ AI Poker Detector ♠")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0C0C0C")
        self.root.resizable(False, False)

        # === Load Background Image ===
        self.bg_label = tk.Label(self.root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_img_original = None
        self.bg_imgtk = None
        if os.path.exists(TABLE_BG):
            self.bg_img_original = Image.open(TABLE_BG)

        # Bind resize event
        self.root.bind("<Configure>", self._resize_bg)

        # === Main container frame ===
        main_container = tk.Frame(root, bg="#1B1B1B", highlightthickness=0)
        main_container.place(relwidth=1, relheight=1)

        self.card_images = {}
        self.placeholder_image = self.create_placeholder()

        # Title
        self.title_label = tk.Label(
            main_container, text="♠ AI Poker Detector ♠",
            font=("Arial Black", 32, "bold"), fg="#FFD700", bg="#1B1B1B"
        )
        self.title_label.pack(pady=15)

        # Main Frame
        main_frame = tk.Frame(main_container, bg="#1B1B1B")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Frame (Video + Cards)
        left_frame = tk.Frame(main_frame, bg="#1B1B1B")
        left_frame.pack(side=tk.LEFT, fill="both", expand=True)

        # Live Feed Frame with border
        self.live_feed_frame = tk.Frame(
            left_frame, bg="#000000", width=800, height=450,
            bd=4, relief="ridge", highlightbackground="#FFD700", highlightthickness=2
        )
        self.live_feed_frame.pack(pady=10)
        self.live_feed_frame.pack_propagate(False)
        self.live_feed_label = tk.Label(self.live_feed_frame, bg="#000000")
        self.live_feed_label.pack(expand=True, fill="both")

        # Community Cards
        self.community_label = tk.Label(
            left_frame, text="Community Cards:", font=("Arial", 20, "bold"), fg="#FFD700", bg="#1B1B1B"
        )
        self.community_label.pack(pady=(10, 5))
        self.community_cards_frame = tk.Frame(left_frame, bg="#1B1B1B")
        self.community_cards_frame.pack()
        self.community_labels = []
        for i in range(5):
            card = tk.Label(
                self.community_cards_frame, bg="#2E2E2E",
                width=CARD_SLOT_SIZE[0], height=CARD_SLOT_SIZE[1],
                bd=3, relief="groove", highlightbackground="#FFD700",
                highlightthickness=1, image=self.placeholder_image
            )
            card.image = self.placeholder_image
            card.pack(side=tk.LEFT, padx=4)
            self.community_labels.append(card)

        # Best Hand
        self.best_hand_label = tk.Label(
            left_frame, text="Best Hand: [None]", font=("Arial", 16, "bold"), fg="white", bg="#1B1B1B"
        )
        self.best_hand_label.pack(pady=10)

        # Player Cards
        self.player_cards_frame = tk.Frame(left_frame, bg="#1B1B1B")
        self.player_cards_frame.pack()
        self.player_labels = []
        for i in range(2):
            card = tk.Label(
                self.player_cards_frame, bg="#2E2E2E",
                width=CARD_SLOT_SIZE[0], height=CARD_SLOT_SIZE[1],
                bd=3, relief="groove", highlightbackground="#FFD700",
                highlightthickness=1, image=self.placeholder_image
            )
            card.image = self.placeholder_image
            card.pack(side=tk.LEFT, padx=4)
            self.player_labels.append(card)

        # Right Frame (Controls)
        right_frame = tk.Frame(main_frame, bg="#1B1B1B", highlightbackground="#FFD700", highlightthickness=1, bd=2, relief="ridge")
        right_frame.pack(side=tk.RIGHT, fill="y", padx=20, pady=(0, 10))

        tk.Label(right_frame, text="Player Count:", font=("Arial", 14, "bold"), fg="white", bg="#1B1B1B").pack(pady=(10, 5))
        self.player_count = ttk.Combobox(right_frame, values=[2, 3, 4, 5, 6], state="readonly", font=("Arial", 12), width=5)
        self.player_count.set(2)
        self.player_count.pack(pady=(0, 20))

        # ✅ Fixed-width labels to prevent frame expansion
        self.win_pct_label = tk.Label(
            right_frame, text="Win %: 0%", font=("Arial", 14, "bold"),
            fg="white", bg="#1B1B1B", width=25, anchor="w"
        )
        self.win_pct_label.pack(pady=5, anchor="w")

        self.next_card_chance_label = tk.Label(
            right_frame, text="Next Card Chance: 0%", font=("Arial", 14),
            fg="white", bg="#1B1B1B", width=25, anchor="w"
        )
        self.next_card_chance_label.pack(pady=5, anchor="w")

        # Pot Odds
        self.pot_odds_label = tk.Label(right_frame, text="Pot Odds: N/A", font=("Arial", 14), fg="white", bg="#1B1B1B", width=25, anchor="w")
        self.pot_odds_label.pack(pady=5, anchor="w")

        # Reset Button
        self.reset_button = tk.Button(
            right_frame, text="♻ Reset Hand", font=("Arial", 14, "bold"),
            bg="#444", fg="white", activebackground="#32CD32",
            activeforeground="black", bd=3, relief="raised",
            command=self.manual_reset_callback
        )
        self.reset_button.pack(side=tk.BOTTOM, pady=10, fill="x")

        # Hover effects for button
        self.reset_button.bind("<Enter>", lambda e: self.reset_button.config(bg="#32CD32", fg="black"))
        self.reset_button.bind("<Leave>", lambda e: self.reset_button.config(bg="#444", fg="white"))

        # Placeholder for callback connection
        self.reset_callback = None

    def manual_reset_callback(self):
        """Calls reset function from main_ui when button is pressed."""
        if self.reset_callback:
            self.reset_callback()

    def _resize_bg(self, event):
        """Resize poker felt background dynamically."""
        if self.bg_img_original:
            resized = self.bg_img_original.resize((event.width, event.height), Image.LANCZOS)
            self.bg_imgtk = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.bg_imgtk)

    def create_placeholder(self):
        placeholder = Image.new('RGB', CARD_SIZE, color=(46, 46, 46))
        return ImageTk.PhotoImage(placeholder)

    def load_card_image(self, card_name):
        if not card_name:
            return self.placeholder_image
        if card_name in self.card_images:
            return self.card_images[card_name]
        img_path = os.path.join(CARD_IMAGE_PATH, f"{card_name}.png")
        if os.path.exists(img_path):
            img = Image.open(img_path).resize(CARD_SIZE)
            imgtk = ImageTk.PhotoImage(img)
            self.card_images[card_name] = imgtk
            return imgtk
        return self.placeholder_image

    def update_frame(self, frame):
        frame_resized = cv2.resize(frame, (800, 450))
        cv2image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.live_feed_label.imgtk = imgtk
        self.live_feed_label.configure(image=imgtk)

    def update_cards(self, player_cards, community_cards):
        for idx, lbl in enumerate(self.player_labels):
            img = self.load_card_image(player_cards[idx] if idx < len(player_cards) else None)
            lbl.config(image=img)
            lbl.image = img

        for idx, lbl in enumerate(self.community_labels):
            img = self.load_card_image(community_cards[idx] if idx < len(community_cards) else None)
            lbl.config(image=img)
            lbl.image = img

    def update_best_hand(self, hand_name):
        self.best_hand_label.config(text=f"Best Hand: {hand_name}")

    def update_win_pct(self, pct):
        self.win_pct_label.config(text=f"Win %: {pct}%", fg="white")

    def set_calculating(self, is_calc):
        if is_calc:
            self.win_pct_label.config(text="Win %: Calculating...", fg="gold")
        else:
            current_text = self.win_pct_label.cget("text")
            if "Calculating" in current_text:
                self.win_pct_label.config(text="Win %: 0%", fg="white")

    def update_next_card_chance(self, pct):
        self.next_card_chance_label.config(text=f"Next Card Chance: {pct}%")
