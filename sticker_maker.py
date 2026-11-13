import os
import subprocess
import sys
import threading
import time
from datetime import datetime

# ------------------------------------------------------------
# INSTALL DEPENDENCIES
# ------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS = os.path.join(HERE, "requirements.txt")

if os.path.exists(REQUIREMENTS):
    subprocess.run(
        [
            sys.executable, "-m", "pip", "install", "-q",
            "--disable-pip-version-check", "-r", REQUIREMENTS
        ],
        check=True
    )

import cv2
import numpy as np
import onnxruntime


# ------------------------------------------------------------
# SAM MODEL SETUP
# ------------------------------------------------------------

options = onnxruntime.SessionOptions()
options.enable_cpu_mem_arena = False

encoder = onnxruntime.InferenceSession(
    os.path.join(HERE, "vision_encoder_uint8.onnx"),
    options
)

decoder = onnxruntime.InferenceSession(
    os.path.join(HERE, "prompt_encoder_mask_decoder_uint8.onnx"),
    options
)

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

WINDOW = "Sticker Maker"
OUTPUT_DIR = os.path.join(HERE, "Stickers")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT = cv2.FONT_HERSHEY_SIMPLEX
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
GREEN = (0, 220, 0)
RED = (0, 0, 255)

MAX_STICKERS = 9
PREVIEW_OPACITY = 0.5


# ------------------------------------------------------------
# PROGRAM STATE
# ------------------------------------------------------------

state = {
    "photo": None,
    "features": None,
    "clicks": [],
    "guesses": None,
    "level": 2,
    "mask": None,

    "stickers": [],
    "selected": None,

    "mouse": (320, 240),
    "placements": [],

    # A newly selected sticker starts at 10% size.
    "scale": 0.1,
    "angle": 0,

    "message": "",
    "message_until": 0,
    "sam_error": None
}


# ------------------------------------------------------------
# SMALL UI HELPERS
# ------------------------------------------------------------

def set_message(message, seconds=2.5):
    state["message"] = message
    state["message_until"] = time.time() + seconds


def show_message():
    if time.time() < state["message_until"]:
        return state["message"]
    return None


# ------------------------------------------------------------
# SAM IMAGE ENCODER
# ------------------------------------------------------------

def study(photo):
    """
    Runs the image encoder in a background thread.

    The model input format and embedding names are kept the same
    as in the supplied working version.
    """
    try:
        resized = cv2.resize(photo, (1024, 1024))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        normalized = (rgb - MEAN) / STD

        input_tensor = normalized.transpose(2, 0, 1)[None].astype(np.float32)

        features_list = encoder.run(
            None,
            {"pixel_values": input_tensor}
        )

        features = {
            f"image_embeddings.{i}": feature
            for i, feature in enumerate(features_list)
        }

        # Only attach the embeddings if this exact frozen photo
        # is still the current photo.
        if state["photo"] is photo:
            state["features"] = features
            state["sam_error"] = None

    except Exception as error:
        if state["photo"] is photo:
            state["sam_error"] = str(error)
        print("SAM encoder error:", error)


# ------------------------------------------------------------
# SAM MASK DECODER
# ------------------------------------------------------------

def ask_sam(features, size, clicks):
    """
    Runs the prompt/mask decoder using the exact input names
    from the supplied code.
    size is (height, width).
    """
    points = np.array(
        [
            [x * 1024 / size[1], y * 1024 / size[0]]
            for x, y, label in clicks
        ],
        dtype=np.float32
    )

    labels = np.array(
        [label for x, y, label in clicks],
        dtype=np.int64
    )

    feeds = {
        "input_points": points[None, None],
        "input_labels": labels[None, None],
        "input_boxes": np.zeros((1, 0, 4), dtype=np.float32)
    }

    outputs = decoder.run(None, {**feeds, **features})

    # This is the mask output used by the supplied version.
    return outputs[1][0, 0]


# ------------------------------------------------------------
# SELECT AND CLEAN A SAM MASK
# ------------------------------------------------------------

