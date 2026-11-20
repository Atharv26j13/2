import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "--disable-pip-version-check", "-r",
    os.path.join(HERE, "requirements.txt")
], check=True)

import cv2
import numpy as np
import onnxruntime


# ==================== SETTINGS ====================

START_SECONDS = 12
MIN_SECONDS = 4
TIME_MULTIPLIER = 0.96

RAPID_FIRE_EVERY = 5
RAPID_FIRE_TIME_FACTOR = 0.5
RAPID_FIRE_SCORE_MULTIPLIER = 3

MATCH_THRESHOLD = 90
SMOOTHING = 0.65
CONFIDENCE = 0.25

FADE_DURATION = 0.5

# ==================================================


POSES = {
    "Arms up!": [-90, -90, -90, -90],

    "T-pose!": [180, 180, 0, 0],

    "Arms down!": [90, 90, 90, 90],

    "Goalpost!": [180, -90, 0, -90],

    "Wings!": [180, 90, 0, 90],

    "Right arm up!": [90, 90, -90, -90],

    "Left arm up!": [-90, -90, 90, 90],

    "Diagonal!": [-135, -135, -45, -45],

    "Left diagonal!": [-135, -135, 90, 90],

    "Right diagonal!": [90, 90, -45, -45],

    "Muscle pose!": [-135, -45, -45, -135],

    "Left bent arm!": [180, -90, 90, 90],

    "Right bent arm!": [90, 90, 0, -90],

    "Half T-pose!": [180, 180, -90, -90],

    "One arm out!": [180, 180, 90, 90]
}


BONES = [
    (5, 7), (7, 9),
    (6, 8), (8, 10),
    (5, 6), (5, 11),
    (6, 12), (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16)
]

FONT = cv2.FONT_HERSHEY_SIMPLEX

WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
GREEN = (0, 200, 0)
RED = (0, 0, 255)
ORANGE = (0, 140, 255)


model = onnxruntime.InferenceSession(
    os.path.join(HERE, "movenet.onnx"),
    providers=["CPUExecutionProvider"]
)


# ==================== BODY DETECTION ====================

def find_body(frame):

    side = max(frame.shape[:2])

    square = cv2.copyMakeBorder(
        frame,
        0, side - frame.shape[0],
        0, side - frame.shape[1],
        cv2.BORDER_CONSTANT
    )

    image = cv2.cvtColor(
        cv2.resize(square, (192, 192)),
        cv2.COLOR_BGR2RGB
    ).astype(np.int32)[None]

    result = model.run(
        None,
        {"input": image}
    )[0][0, 0]

    return [
        (px * side, py * side, sure)
        for py, px, sure in result
    ]


def smooth_points(old_points, new_points):

    if old_points is None:
        return new_points

    updated = []

    for old, new in zip(old_points, new_points):

        if new[2] >= CONFIDENCE:

            x = (
                SMOOTHING * old[0]
                + (1 - SMOOTHING) * new[0]
            )

            y = (
                SMOOTHING * old[1]
                + (1 - SMOOTHING) * new[1]
            )

        else:
            x, y = old[0], old[1]

        updated.append((x, y, new[2]))

    return updated


# ==================== POSE MATCHING ====================

def arm_angles(points):

    left, right = (
        ((5, 7, 9), (6, 8, 10))
        if points[5][0] < points[6][0]
        else ((6, 8, 10), (5, 7, 9))
    )

    return [
        np.degrees(
            np.arctan2(
                points[b][1] - points[a][1],
                points[b][0] - points[a][0]
            )
        )
        for a, b in [
            *zip(left, left[1:]),
            *zip(right, right[1:])
        ]
    ]


def match(points, target):

    required = (5, 6, 7, 8, 9, 10)

    if min(points[i][2] for i in required) < CONFIDENCE:
        return 0

    differences = [
        abs((a - t + 180) % 360 - 180)
        for a, t in zip(arm_angles(points), target)
    ]

    return max(
        0,
        100 - np.mean(differences)
    )


# ==================== DRAWING ====================

def is_rapid_fire_round(game):

    return game["round"] % RAPID_FIRE_EVERY == 0


def get_round_duration(game):

    base = game["seconds"]

    if is_rapid_fire_round(game):
        return base * RAPID_FIRE_TIME_FACTOR

    return base


