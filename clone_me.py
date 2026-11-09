
import os
import time

import cv2
import numpy as np
import onnxruntime

HERE = os.path.dirname(os.path.abspath(__file__))

# ONNX Runtime optimisation
options = onnxruntime.SessionOptions()
options.intra_op_num_threads = 4
options.inter_op_num_threads = 1
options.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL

model = onnxruntime.InferenceSession(
    os.path.join(HERE, "modnet.onnx"),
    sess_options=options,
    providers=["CPUExecutionProvider"]
)

INPUT = model.get_inputs()[0].name
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Settings
LIVE_SIZE = 256
CAPTURE_SIZE = 256

CAPTURE_EVERY = 2

# Visual effects
FADE_AMOUNT = 0.08
DESATURATION_AMOUNT = 0.10
MIN_ALPHA = 0.03

# Outline settings
outline_enabled = True
OUTLINE_THICKNESS = 3


def cut_out(frame, size=LIVE_SIZE):
    height, width = frame.shape[:2]

    new_width = max(
        32,
        round(width * size / height / 32) * 32
    )

    small = cv2.resize(
        frame,
        (new_width, size),
        interpolation=cv2.INTER_LINEAR
    )

    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    rgb = rgb.astype(np.float32) / 127.5 - 1

    x = np.transpose(rgb, (2, 0, 1))[None]

    matte = model.run(None, {INPUT: x})[0][0, 0]

    return cv2.resize(
        matte,
        (width, height),
        interpolation=cv2.INTER_LINEAR
    )


def clean(matte):
    binary = (matte > 0.35).astype(np.uint8)

    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary)

    if count < 2:
        return np.zeros_like(matte)

    biggest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])

    body = (labels == biggest).astype(np.uint8)

    body = cv2.erode(
        body,
        np.ones((5, 5), np.uint8)
    )

    return cv2.GaussianBlur(
        body.astype(np.float32),
        (9, 9),
        0
    )


def paste(scene, person, matte, opacity=1.0, saturation=1.0):

    gray = cv2.cvtColor(person, cv2.COLOR_BGR2GRAY)

    gray = cv2.cvtColor(
        gray,
        cv2.COLOR_GRAY2BGR
    )

    person = cv2.addWeighted(
        person,
        saturation,
        gray,
        1 - saturation,
        0
    )

    alpha = matte[:, :, None] * opacity

    result = (
        person.astype(np.float32) * alpha +
        scene.astype(np.float32) * (1 - alpha)
    )

    return np.clip(result, 0, 255).astype(np.uint8)


def draw_outline(image, matte):

    binary = (matte > 0.35).astype(np.uint8)

    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    cv2.drawContours(
        image,
        contours,
        -1,
        (255, 255, 255),
        OUTLINE_THICKNESS,
        cv2.LINE_AA
    )

    return image


# Camera
video = cv2.VideoCapture(0)

video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
video.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Frame, matte, opacity, saturation
copies = []

cached_matte = None
frame_count = 0

# FPS
fps = 0
fps_start = time.time()
fps_frames = 0

message = ""
message_until = 0

print("Clone Me started!")
print("Capturing every 2 frames.")
print("Press O to toggle the white outline.")

while True:

    ok, frame = video.read()

    if not ok:
        break

    frame = cv2.flip(frame, 1)

    height, width = frame.shape[:2]

    frame_count += 1

    # Live segmentation
    if cached_matte is None or frame_count % 3 == 0:
        cached_matte = clean(cut_out(frame, LIVE_SIZE))

    matte = cached_matte

    # Capture every 2 frames
    if frame_count % CAPTURE_EVERY == 0:

        capture_matte = clean(cut_out(frame, CAPTURE_SIZE))

        # Age existing clones
        for clone in copies:
            clone[2] *= (1 - FADE_AMOUNT)
            clone[3] *= (1 - DESATURATION_AMOUNT)

        # Remove invisible clones
        copies = [
            clone for clone in copies
            if clone[2] > MIN_ALPHA
        ]

        # Add newest clone
        copies.append([
            frame.copy(),
            capture_matte,
            1.0,
            1.0
        ])

    # Compose image
    view = frame.copy()

    for old_frame, old_matte, opacity, saturation in copies:

        view = paste(
            view,
            old_frame,
            old_matte,
            opacity,
            saturation
        )

    # Current person remains fully coloured
    view = paste(view, frame, matte)

    # Draw white outline around current person
    if outline_enabled:
        view = draw_outline(view, matte)

    # FPS calculation
    fps_frames += 1
    now = time.time()

    if now - fps_start >= 1:
        fps = fps_frames / (now - fps_start)
        fps_frames = 0
        fps_start = now

    # Instructions
    outline_status = "ON" if outline_enabled else "OFF"

    cv2.putText(
        view,
        f"{len(copies)} clones | O outline: {outline_status} | S save | U undo | C clear | Q quit",
        (10, 25),
        FONT,
        0.48,
        (255, 255, 255),
        2
    )

    cv2.putText(
        view,
        f"FPS: {fps:.1f}",
        (10, 55),
        FONT,
        0.65,
        (0, 255, 0),
        2
    )

    # Messages
    if time.time() < message_until:
        cv2.putText(
            view,
            message,
            (10, height - 15),
            FONT,
            0.7,
            (0, 255, 255),
            2
        )

    cv2.imshow("Clone Me", view)

    code = cv2.waitKey(1)
    key = chr(code & 255).lower() if code != -1 else ""

    # Quit
    if key in ("q", "\x1b"):
        break

    # Toggle outline
    elif key == "o":
        outline_enabled = not outline_enabled

    # Undo
    elif key == "u" and copies:
        copies.pop()

    # Clear
    elif key == "c":
        copies.clear()

    # Save
    elif key == "s":

        if not copies:
            message = "No clones to save!"

        else:
            name = time.strftime("clone_photo_%H%M%S.jpg")

            photo = frame.copy()

            for old_frame, old_matte, opacity, saturation in copies:

                photo = paste(
                    photo,
                    old_frame,
                    old_matte,
                    opacity,
                    saturation
                )

            photo = paste(photo, frame, matte)

            if outline_enabled:
                photo = draw_outline(photo, matte)

            cv2.imwrite(
                os.path.join(HERE, name),
                photo
            )

            message = "Saved " + name

        message_until = time.time() + 2

    # Window closed
    if cv2.getWindowProperty(
        "Clone Me",
        cv2.WND_PROP_VISIBLE
    ) < 1:
        break


video.release()
cv2.destroyAllWindows()
