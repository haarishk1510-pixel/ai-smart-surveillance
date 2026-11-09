import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)

    if cap.isOpened():
        print(f"Camera {i} working")

        ret, frame = cap.read()
        if ret:
            cv2.imshow(f"Camera {i}", frame)
            cv2.waitKey(1000)  # show for 1 sec

        cap.release()
        cv2.destroyAllWindows()
    else:
        print(f"Camera {i} not working")