def apply_rapid_fire_style(view, now):

    # Shift hue smoothly and boost saturation for a lively, colourful screen.
    hsv = cv2.cvtColor(view, cv2.COLOR_BGR2HSV).astype(np.int16)
    hue_shift = int((now * 90) % 180)
    hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] + 55, 0, 255)
    colourful = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # Blend colourful tint while preserving real camera clarity.
    blended = cv2.addWeighted(colourful, 0.45, view, 0.55, 0)

    # Draw a vibrant cycling border around the frame.
    border_hue = int((now * 160) % 180)
    border_color = tuple(
        int(c)
        for c in cv2.cvtColor(
            np.uint8([[[border_hue, 255, 255]]]),
            cv2.COLOR_HSV2BGR
        )[0, 0]
    )
    cv2.rectangle(
        blended,
        (0, 0),
        (blended.shape[1] - 1, blended.shape[0] - 1),
        border_color,
        12
    )

    return blended


def draw_target(view, angles):

    x, y = view.shape[1] - 80, 150

    cv2.rectangle(
        view,
        (x - 76, y - 70),
        (x + 76, y + 80),
        (40, 40, 40),
        -1
    )

    cv2.circle(
        view,
        (x, y - 42),
        11,
        WHITE,
        2
    )

    cv2.polylines(
        view,
        [
            np.array([
                (x - 20, y - 22),
                (x + 20, y - 22)
            ]),
            np.array([
                (x, y - 22),
                (x, y + 30)
            ])
        ],
        False,
        WHITE,
        3
    )

    def step(point, angle):

        return (
            int(point[0] + 26 * np.cos(np.radians(angle))),
            int(point[1] + 26 * np.sin(np.radians(angle)))
        )

    for shoulder, (upper, lower) in (
        ((x - 20, y - 22), angles[:2]),
        ((x + 20, y - 22), angles[2:])
    ):

        elbow = step(shoulder, upper)
        hand = step(elbow, lower)

        cv2.polylines(
            view,
            [np.array([shoulder, elbow, hand])],
            False,
            YELLOW,
            4
        )


def draw_skeleton(view, points):

    for a, b in BONES:

        if (
            points[a][2] >= CONFIDENCE
            and points[b][2] >= CONFIDENCE
        ):

            cv2.line(
                view,
                (int(points[a][0]), int(points[a][1])),
                (int(points[b][0]), int(points[b][1])),
                YELLOW,
                4
            )


# ==================== GAME ====================

def new_game():

    game = {
        "score": 0,
        "round": 1,
        "normal_points": 1,
        "pose": random.choice(list(POSES)),
        "seconds": START_SECONDS,
        "deadline": 0.0,
        "game_over": False
    }
    game["deadline"] = time.time() + get_round_duration(game)
    return game


video = cv2.VideoCapture(0)

if not video.isOpened():
    raise RuntimeError("Could not open webcam.")

smoothed_points = None

game = new_game()

frozen_frame = None
freeze_started = 0

