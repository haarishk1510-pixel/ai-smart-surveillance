import cv2
import os
import time

if not os.path.exists("known_faces"):
    os.makedirs("known_faces")

# Try camera index 0 first
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Camera index 0 failed, trying index 1...")
    cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("❌ Camera not detected.")
    exit()

print("Press 's' to capture your face")
print("Press 'q' to quit")

time.sleep(1)

count = 1

while True:
    ret, frame = cap.read()

    if not ret:
        print("Frame not received...")
        continue

    cv2.imshow("Register Face", frame)

    key = cv2.waitKey(1) & 0xFF

    # 🔥 PRESS 's' TO SAVE IMAGE
    if key == ord('s'):
        filename = f"known_faces/haarish_{count}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")
        count += 1

    # ❌ PRESS 'q' TO EXIT
    elif key == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()