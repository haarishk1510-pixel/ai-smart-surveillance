import cv2
from ultralytics import YOLO


class HumanDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(0)

    def detect_humans(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, None

        results = self.model(frame)

        human_detected = False

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = self.model.names[cls]

                if label == "person":
                    human_detected = True

        return human_detected, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
