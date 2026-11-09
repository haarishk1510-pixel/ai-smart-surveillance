import os
import cv2
import time
import threading
import mysql.connector
import serial
import boto3
from datetime import datetime
from deepface import DeepFace
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# ================= AWS =================
S3_BUCKET = os.environ["S3_BUCKET"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

s3 = boto3.client("s3")
sns = boto3.client("sns")

# ================= SERIAL =================
ser = None
try:
    ser = serial.Serial(os.environ.get("SERIAL_PORT", "/dev/cu.usbmodem114401"), 9600, timeout=1)
    time.sleep(2)
    print("✅ Arduino connected")
except:
    print("⚠️ Arduino not connected")

# ================= DATABASE =================
db = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("EDGE_DB_USER", "root"),
    password=os.environ["EDGE_DB_PASSWORD"],
    database=os.environ.get("DB_NAME", "surveillance_db")
)
cursor = db.cursor()

# ================= CONFIG =================
KNOWN_DIR = "known_faces"
SAVE_COOLDOWN = 5

last_saved_time = 0
last_status = None


# stability counters
auth_count = 0
unauth_count = 0

known_images = [
    os.path.join(KNOWN_DIR, f)
    for f in os.listdir(KNOWN_DIR)
    if f.endswith((".jpg", ".png", ".jpeg"))
]

# ================= CAMERA =================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

# ================= BACKGROUND FUNCTION =================
def handle_event(frame, status, distance):
    try:
        filename = f"evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        os.makedirs("evidence", exist_ok=True)
        path = os.path.join("evidence", filename)

        cv2.imwrite(path, frame)
        print("📸 Saved")

        s3.upload_file(path, S3_BUCKET, filename)
        print("☁️ S3 uploaded")

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Unauthorized Alert",
            Message=f"Detected at {datetime.now()}"
        )
        print("📩 Alert sent")

        cursor.execute("""
            INSERT INTO events (name, status, distance, image_path, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, ("Unknown", status, float(distance), path, datetime.now()))
        db.commit()
        print("🗄 DB saved")

    except Exception as e:
        print("⚠️ Background error:", e)

# ================= LOOP =================
frame_count = 0
status = "UNAUTHORIZED"
best_distance = 1.0

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame_count += 1
    display = frame.copy()

    # 🔥 AI every 10 frames (faster + stable)
    if frame_count % 10 == 0:

        small = cv2.resize(frame, (320, 240))

        match_count = 0
        best_distance = 1.0

        for img in known_images[:3]:
            try:
                result = DeepFace.verify(
                    small,
                    img,
                    model_name="Facenet",
                    enforce_detection=False
                )

                dist = result["distance"]

                if dist < best_distance:
                    best_distance = dist

                if dist < 0.55:
                    match_count += 1

            except:
                pass

        # ===== STABILITY LOGIC =====
        if match_count >= 1:
            auth_count += 1
            unauth_count = 0
        else:
            unauth_count += 1
            auth_count = 0

        if auth_count >= 2:
            status = "AUTHORIZED"
        elif unauth_count >= 3:
            status = "UNAUTHORIZED"
        # else → keep previous status

    # ================= DISPLAY =================
    color = (0, 255, 0) if status == "AUTHORIZED" else (0, 0, 255)

    cv2.putText(display,
                f"{status} ({best_distance:.2f})",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                2)

    cv2.imshow("AI Surveillance", display)

    # ================= SERIAL =================
    if status != last_status:
        if ser:
            ser.write(b'A' if status == "AUTHORIZED" else b'U')
        print("Sending:", status)
        last_status = status

    # ================= EVENT =================
    current_time = time.time()

    if status == "UNAUTHORIZED" and current_time - last_saved_time > SAVE_COOLDOWN:
        threading.Thread(
            target=handle_event,
            args=(frame.copy(), status, best_distance),
            daemon=True
        ).start()

        last_saved_time = current_time

    # ================= EXIT =================
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()