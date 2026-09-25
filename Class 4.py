import cv2

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture Image")
        break

    avg_channels = cv2.mean(frame)

    # Extract BGR values and convert to integers
    avg_bgr = [int(x) for x in avg_channels[:3]]

    avg = 0

    binc = 135-avg_bgr[0]
    ginc = 135-avg_bgr[1]
    rinc = 135-avg_bgr[2]

    b, g, r = cv2.split(frame)

    b_tinted = cv2.add(b, binc)
    g_tinted = cv2.add(g, ginc)
    r_tinted = cv2.add(r, rinc)

    frame = cv2.merge((b_tinted, g_tinted, r_tinted))

    for i in avg_bgr:
        avg += i * (1 / 3)

    avg = int(avg)

    print(avg)

    inc = 135-avg
    bright_image = cv2.convertScaleAbs(frame, alpha=1.0+(inc/100), beta=inc*0.7) 

    cv2.imshow('Camera', bright_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()