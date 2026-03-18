import time
from collections import defaultdict

MIN_ACCEPT_CONF   = 0.60   # confidence gate
COOLDOWN_S        = 0.6    # don't accept same label twice too fast
MIN_STABLE_FRAMES = 2      # require this many consecutive frames before locking

class GameState:
    def __init__(self):
        self.player_cards = [None, None]
        self.community_cards = [None, None, None, None, None]
        self.locked_cards = set()
        self.missing_frames = 0
        self._last_accept = {}          # label -> timestamp
        self._streak = defaultdict(int) # label -> consecutive-frame count above conf

    def reset(self):
        self.player_cards = [None, None]
        self.community_cards = [None, None, None, None, None]
        self.locked_cards.clear()
        self.missing_frames = 0
        self._last_accept.clear()
        self._streak.clear()

    def add_card(self, label, conf):
        # confidence gate
        if conf < MIN_ACCEPT_CONF:
            return
        # cooldown
        now = time.time()
        if label in self._last_accept and (now - self._last_accept[label]) < COOLDOWN_S:
            return
        # already present?
        if label in self.locked_cards or label in self.player_cards or label in self.community_cards:
            return

        # fill player first, then community
        if None in self.player_cards:
            idx = self.player_cards.index(None)
            self.player_cards[idx] = label
        elif None in self.community_cards:
            idx = self.community_cards.index(None)
            self.community_cards[idx] = label
        else:
            return

        self.locked_cards.add(label)
        self._last_accept[label] = now

    def ingest_frame(self, detections):
        """
        Call this once per frame with the detections dict that detect_cards returns.
        It requires MIN_STABLE_FRAMES consecutive frames before locking a card.
        """
        # merge any per-bucket lists; your detect_cards currently uses "player" only
        all_dets = []
        all_dets.extend(detections.get("player", []))
        all_dets.extend(detections.get("community", []))

        seen_this_frame = set()
        for label, conf in all_dets:
            if conf < MIN_ACCEPT_CONF:
                continue
            seen_this_frame.add(label)
            self._streak[label] += 1
            if self._streak[label] >= MIN_STABLE_FRAMES:
                # lock it and reset the streak so we don't spam
                self.add_card(label, conf)
                self._streak[label] = 0

        # reset streaks for labels not seen this frame
        for lab in list(self._streak.keys()):
            if lab not in seen_this_frame:
                self._streak[lab] = 0

    def all_cards_locked(self):
        return None not in self.player_cards and None not in self.community_cards

    def check_auto_reset(self, detections, threshold_frames=2):
        if self.all_cards_locked():
            detected_count = len(detections.get("player", [])) + len(detections.get("community", []))
            if detected_count == 0:
                self.missing_frames += 1
            else:
                self.missing_frames = 0
            if self.missing_frames >= threshold_frames:
                print("♻️ Auto-resetting game state...")
                self.reset()
                self.missing_frames = 0
        else:
            self.missing_frames = 0
