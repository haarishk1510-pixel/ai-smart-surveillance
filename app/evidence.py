import os
from datetime import datetime
import cv2


def save_evidence(frame):
    folder = "static/evidence"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"evidence_{timestamp}.jpg"
    path = os.path.join(folder, filename)

    cv2.imwrite(path, frame)

    print(f"Evidence saved: {path}")
