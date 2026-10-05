
import cv2, time, pyautogui
import mediapipe as mp
from collections import deque

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

mp_drawing = mp.solutions.drawing_utils

# ---------------- SETTINGS ----------------

ss = 7
sd = 1

cw, ch = 480, 360

screen_w, screen_h = pyautogui.size()

# Mouse settings
mouse_smooth = 0.4
mouse_sensitivity = 1

# Extra smoothing
smooth_points = 5
x_history = deque(maxlen=smooth_points)
y_history = deque(maxlen=smooth_points)

last_scroll = 0

# Prevent repeated clicks
previous_gesture = "none"

# Small delay after clicking
click_delay = 0.25
last_click = 0


# ---------------- LEFT HAND ----------------

def left_thumb_gesture(land):

    thumb_tip = land.landmark[
        mp_hands.HandLandmark.THUMB_TIP
    ]

    thumb_ip = land.landmark[
        mp_hands.HandLandmark.THUMB_IP
    ]

    if thumb_tip.y < thumb_ip.y:
        return "scroll_up"

    elif thumb_tip.y > thumb_ip.y:
        return "scroll_down"

    return "none"


# ---------------- FINGER DETECTION ----------------

def finger_open(land, tip, pip):

    tip_point = land.landmark[tip]
    pip_point = land.landmark[pip]

    return tip_point.y < pip_point.y


# ---------------- RIGHT HAND ----------------

def right_hand_gesture(land):

    index_open = finger_open(
        land,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_PIP
    )

    middle_open = finger_open(
        land,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP
    )

    ring_open = finger_open(
        land,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_PIP
    )

    # Index + middle + ring
    if index_open and middle_open and ring_open:
        return "right_click"

    # Index + middle
    elif index_open and middle_open:
        return "left_click"

    # Index only
    elif index_open:
        return "move"

    return "none"


# ---------------- CAMERA ----------------

cap = cv2.VideoCapture(0)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    cw
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    ch
)

cap.set(
    cv2.CAP_PROP_BUFFERSIZE,
    1
)

p_time = time.time()


# ---------------- START ----------------

print("Gesture Control Active")
print()

print("LEFT HAND:")
print("Thumb UP   = Scroll Up")
print("Thumb DOWN = Scroll Down")

print()

print("RIGHT HAND:")
print("Index only          = Move Mouse")
print("Index + Middle      = Single Left Click")
print("Index + Middle + Ring = Single Right Click")

print()

print("Press 'q' to exit")


# ---------------- MAIN LOOP ----------------

while cap.isOpened():

    success, img = cap.read()

    if not success:
        break

    img = cv2.flip(img, 1)

    rgb = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb)

    left_gesture = "none"
    right_gesture = "none"

    right_hand_found = False


    # ---------------- HANDS ----------------

    if results.multi_hand_landmarks:

        for hand, handedness_info in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):

            handedness = (
                handedness_info
                .classification[0]
                .label
            )

            mp_drawing.draw_landmarks(
                img,
                hand,
                mp_hands.HAND_CONNECTIONS
            )


            # ==============================
            # LEFT HAND
            # ==============================

            if handedness == "Left":

                left_gesture = left_thumb_gesture(hand)

                current_time = time.time()

                if current_time - last_scroll > sd:

                    if left_gesture == "scroll_up":

                        pyautogui.scroll(ss)

                        last_scroll = current_time

                    elif left_gesture == "scroll_down":

                        pyautogui.scroll(-ss)

                        last_scroll = current_time


            # ==============================
            # RIGHT HAND
            # ==============================

            elif handedness == "Right":

                right_hand_found = True

                right_gesture = right_hand_gesture(hand)


                # ---------------- MOUSE ----------------

                index_tip = hand.landmark[
                    mp_hands.HandLandmark.INDEX_FINGER_TIP
                ]


                # Camera position -> screen position

                target_x = (
                    index_tip.x *
                    screen_w *
                    mouse_sensitivity
                )

                target_y = (
                    index_tip.y *
                    screen_h *
                    mouse_sensitivity
                )


                # Keep inside screen

                target_x = max(
                    0,
                    min(
                        screen_w - 1,
                        target_x
                    )
                )

                target_y = max(
                    0,
                    min(
                        screen_h - 1,
                        target_y
                    )
                )


                # ---------------- EXTRA SMOOTHING ----------------

                x_history.append(target_x)
                y_history.append(target_y)

                average_x = sum(x_history) / len(x_history)
                average_y = sum(y_history) / len(y_history)


                current_x, current_y = pyautogui.position()


                # Gradual movement

                new_x = current_x + (
                    average_x - current_x
                ) * mouse_smooth

                new_y = current_y + (
                    average_y - current_y
                ) * mouse_smooth


                # Only move with index finger alone

                if right_gesture == "move":

                    pyautogui.moveTo(
                        int(new_x),
                        int(new_y)
                    )


                # ==============================
                # LEFT CLICK
                # ==============================

                if right_gesture == "left_click":

                    # Only click when gesture first appears

                    if previous_gesture != "left_click":

                        current_time = time.time()

                        if current_time - last_click > click_delay:

                            pyautogui.click()

                            last_click = current_time


                # ==============================
                # RIGHT CLICK
                # ==============================

                elif right_gesture == "right_click":

                    # Only click when gesture first appears

                    if previous_gesture != "right_click":

                        current_time = time.time()

                        if current_time - last_click > click_delay:

                            pyautogui.rightClick()

                            last_click = current_time


                previous_gesture = right_gesture


    # ---------------- RESET ----------------

    if not right_hand_found:

        previous_gesture = "none"

        x_history.clear()
        y_history.clear()


    # ---------------- FPS ----------------

    current_time = time.time()

    fps = 1 / (
        current_time - p_time
    )

    p_time = current_time


    # ---------------- DISPLAY ----------------

    cv2.putText(
        img,
        f"FPS: {int(fps)}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 0, 0),
        2
    )

    cv2.putText(
        img,
        f"Left: {left_gesture}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 0, 0),
        2
    )

    cv2.putText(
        img,
        f"Right: {right_gesture}",
        (10, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 0, 0),
        2
    )


    cv2.imshow(
        "Gesture Control",
        img
    )


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# ---------------- CLEANUP ----------------

cap.release()

cv2.destroyAllWindows()
