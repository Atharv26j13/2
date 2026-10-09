
import cv2, time, numpy as np
import mediapipe as mp

H = mp.solutions.hands
TIP = H.HandLandmark

hands = H.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

draw = mp.solutions.drawing_utils
MAIN = "Gesture-Controlled Photo App"
POP = "Captured - ESC to resume"

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not access the webcam.")
    hands.close()
    exit()

cv2.namedWindow(MAIN, cv2.WINDOW_NORMAL)

paused = False
freeze = None
pinch_on = False
last_capture = 0
CAP = 3

finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]


def contrast(img, enabled):
    if enabled:
        return cv2.convertScaleAbs(img, alpha=1.5, beta=0)
    return img


def brightness(img, enabled):
    if enabled:
        return cv2.convertScaleAbs(img, alpha=1, beta=50)
    return img


def vibrant(img, enabled):
    if enabled:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        s = np.clip(s * 1.4, 0, 255)
        hsv = cv2.merge([h, s, v]).astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img


def gray(img, enabled):
    if enabled:
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    return img


while True:

    if paused:
        cv2.imshow(MAIN, freeze)
        k = cv2.waitKey(30) & 0xFF

        if k == ord("q"):
            break

        if k == 27:
            paused = False
            pinch_on = False
            try:
                cv2.destroyWindow(POP)
            except cv2.error:
                pass
            continue

        try:
            if cv2.getWindowProperty(
                POP, cv2.WND_PROP_VISIBLE
            ) <= 0:
                paused = False
                pinch_on = False
        except cv2.error:
            paused = False
            pinch_on = False

        continue

    ok, img = cap.read()
    if not ok:
        print("Error: Failed to capture image.")
        break

    img = cv2.flip(img, 1)
    res = hands.process(
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    )

    now = time.time()
    capture = False

    active = {
        "Index": False,
        "Middle": False,
        "Ring": False,
        "Pinky": False
    }

    if res.multi_hand_landmarks:
        for hand_index, hand in enumerate(res.multi_hand_landmarks):
            draw.draw_landmarks(
                img, hand, H.HAND_CONNECTIONS
            )

            lm = hand.landmark
            handedness = (
                res.multi_handedness[hand_index]
                .classification[0].label
            )

            fingers = {}

            if handedness == "Right":
                fingers["Thumb"] = (
                    lm[TIP.THUMB_TIP].x <
                    lm[TIP.THUMB_IP].x
                )
            else:
                fingers["Thumb"] = (
                    lm[TIP.THUMB_TIP].x >
                    lm[TIP.THUMB_IP].x
                )

            fingers["Index"] = (
                lm[TIP.INDEX_FINGER_TIP].y <
                lm[TIP.INDEX_FINGER_PIP].y
            )
            fingers["Middle"] = (
                lm[TIP.MIDDLE_FINGER_TIP].y <
                lm[TIP.MIDDLE_FINGER_PIP].y
            )
            fingers["Ring"] = (
                lm[TIP.RING_FINGER_TIP].y <
                lm[TIP.RING_FINGER_PIP].y
            )
            fingers["Pinky"] = (
                lm[TIP.PINKY_TIP].y <
                lm[TIP.PINKY_PIP].y
            )

            for name in active:
                active[name] = active[name] or fingers[name]

            y_text = 30 + hand_index * 160

            cv2.putText(
                img, f"{handedness} Hand",
                (10, y_text), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 0), 2
            )

            for i, name in enumerate(finger_names):
                status = "UP" if fingers[name] else "DOWN"
                color = (
                    (0, 255, 0) if fingers[name]
                    else (0, 0, 255)
                )

                cv2.putText(
                    img, f"{name}: {status}",
                    (10, y_text + 30 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, color, 2
                )

            thumb = lm[TIP.THUMB_TIP]
            index = lm[TIP.INDEX_FINGER_TIP]

            distance = np.hypot(
                thumb.x - index.x,
                thumb.y - index.y
            )

            if distance < 0.05 and not pinch_on:
                if now - last_capture >= CAP:
                    capture = True
                    last_capture = now
                pinch_on = True

            elif distance >= 0.07:
                pinch_on = False

    else:
        pinch_on = False

    out = img.copy()
    out = contrast(out, active["Index"])
    out = brightness(out, active["Middle"])
    out = vibrant(out, active["Ring"])
    out = gray(out, active["Pinky"])

    cv2.putText(
        out, "Pinch thumb + index to take photo",
        (10, out.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6, (0, 255, 0), 2
    )

    if capture:
        name = f"picture_{int(now)}.jpg"
        cv2.imwrite(name, out)
        print("Saved:", name)

        freeze = out.copy()
        paused = True
        cv2.imshow(POP, freeze)

    cv2.imshow(MAIN, out)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
