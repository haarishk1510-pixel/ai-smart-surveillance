from deepface import DeepFace
import os
import cv2
import tempfile

KNOWN_FACES_DIR = "known_faces"

authorized_images = []

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        authorized_images.append(os.path.join(KNOWN_FACES_DIR, filename))

print("Authorized images loaded:", authorized_images)


def recognize_face(frame):

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    cv2.imwrite(temp_file.name, frame)

    for auth_img in authorized_images:
        try:
            result = DeepFace.verify(
                img1_path=temp_file.name,
                img2_path=auth_img,
                enforce_detection=False
            )

            print("Distance:", result["distance"])

            if result["distance"] < 0.35:
                return os.path.splitext(os.path.basename(auth_img))[0]

        except Exception as e:
            print("Error:", e)
            continue

    return "Unauthorized"