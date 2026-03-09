import time
from app.evidence import save_evidence


class DecisionEngine:
    def __init__(self, cooldown=5):
        self.cooldown = cooldown  # seconds
        self.last_saved_time = 0

    def process(self, human_detected, frame):
        current_time = time.time()

        if human_detected:
            if current_time - self.last_saved_time > self.cooldown:
                print("Decision: Human detected → Saving evidence")
                save_evidence(frame)
                self.last_saved_time = current_time
            else:
                print("Decision: Human detected → Cooldown active")
        else:
            print("Decision: Monitoring...")