while True:

    ok, frame = video.read()

    if not ok:
        break

    now = time.time()

    view = cv2.flip(frame, 1)

    # ==================== FREEZE FRAME ====================

    if frozen_frame is not None:

        elapsed = now - freeze_started

        if elapsed < FADE_DURATION:

            alpha = 1 - elapsed / FADE_DURATION

            display = cv2.addWeighted(
                frozen_frame,
                alpha,
                view,
                1 - alpha,
                0
            )

            # Celebration text fades with the frame.

            text_layer = display.copy()

            cv2.putText(
                text_layer,
                "NICE!",
                (display.shape[1] // 2 - 65,
                 display.shape[0] // 2),
                FONT,
                2,
                GREEN,
                5
            )

            display = cv2.addWeighted(
                text_layer,
                alpha,
                display,
                1 - alpha,
                0
            )

            cv2.imshow("Strike a Pose", display)

            key = chr(cv2.waitKey(1) & 255).lower()

            if key in ("q", "\x1b"):
                break

            if key == "r":
                game = new_game()
                frozen_frame = None
                smoothed_points = None

            if cv2.getWindowProperty(
                "Strike a Pose",
                cv2.WND_PROP_VISIBLE
            ) == 0:
                break

            continue

        else:
            frozen_frame = None

    # ==================== DETECTION ====================

    raw_points = find_body(view)

    points = smooth_points(
        smoothed_points,
        raw_points
    )

    smoothed_points = points

    draw_skeleton(view, points)

    # ==================== SCORING ====================

    if not game["game_over"]:

        percent = match(
            points,
            POSES[game["pose"]]
        )

        if percent > MATCH_THRESHOLD:

            rapid_completed = is_rapid_fire_round(game)

            # Award points (3x during a rapid fire round).
            points_earned = (
                game["normal_points"] * RAPID_FIRE_SCORE_MULTIPLIER
                if rapid_completed
                else game["normal_points"]
            )
            game["score"] += points_earned

            # Completing a rapid fire round permanently increases normal round points by 1.
            if rapid_completed:
                game["normal_points"] += 1

            # Save the exact detected frame.

            cv2.imwrite(
                os.path.join(
                    HERE,
                    f"pose_{time.strftime('%H%M%S')}_{game['score']}.jpg"
                ),
                view
            )

            # Exponential difficulty progression.

            game["seconds"] = max(
                MIN_SECONDS,
                game["seconds"] * TIME_MULTIPLIER
            )

            # Advance to the next round and select a different pose.

            game["round"] += 1

            previous_pose = game["pose"]

            choices = [
                name for name in POSES
                if name != previous_pose
            ]

            game["pose"] = random.choice(choices)

            # Start the next timer after the fade (half duration for rapid fire rounds).

            game["deadline"] = (
                now + FADE_DURATION + get_round_duration(game)
            )

            # Freeze the exact successful frame.

            frozen_frame = view.copy()
            freeze_started = now

            cv2.imshow(
                "Strike a Pose",
                frozen_frame
            )

            key = chr(cv2.waitKey(1) & 255).lower()

            if key in ("q", "\x1b"):
                break

            if key == "r":
                game = new_game()
                frozen_frame = None
                smoothed_points = None

            continue

        if now >= game["deadline"]:
            game["game_over"] = True

    # ==================== INTERFACE ====================

    if not game["game_over"]:

        rapid_active = is_rapid_fire_round(game)

        if rapid_active:
            view = apply_rapid_fire_style(view, now)

        remaining = max(
            0,
            game["deadline"] - time.time()
        )

        cv2.rectangle(
            view,
            (0, 0),
            (view.shape[1], 60),
            (30, 30, 30),
            -1
        )

        cv2.putText(
            view,
            game["pose"],
            (15, 42),
            FONT,
            1.2,
            YELLOW,
            3
        )

        if rapid_active:
            cv2.putText(
                view,
                f"RAPID FIRE! x{RAPID_FIRE_SCORE_MULTIPLIER} PTS",
                (15, 115),
                FONT,
                0.75,
                YELLOW,
                2
            )

        cv2.putText(
            view,
            f"{remaining:.1f} s",
            (view.shape[1] - 290, 40),
            FONT,
            0.8,
            WHITE,
            2
        )

        cv2.putText(
            view,
            f"Score: {game['score']}",
            (view.shape[1] - 150, 40),
            FONT,
            0.8,
            WHITE,
            2
        )

        cv2.rectangle(
            view,
            (15, 70),
            (315, 85),
            (50, 50, 50),
            -1
        )

        cv2.rectangle(
            view,
            (15, 70),
            (15 + int(3 * percent), 85),
            GREEN if percent > MATCH_THRESHOLD else ORANGE,
            -1
        )

        cv2.putText(
            view,
            f"Match: {percent:.0f}%",
            (330, 84),
            FONT,
            0.6,
            WHITE,
            2
        )

        draw_target(
            view,
            POSES[game["pose"]]
        )

    else:

        view = view // 3

        cv2.putText(
            view,
            "GAME OVER!",
            (40, view.shape[0] // 2 - 60),
            FONT,
            1.8,
            RED,
            4
        )

        cv2.putText(
            view,
            f"Final score: {game['score']}",
            (40, view.shape[0] // 2),
            FONT,
            1.2,
            YELLOW,
            3
        )

        cv2.putText(
            view,
            "R - Play again    Q - Quit",
            (40, view.shape[0] // 2 + 55),
            FONT,
            0.8,
            WHITE,
            2
        )

    cv2.imshow("Strike a Pose", view)

    key = chr(cv2.waitKey(1) & 255).lower()

    if key in ("q", "\x1b"):
        break

    if key == "r":
        game = new_game()
        smoothed_points = None
        frozen_frame = None

    if cv2.getWindowProperty(
        "Strike a Pose",
        cv2.WND_PROP_VISIBLE
    ) == 0:
        break


video.release()
cv2.destroyAllWindows()