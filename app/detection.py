import cv2
from app.face_auth import recognize_face

# Load Haarcascade for face detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )

    results = []

    for (x, y, w, h) in faces:
        face_crop = frame[y:y+h, x:x+w]

        person_name = recognize_face(face_crop)

        results.append({
            "name": person_name,
            "box": (x, y, w, h)
        })

    return results