def pick(guesses, size, clicks, level):
    """
    Selects one of SAM's three masks and keeps the connected
    components containing positive clicks.
    size is (height, width).
    """
    if guesses is None or len(guesses) == 0:
        return None

    ordered = sorted(
        guesses,
        key=lambda mask: int((mask > 0).sum())
    )

    level = max(0, min(level, len(ordered) - 1))
    guess = ordered[level]

    mask = (
        cv2.resize(
            guess.astype(np.float32),
            (size[1], size[0]),
            interpolation=cv2.INTER_LINEAR
        ) > 0
    ).astype(np.uint8)

    cleaned = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        np.ones((5, 5), dtype=np.uint8)
    )

    count, pieces = cv2.connectedComponents(cleaned)

    keep = []

    height, width = mask.shape

    for x, y, label in clicks:
        if label == 1:
            x = int(np.clip(x, 0, width - 1))
            y = int(np.clip(y, 0, height - 1))
            component = int(pieces[y, x])

            if component != 0:
                keep.append(component)

    if keep:
        return np.isin(pieces, keep).astype(np.uint8)

    # If no positive click falls inside the cleaned mask,
    # use the original mask instead of returning an empty mask.
    return mask


# ------------------------------------------------------------
# STICKER TRANSFORMATION
# ------------------------------------------------------------

def transform_sticker(sticker, scale, angle):
    """Resize and rotate an RGBA sticker without cropping it."""
    height, width = sticker.shape[:2]

    new_width = max(1, int(round(width * scale)))
    new_height = max(1, int(round(height * scale)))

    resized = cv2.resize(
        sticker,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    )

    if angle % 360 == 0:
        return resized

    center = (new_width / 2.0, new_height / 2.0)

    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    cosine = abs(matrix[0, 0])
    sine = abs(matrix[0, 1])

    rotated_width = max(1, int(round(new_height * sine + new_width * cosine)))
    rotated_height = max(1, int(round(new_height * cosine + new_width * sine)))

    matrix[0, 2] += rotated_width / 2.0 - center[0]
    matrix[1, 2] += rotated_height / 2.0 - center[1]

    return cv2.warpAffine(
        resized,
        matrix,
        (rotated_width, rotated_height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)
    )


# ------------------------------------------------------------
# ALPHA COMPOSITING
# ------------------------------------------------------------

def blend_rgba(image, rgba, left, top, opacity=1.0):
    """
    Alpha-composites an RGBA image onto a BGR image.
    left/top are the destination top-left coordinates.
    """
    image_height, image_width = image.shape[:2]
    sticker_height, sticker_width = rgba.shape[:2]

    right = left + sticker_width
    bottom = top + sticker_height

    clipped_left = max(0, left)
    clipped_top = max(0, top)
    clipped_right = min(image_width, right)
    clipped_bottom = min(image_height, bottom)

    if clipped_left >= clipped_right or clipped_top >= clipped_bottom:
        return image

    sx1 = clipped_left - left
    sy1 = clipped_top - top
    sx2 = sx1 + clipped_right - clipped_left
    sy2 = sy1 + clipped_bottom - clipped_top

    sticker_crop = rgba[sy1:sy2, sx1:sx2]
    background = image[
        clipped_top:clipped_bottom,
        clipped_left:clipped_right
    ]

    colour = sticker_crop[:, :, :3].astype(np.float32)
    alpha = sticker_crop[:, :, 3:4].astype(np.float32) / 255.0
    alpha *= opacity

    background_float = background.astype(np.float32)

    blended = colour * alpha + background_float * (1.0 - alpha)

    image[
        clipped_top:clipped_bottom,
        clipped_left:clipped_right
    ] = np.clip(blended, 0, 255).astype(np.uint8)

    return image


def overlay_sticker(image, sticker, center_x, center_y, scale, angle):
    """Place a fully opaque (original-alpha) sticker at a centre point."""
    transformed = transform_sticker(sticker, scale, angle)

    height, width = transformed.shape[:2]
    left = int(round(center_x - width / 2))
    top = int(round(center_y - height / 2))

    return blend_rgba(image, transformed, left, top, opacity=1.0)


# ------------------------------------------------------------
# CURSOR PREVIEW: 50% OPACITY + WHITE OUTLINE
# ------------------------------------------------------------

def draw_preview(image, sticker, center_x, center_y, scale, angle):
    transformed = transform_sticker(sticker, scale, angle)

    height, width = transformed.shape[:2]
    left = int(round(center_x - width / 2))
    top = int(round(center_y - height / 2))

    # Preview only is half-transparent. The saved sticker itself
    # and the placed sticker remain at their original opacity.
    blend_rgba(image, transformed, left, top, opacity=PREVIEW_OPACITY)

    mask = (transformed[:, :, 3] > 10).astype(np.uint8)
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    shifted = []
    for contour in contours:
        contour = contour.copy()
        contour[:, :, 0] += left
        contour[:, :, 1] += top
        shifted.append(contour)

    if shifted:
        cv2.drawContours(image, shifted, -1, WHITE, 2)

    return image


