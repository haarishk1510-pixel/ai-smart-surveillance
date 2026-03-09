import os
import cv2
import boto3
import time
import numpy as np
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
from deepface import DeepFace

# ================= LOAD ENV =================
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

print("REGION:", AWS_REGION)
print("BUCKET:", S3_BUCKET)

# ================= SETTINGS =================
KNOWN_FACES_DIR = "known_faces"
SAVE_COOLDOWN = 5
STABLE_FRAME_REQUIRED = 1

last_severity = None
stable_count = 0
last_saved_time = 0

# ================= AWS CLIENTS =================
s3 = boto3.client("s3", region_name=AWS_REGION)
sns = boto3.client("sns", region_name=AWS_REGION)

# ================= DATABASE =================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Amuthas@1",
    database="surveillance_db"
)
cursor = db.cursor()
print("Database Connected")

# ================= COSINE DISTANCE =================
def cosine_distance(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return 1 - np.dot(a, b)

# ================= LOAD KNOWN FACES =================
def load_known_faces():
    embeddings = {}
    print("Loading authorized users...")

    for file in os.listdir(KNOWN_FACES_DIR):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(file)[0].split("_")[0]
            path = os.path.join(KNOWN_FACES_DIR, file)

            try:
                rep = DeepFace.represent(
                    img_path=path,
                    model_name="ArcFace",
                    enforce_detection=False
                )
                embeddings[name] = np.array(rep[0]["embedding"])
                print("Loaded:", name)
            except:
                print("Failed:", file)

    print("Total users:", len(embeddings))
    return embeddings

known_embeddings = load_known_faces()

# ================= FACE DETECTOR =================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("🚀 AI Smart Surveillance - Final Stable Version")

# ================= MAIN LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (640, 480))

    display_frame = frame.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 6)

    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]

        try:
            rep = DeepFace.represent(
                img_path=face_img,
                model_name="ArcFace",
                enforce_detection=False
            )

            live_embedding = np.array(rep[0]["embedding"])

            min_distance = float("inf")
            matched_name = "Unknown"

            for name, known_embedding in known_embeddings.items():
                dist = cosine_distance(live_embedding, known_embedding)
                if dist < min_distance:
                    min_distance = dist
                    matched_name = name

            print("Distance:", round(min_distance, 3))

            # ================= SEVERITY LOGIC =================
            if min_distance < 0.60:
                severity = "AUTHORIZED"
                color = (0, 255, 0)

            elif min_distance < 0.75:
                severity = "SUSPICIOUS"
                color = (0, 255, 255)

            else:
                severity = "UNAUTHORIZED"
                color = (0, 0, 255)

            # Draw box
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(
                display_frame,
                f"{severity} ({min_distance:.2f})",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

            # ================= STABILITY CONTROL =================
            if severity == last_severity:
                stable_count += 1
            else:
                stable_count = 0

            last_severity = severity
            current_time = time.time()

            # ================= UNAUTHORIZED TRIGGER =================
            if (
                severity == "UNAUTHORIZED"
                and stable_count >= STABLE_FRAME_REQUIRED
                and current_time - last_saved_time > SAVE_COOLDOWN
            ):

                print("🚨 UNAUTHORIZED PERSON DETECTED")

                filename = f"evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                os.makedirs("evidence", exist_ok=True)
                local_path = os.path.join("evidence", filename)

                cv2.imwrite(local_path, frame)
                print("📸 Saved Locally:", local_path)

                try:
                    s3.upload_file(local_path, S3_BUCKET, filename)
                    print("☁ Uploaded to S3")
                except Exception as e:
                    print("S3 Error:", e)

                try:
                    sql = """
                    INSERT INTO events (name, status, distance, image_path, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    values = (
                        matched_name,
                        severity,
                        float(min_distance),
                        local_path,
                        datetime.now()
                    )
                    cursor.execute(sql, values)
                    db.commit()
                    print("🗄 Logged in Database")
                except Exception as e:
                    print("DB Error:", e)

                try:
                    sns.publish(
                        TopicArn=SNS_TOPIC_ARN,
                        Subject="🚨 Unauthorized Alert",
                        Message=f"Unauthorized person detected at {datetime.now()}"
                    )
                    print("📩 SNS Sent")
                except Exception as e:
                    print("SNS Error:", e)

                last_saved_time = current_time

        except Exception as e:
            print("Face Processing Error:", e)
            continue

    cv2.imshow("AI Smart Surveillance", display_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
