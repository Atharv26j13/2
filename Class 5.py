import cv2
import mediapipe as mp
import numpy as np
import time
import random

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cam = cv2.VideoCapture(0)

start_time = time.time()
punch_count = 0
previous_gesture = "No Hand"

effects = []

onomatopoeia = [
    "POW!",
    "BAM!",
    "WHAM!",
    "KRAK!",
    "BOOM!",
    "THUD!",
    "SMASH!",
    "CRACK!"
]


def add_effect(x, y):
    effects.append({
        "text": random.choice(onomatopoeia),
        "x": x,
        "y": y,
        "start": time.time()
    })


while True:

    ret, frame = cam.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    elapsed = time.time() - start_time
    remaining = max(0, 60 - elapsed)

    # ---------------- GRAYSCALE ----------------

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ---------------- CANNY OUTLINE ----------------

    edges = cv2.Canny(gray, 80, 150)

    # Make edges black on white
    manga = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    # Darken areas where edges are detected
    manga[edges > 0] = (0, 0, 0)

    # ---------------- HAND DETECTION ----------------

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    gesture = "No Hand"

    fist_x = 0
    fist_y = 0

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]
        landmarks = hand.landmark

        mp_draw.draw_landmarks(
            manga,
            hand,
            mp_hands.HAND_CONNECTIONS
        )

        fingers = []

        # Thumb
        if landmarks[4].x < landmarks[3].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # Index
        if landmarks[8].y < landmarks[6].y:
            fingers.append(1)
        else:
            fingers.append(0)

        # Middle
        if landmarks[12].y < landmarks[10].y:
            fingers.append(1)
        else:
            fingers.append(0)

        # Ring
        if landmarks[16].y < landmarks[14].y:
            fingers.append(1)
        else:
            fingers.append(0)

        # Pinky
        if landmarks[20].y < landmarks[18].y:
            fingers.append(1)
        else:
            fingers.append(0)

        if fingers == [0, 0, 0, 0, 0]:

            gesture = "Fist"

            fist_x = int(landmarks[9].x * frame.shape[1])
            fist_y = int(landmarks[9].y * frame.shape[0])

    # ---------------- PUNCH DETECTION ----------------

    if gesture == "Fist" and previous_gesture != "Fist":

        punch_count += 1

        add_effect(fist_x, fist_y)

        # BLACK FLASH
        black = np.zeros_like(manga)

        cv2.imshow(
            "Manga Punch Counter",
            black
        )

        cv2.waitKey(50)

        # WHITE FLASH
        white = np.ones_like(manga) * 255

        cv2.imshow(
            "Manga Punch Counter",
            white
        )

        cv2.waitKey(50)

    previous_gesture = gesture

    # ---------------- MANGA TEXT EFFECTS ----------------

    current_time = time.time()

    new_effects = []

    for effect in effects:

        age = current_time - effect["start"]

        if age < 1:

            progress = age / 1

            scale = 2.5 * (1 - progress)

            font = cv2.FONT_HERSHEY_TRIPLEX

            thickness = max(
                1,
                int(8 * (1 - progress))
            )

            text = effect["text"]

            (text_width, text_height), baseline = cv2.getTextSize(
                text,
                font,
                scale,
                thickness
            )

            x = effect["x"] - text_width // 2
            y = effect["y"]

            # Black outline
            cv2.putText(
                manga,
                text,
                (x, y),
                font,
                scale,
                (0, 0, 0),
                thickness + 8,
                cv2.LINE_AA
            )

            # White fill
            cv2.putText(
                manga,
                text,
                (x, y),
                font,
                scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA
            )

            new_effects.append(effect)

    effects = new_effects

    # ---------------- UI ----------------

    cv2.putText(
        manga,
        f"PUNCHES: {punch_count}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        3
    )

    cv2.putText(
        manga,
        f"TIME: {remaining:.1f}",
        (30, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        3
    )

    # ---------------- TIME'S UP ----------------

    if elapsed >= 60:

        cv2.putText(
            manga,
            "TIME'S UP!",
            (30, 160),
            cv2.FONT_HERSHEY_TRIPLEX,
            1.5,
            (255, 255, 255),
            4
        )

        cv2.putText(
            manga,
            f"TOTAL PUNCHES: {punch_count}",
            (30, 220),
            cv2.FONT_HERSHEY_TRIPLEX,
            1.2,
            (255, 255, 255),
            3
        )

    cv2.imshow(
        "Manga Punch Counter",
        manga
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cam.release()
cv2.destroyAllWindows()