# ------------------------------------------------------------
# DRAW THE NINE-SLOT STICKER LIBRARY
# ------------------------------------------------------------

def draw_library(image):
    panel_width = 244
    panel_height = 244

    cv2.rectangle(
        image,
        (0, 0),
        (panel_width, panel_height),
        (25, 25, 25),
        -1
    )

    for index in range(MAX_STICKERS):
        column = index % 3
        row = index // 3

        x = 8 + column * 79
        y = 8 + row * 79

        cv2.rectangle(
            image,
            (x, y),
            (x + 68, y + 68),
            (55, 55, 55),
            -1
        )

        border_colour = (
            GREEN if state["selected"] == index else WHITE
        )

        cv2.rectangle(
            image,
            (x, y),
            (x + 68, y + 68),
            border_colour,
            2
        )

        if index < len(state["stickers"]):
            sticker = state["stickers"][index]
            sticker_height, sticker_width = sticker.shape[:2]

            factor = min(52 / sticker_width, 52 / sticker_height)

            thumb_width = max(1, int(round(sticker_width * factor)))
            thumb_height = max(1, int(round(sticker_height * factor)))

            thumbnail = cv2.resize(
                sticker,
                (thumb_width, thumb_height),
                interpolation=cv2.INTER_AREA
            )

            thumb_x = x + (68 - thumb_width) // 2
            thumb_y = y + (68 - thumb_height) // 2

            blend_rgba(
                image,
                thumbnail,
                thumb_x,
                thumb_y,
                opacity=1.0
            )

        cv2.putText(
            image,
            str(index + 1),
            (x + 48, y + 63),
            FONT,
            0.4,
            WHITE,
            1,
            cv2.LINE_AA
        )

    return image


# ------------------------------------------------------------
# SAVE A NEW STICKER
# ------------------------------------------------------------

