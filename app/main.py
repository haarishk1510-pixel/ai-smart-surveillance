from app.detection import HumanDetector
from app.decision_engine import DecisionEngine
from app.face_auth import FaceAuthenticator


def main():
    detector = HumanDetector()
    engine = DecisionEngine()
    face_auth = FaceAuthenticator()

    try:
        while True:
            result = detector.detect()

            if result is None:
                break

            human_detected, frame = result

            if human_detected:
                authorized = face_auth.is_authorized(frame)

                if authorized:
                    print("Authorized Person Detected")
                else:
                    print("Unauthorized Person Detected")
                    engine.process(True, frame)
            else:
                print("Monitoring...")

    except KeyboardInterrupt:
        print("Stopping system...")

    finally:
        detector.release()


if __name__ == "__main__":
    main()