def save_sticker():
    if state["photo"] is None or state["mask"] is None:
        set_message("Select an object first.")
        return

    if len(state["stickers"]) >= MAX_STICKERS:
        set_message("Sticker library is full (9 stickers maximum).")
        return

    mask = state["mask"].astype(np.uint8)

    if cv2.countNonZero(mask) == 0:
        set_message("The selection is empty.")
        return

    x, y, width, height = cv2.boundingRect(mask)

    photo_crop = state["photo"][y:y + height, x:x + width].copy()
    mask_crop = mask[y:y + height, x:x + width]

    # Smooth the alpha edge slightly without changing the RGB image.
    alpha = cv2.GaussianBlur(
        mask_crop * 255,
        (3, 3),
        0
    )

    sticker = np.dstack((photo_crop, alpha))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"sticker_{timestamp}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    if not cv2.imwrite(filepath, sticker):
        set_message("Could not save the sticker PNG.")
        return

    state["stickers"].append(sticker)
    state["selected"] = len(state["stickers"]) - 1
    state["scale"] = 0.1
    state["angle"] = 0

    # Build the one-second black-background sticker preview.
    black = np.zeros_like(state["photo"])

    view_height, view_width = black.shape[:2]
    sticker_height, sticker_width = sticker.shape[:2]

    preview_scale = min(
        1.0,
        (view_width - 40) / max(1, sticker_width),
        (view_height - 60) / max(1, sticker_height)
    )

    transformed = transform_sticker(sticker, preview_scale, 0)

    transformed_height, transformed_width = transformed.shape[:2]
    left = (view_width - transformed_width) // 2
    top = (view_height - transformed_height) // 2

    blend_rgba(black, transformed, left, top)

    contours, _ = cv2.findContours(
        (transformed[:, :, 3] > 10).astype(np.uint8),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    shifted = []
    for contour in contours:
        contour = contour.copy()
        contour[:, :, 0] += left
        contour[:, :, 1] += top
        shifted.append(contour)

    if shifted:
        cv2.drawContours(black, shifted, -1, WHITE, 2)

    cv2.imshow(WINDOW, black)
    cv2.waitKey(1000)

    # Resume live mode after showing the saved sticker.
    state.update({
        "photo": None,
        "features": None,
        "clicks": [],
        "guesses": None,
        "mask": None,
        "level": 2,
        "sam_error": None
    })

    set_message(f"Saved {filename}. Select it with 1-{len(state['stickers'])}.")


# ------------------------------------------------------------
# MOUSE CALLBACK
# ------------------------------------------------------------

def on_mouse(event, x, y, flags, extra):
    state["mouse"] = (x, y)

    # Live mode: left-click places the selected sticker.
    if state["photo"] is None:
        if event == cv2.EVENT_LBUTTONDOWN:
            selected = state["selected"]

            if selected is not None and selected < len(state["stickers"]):
                state["placements"].append({
                    "index": selected,
                    "x": x,
                    "y": y,
                    "scale": state["scale"],
                    "angle": state["angle"]
                })
        return

    # Frozen mode: wait for the encoder to finish.
    if state["features"] is None:
        return

    label = None

    if event == cv2.EVENT_LBUTTONDOWN:
        label = 1
    elif event == cv2.EVENT_RBUTTONDOWN:
        label = 0

    if label is None:
        return

    height, width = state["photo"].shape[:2]

    x = int(np.clip(x, 0, width - 1))
    y = int(np.clip(y, 0, height - 1))

    state["clicks"].append((x, y, label))

    try:
        state["guesses"] = ask_sam(
            state["features"],
            (height, width),
            state["clicks"]
        )

        state["mask"] = pick(
            state["guesses"],
            (height, width),
            state["clicks"],
            state["level"]
        )

    except Exception as error:
        print("SAM decoder error:", error)
        state["sam_error"] = str(error)


# ------------------------------------------------------------
# CAMERA SETUP
# ------------------------------------------------------------

video = cv2.VideoCapture(0)

video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not video.isOpened():
    raise RuntimeError("Could not open the webcam. Check camera permissions.")

cv2.namedWindow(WINDOW)
cv2.setMouseCallback(WINDOW, on_mouse)


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

try:
    while True:
        ok, camera_frame = video.read()

        if not ok:
            print("Could not read a frame from the webcam.")
            break

        # Mirror the camera so the preview behaves like a mirror.
        live = cv2.flip(camera_frame, 1)

        # Use the frozen photo in SAM mode; otherwise use live camera.
        if state["photo"] is None:
            view = live.copy()
        else:
            view = state["photo"].copy()

        # ----------------------------------------------------
        # LIVE MODE: DRAW PLACED STICKERS AND CURSOR PREVIEW
        # ----------------------------------------------------

        if state["photo"] is None:

            # Draw all placed stickers at full original opacity.
            for placement in state["placements"]:
                index = placement["index"]

                if 0 <= index < len(state["stickers"]):
                    overlay_sticker(
                        view,
                        state["stickers"][index],
                        placement["x"],
                        placement["y"],
                        placement["scale"],
                        placement["angle"]
                    )

            # Draw the selected sticker preview around the cursor.
            if state["selected"] is not None:
                selected = state["selected"]

                if 0 <= selected < len(state["stickers"]):
                    draw_preview(
                        view,
                        state["stickers"][selected],
                        state["mouse"][0],
                        state["mouse"][1],
                        state["scale"],
                        state["angle"]
                    )

            # Draw the library last so it remains readable.
            view = draw_library(view)

            cv2.putText(
                view,
                f"Size: {state['scale']:.2f}  Rotation: {state['angle']} deg",
                (10, 265),
                FONT,
                0.5,
                WHITE,
                1,
                cv2.LINE_AA
            )

        # ----------------------------------------------------
        # FROZEN MODE: SHOW SAM MASK AND PROMPTS
        # ----------------------------------------------------

        else:
            if state["mask"] is not None:
                mask_bool = state["mask"].astype(bool)

                overlay_colour = np.zeros_like(view)
                overlay_colour[:] = YELLOW

                view[mask_bool] = (
                    view[mask_bool].astype(np.float32) * 0.5
                    + overlay_colour[mask_bool].astype(np.float32) * 0.5
                ).astype(np.uint8)

                contours, _ = cv2.findContours(
                    state["mask"].astype(np.uint8),
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )

                cv2.drawContours(view, contours, -1, WHITE, 2)

            for x, y, label in state["clicks"]:
                cv2.circle(
                    view,
                    (x, y),
                    7,
                    GREEN if label == 1 else RED,
                    -1
                )

        # ----------------------------------------------------
        # HELP TEXT
        # ----------------------------------------------------

        if state["photo"] is None:
            help_line = (
                "1-9 select | Click place | +/- size | [ ] rotate | "
                "SPACE capture | 0 undo | X clear | F freeze"
            )
        elif state["features"] is None:
            help_line = "SAM is analysing the photo..."
        else:
            help_line = (
                "Click select | Right-click exclude | M change mask | "
                "S save sticker | F live"
            )

        bar_y = view.shape[0] - 35
        cv2.rectangle(
            view,
            (0, bar_y),
            (view.shape[1], view.shape[0]),
            (30, 30, 30),
            -1
        )

        displayed_message = show_message()
        text_to_show = displayed_message if displayed_message else help_line

        cv2.putText(
            view,
            text_to_show,
            (10, view.shape[0] - 12),
            FONT,
            0.43,
            WHITE,
            1,
            cv2.LINE_AA
        )

        # Display SAM errors separately when present.
        if state["sam_error"]:
            cv2.putText(
                view,
                "SAM error - see terminal",
                (10, 295),
                FONT,
                0.5,
                RED,
                1,
                cv2.LINE_AA
            )

        cv2.imshow(WINDOW, view)

        key = cv2.waitKey(1) & 0xFF
        key_char = chr(key).lower() if key != 255 else ""

        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if key_char in ("q", "\x1b"):
            break

        try:
            if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break

        # ----------------------------------------------------
        # FREEZE / RETURN TO LIVE MODE
        # ----------------------------------------------------

        if key_char == "f":
            if state["photo"] is None:
                photo = live.copy()

                state.update({
                    "photo": photo,
                    "features": None,
                    "clicks": [],
                    "guesses": None,
                    "mask": None,
                    "level": 2,
                    "sam_error": None
                })

                threading.Thread(
                    target=study,
                    args=(photo,),
                    daemon=True
                ).start()

            else:
                state.update({
                    "photo": None,
                    "features": None,
                    "clicks": [],
                    "guesses": None,
                    "mask": None,
                    "level": 2,
                    "sam_error": None
                })

        # ----------------------------------------------------
        # CYCLE THROUGH SAM MASKS
        # ----------------------------------------------------

        elif key_char == "m" and state["photo"] is not None:
            if state["guesses"] is not None:
                state["level"] = (state["level"] + 1) % len(state["guesses"])

                state["mask"] = pick(
                    state["guesses"],
                    state["photo"].shape[:2],
                    state["clicks"],
                    state["level"]
                )

        # ----------------------------------------------------
        # SAVE SELECTED OBJECT AS A STICKER
        # ----------------------------------------------------

        elif key_char == "s" and state["photo"] is not None:
            if state["mask"] is not None:
                save_sticker()
            else:
                set_message("Click an object first to select it.")

        # ----------------------------------------------------
        # SELECT A STICKER WITH KEYS 1-9
        # ----------------------------------------------------

        elif state["photo"] is None and key_char and key_char in "123456789":
            index = int(key_char) - 1

            if index < len(state["stickers"]):
                state["selected"] = index
                state["scale"] = 0.1
                state["angle"] = 0

        # ----------------------------------------------------
        # ADJUST STICKER SIZE
        # ----------------------------------------------------

        elif state["photo"] is None and key in (ord("+"), ord("=")):
            state["scale"] = min(2.0, state["scale"] * 1.1)

        elif state["photo"] is None and key == ord("-"):
            state["scale"] = max(0.01, state["scale"] / 1.1)

        # ----------------------------------------------------
        # ROTATE STICKER
        # ----------------------------------------------------

        elif state["photo"] is None and key_char == "[":
            state["angle"] -= 10

        elif state["photo"] is None and key_char == "]":
            state["angle"] += 10

        # ----------------------------------------------------
        # UNDO LAST PLACEMENT
        # ----------------------------------------------------

        elif state["photo"] is None and key_char == "0":
            if state["placements"]:
                state["placements"].pop()

        # ----------------------------------------------------
        # CLEAR ALL PLACEMENTS
        # ----------------------------------------------------

        elif state["photo"] is None and key_char == "x":
            state["placements"].clear()

        # ----------------------------------------------------
        # CAPTURE AND SAVE THE COMPOSITED PHOTOGRAPH
        # ----------------------------------------------------

        elif state["photo"] is None and key == 32:
            final_photo = live.copy()

            for placement in state["placements"]:
                index = placement["index"]

                if 0 <= index < len(state["stickers"]):
                    overlay_sticker(
                        final_photo,
                        state["stickers"][index],
                        placement["x"],
                        placement["y"],
                        placement["scale"],
                        placement["angle"]
                    )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"capture_{timestamp}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)

            saved = cv2.imwrite(filepath, final_photo)

            if saved:
                print("Photograph saved:", filepath)

                # Show the actual saved composition for one second.
                cv2.imshow(WINDOW, final_photo)
                cv2.waitKey(1000)

                state["placements"].clear()
                set_message(f"Photo saved: {filename}")
            else:
                print("Could not save photograph:", filepath)
                set_message("Photo could not be saved!")

finally:
    video.release()
    cv2.destroyAllWindows()
