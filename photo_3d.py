
import os
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))

subprocess.run(
    [
        sys.executable, "-m", "pip", "install", "-q",
        "--disable-pip-version-check",
        "-r", os.path.join(HERE, "requirements.txt")
    ],
    check=True
)

import cv2
import numpy as np
import onnxruntime


# ============================================================
# CONFIGURATION
# ============================================================

WIDTH, HEIGHT = 640, 480

DEPTH_WIDTH, DEPTH_HEIGHT = 256, 192

PANEL_WIDTH, PANEL_HEIGHT = 480, 360

DEPTH_INTERVAL = 0.18

NEAR_DISTANCE = 0.30
FAR_DISTANCE = 8.0

BLUR_PER_DIOPTRE = 3.0
MAX_BLUR_SIGMA = 40.0

WOBBLE = 12

FONT = cv2.FONT_HERSHEY_SIMPLEX

cv2.setNumThreads(2)
cv2.setUseOptimized(True)


# ============================================================
# AI SETUP
# ============================================================

options = onnxruntime.SessionOptions()

options.intra_op_num_threads = 2
options.inter_op_num_threads = 1

options.execution_mode = (
    onnxruntime.ExecutionMode.ORT_SEQUENTIAL
)

options.graph_optimization_level = (
    onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
)

options.add_session_config_entry(
    "session.intra_op.allow_spinning", "0"
)

options.add_session_config_entry(
    "session.inter_op.allow_spinning", "0"
)

model = onnxruntime.InferenceSession(
    os.path.join(HERE, "depth.onnx"),
    options,
    providers=["CPUExecutionProvider"]
)

input_name = model.get_inputs()[0].name

MEAN = np.array(
    [0.485, 0.456, 0.406],
    np.float32
)

STD = np.array(
    [0.229, 0.224, 0.225],
    np.float32
)


# ============================================================
# DEPTH ESTIMATION
# ============================================================

def depth(picture):

    small = cv2.resize(
        picture,
        (336, 252),
        interpolation=cv2.INTER_AREA
    )

    rgb = cv2.cvtColor(
        small,
        cv2.COLOR_BGR2RGB
    ).astype(np.float32) / 255.0

    x = (
        (rgb - MEAN) / STD
    ).transpose(2, 0, 1)[None]

    result = model.run(
        None,
        {input_name: x}
    )[0][0]

    result = np.nan_to_num(result)

    result = cv2.resize(
        result,
        (DEPTH_WIDTH, DEPTH_HEIGHT)
    )

    minimum = float(result.min())
    maximum = float(result.max())

    near = (
        (result - minimum) /
        (maximum - minimum + 1e-6)
    )

    return cv2.GaussianBlur(
        near.astype(np.float32),
        (5, 5),
        0
    )


# ============================================================
# DEPTH TO DISTANCE
# ============================================================

def estimate_distance(near):

    near = np.clip(near, 0, 1)

    far_v = 1.0 / FAR_DISTANCE
    near_v = 1.0 / NEAR_DISTANCE

    vergence = (
        far_v + near * (near_v - far_v)
    )

    return 1.0 / np.maximum(vergence, 1e-6)


# ============================================================
# MYOPIA AND HYPEROPIA
# ============================================================

def optical_blur(
    frame,
    distance,
    power,
    condition,
    accommodation,
    pupil
):

    if power <= 0:
        return frame.copy()

    object_vergence = 1.0 / np.maximum(
        distance, 0.01
    )

    if condition == "myopia":

        defocus = np.maximum(
            power - object_vergence,
            0
        )

    else:

        defocus = np.maximum(
            power + object_vergence - accommodation,
            0
        )

    defocus = cv2.GaussianBlur(
        defocus.astype(np.float32),
        (5, 5),
        0
    )

    mask = 1.0 - np.exp(
        -1.1 * defocus
    )

    mask = np.clip(
        mask,
        0,
        0.98
    )

    mask = cv2.resize(
        mask,
        (WIDTH, HEIGHT),
        interpolation=cv2.INTER_LINEAR
    )

    sigma = min(
        MAX_BLUR_SIGMA,
        power * BLUR_PER_DIOPTRE
    )

    sigma *= pupil / 4.0

    blurred = cv2.GaussianBlur(
        frame,
        (0, 0),
        sigmaX=sigma,
        sigmaY=sigma,
        borderType=cv2.BORDER_REFLECT
    )

    mask = mask[:, :, None]

    output = (
        frame.astype(np.float32) * (1 - mask) +
        blurred.astype(np.float32) * mask
    )

    return np.clip(
        output, 0, 255
    ).astype(np.uint8)


# ============================================================
# LIVE 3D PARALLAX
# ============================================================

def make_3d_photo(depth):
    if depth is None:
        return np.zeros((480, 640, 3), dtype=np.uint8)

    depth = np.asarray(depth, dtype=np.float32)

    if depth.ndim != 2:
        depth = np.squeeze(depth)

    if depth.ndim != 2:
        raise ValueError(
            f"Expected a 2D depth map, received shape: {depth.shape}"
        )

    depth = cv2.resize(depth, (640, 480))

    depth = cv2.normalize(
        depth, None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)

    # Colour-coded depth map
    return cv2.applyColorMap(depth, cv2.COLORMAP_TURBO)


# ============================================================
# FOUR-PANEL LAYOUT
# ============================================================

def make_panel(image, title, subtitle):

    image = cv2.resize(
        image,
        (PANEL_WIDTH, PANEL_HEIGHT),
        interpolation=cv2.INTER_AREA
    )

    panel = np.zeros(
        (PANEL_HEIGHT + 48, PANEL_WIDTH, 3),
        dtype=np.uint8
    )

    panel[:] = (25, 25, 25)

    panel[48:, :] = image

    cv2.putText(
        panel,
        title,
        (12, 21),
        FONT,
        0.58,
        (0, 255, 255),
        2
    )

    cv2.putText(
        panel,
        subtitle,
        (12, 40),
        FONT,
        0.38,
        (200, 200, 200),
        1
    )

    return panel


def make_layout(original, three_d, myopia, hyperopia,
                prescription, fps):

    p1 = make_panel(
        original,
        "ORIGINAL",
        "Unmodified camera feed"
    )

    p2 = make_panel(
        three_d,
        "3D PHOTO",
        "Live depth-based parallax"
    )

    p3 = make_panel(
        myopia,
        "MYOPIA",
        f"Negative prescription: {-max(-prescription, 0):.2f}D"
    )

    p4 = make_panel(
        hyperopia,
        "HYPEROPIA",
        f"Positive prescription: {max(prescription, 0):.2f}D"
    )

    top = np.hstack((p1, p2))
    bottom = np.hstack((p3, p4))

    layout = np.vstack((top, bottom))

    footer = np.zeros(
        (42, layout.shape[1], 3),
        dtype=np.uint8
    )

    cv2.putText(
        footer,
        f"FPS: {fps:.1f} | "
        f"Prescription: {prescription:+.2f}D | "
        "Q: Quit",
        (12, 27),
        FONT,
        0.55,
        (255, 255, 255),
        1
    )

    return np.vstack((layout, footer))


# ============================================================
# SHARED AI WORKER
# ============================================================

shared = {
    "picture": None,
    "near": None,
    "sequence": 0,
    "running": True,
    "error": None
}

lock = threading.Lock()


def keep_measuring():

    last_sequence = -1
    previous = None

    while True:

        with lock:

            if not shared["running"]:
                break

            picture = shared["picture"]
            sequence = shared["sequence"]

            if picture is not None:
                picture = picture.copy()

        if picture is None or sequence == last_sequence:

            time.sleep(0.01)
            continue

        start = time.perf_counter()

        try:

            current = depth(picture)

            if previous is not None:

                current = cv2.addWeighted(
                    current, 0.72,
                    previous, 0.28,
                    0
                )

            previous = current

            with lock:

                shared["near"] = current
                shared["error"] = None

            last_sequence = sequence

        except Exception as error:

            with lock:
                shared["error"] = str(error)

            print("AI worker error:", error)

        elapsed = time.perf_counter() - start

        if elapsed < DEPTH_INTERVAL:
            time.sleep(DEPTH_INTERVAL - elapsed)


# ============================================================
# CAMERA
# ============================================================

video = cv2.VideoCapture(0)

video.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
video.set(cv2.CAP_PROP_FPS, 30)
video.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not video.isOpened():
    raise RuntimeError("Could not open camera.")


# ============================================================
# WINDOW
# ============================================================

WINDOW = "AI Human Vision Simulator"

cv2.namedWindow(
    WINDOW,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    WINDOW,
    PANEL_WIDTH * 2,
    (PANEL_HEIGHT + 48) * 2 + 42
)

# One shared signed prescription slider:
# 0 = -20D
# 80 = 0D
# 160 = +20D

cv2.createTrackbar(
    "Prescription (-20D to +20D)",
    WINDOW,
    80,
    160,
    lambda x: None
)

cv2.createTrackbar(
    "Accommodation (D)",
    WINDOW,
    0,
    80,
    lambda x: None
)

cv2.createTrackbar(
    "Pupil diameter (mm x2)",
    WINDOW,
    8,
    16,
    lambda x: None
)


# ============================================================
# START AI
# ============================================================

worker = threading.Thread(
    target=keep_measuring,
    daemon=True
)

worker.start()


# ============================================================
# MAIN LOOP
# ============================================================

previous_time = time.perf_counter()
fps = 0.0

try:

    while True:

        ok, frame = video.read()

        if not ok:
            break

        frame = cv2.flip(frame, 1)

        with lock:

            shared["picture"] = frame.copy()
            shared["sequence"] += 1

            near = shared["near"]

        if near is None:

            near = np.zeros(
                (DEPTH_HEIGHT, DEPTH_WIDTH),
                dtype=np.float32
            )

        # Single signed prescription.
        slider = cv2.getTrackbarPos(
            "Prescription (-20D to +20D)",
            WINDOW
        )

        prescription = (slider - 80) / 4.0

        # Separate the signed value into the two conditions.
        myopia_power = max(-prescription, 0)
        hyperopia_power = max(prescription, 0)

        accommodation = (
            cv2.getTrackbarPos(
                "Accommodation (D)", WINDOW
            ) / 4.0
        )

        pupil = (
            cv2.getTrackbarPos(
                "Pupil diameter (mm x2)", WINDOW
            ) / 2.0
        )

        # Estimate scene distances.
        distance = estimate_distance(near)

        # 1. Original.
        original = frame.copy()

        # 2. Live 3D.
        phase = time.perf_counter() * 2 * np.pi / 4.0

        three_d = make_3d_photo(near)

        # 3. Myopia.
        myopia = optical_blur(
            frame,
            distance,
            myopia_power,
            "myopia",
            accommodation,
            pupil
        )

        # 4. Hyperopia.
        hyperopia = optical_blur(
            frame,
            distance,
            hyperopia_power,
            "hyperopia",
            accommodation,
            pupil
        )

        # FPS.
        now = time.perf_counter()

        instant_fps = 1.0 / max(
            now - previous_time,
            1e-6
        )

        fps = (
            fps * 0.85 +
            instant_fps * 0.15
        )

        previous_time = now

        # Build four-panel interface.
        view = make_layout(
            original,
            three_d,
            myopia,
            hyperopia,
            prescription,
            fps
        )

        cv2.imshow(
            WINDOW,
            view
        )

        key = cv2.waitKey(1) & 0xFF

        if key in (ord("q"), 27):
            break

        if cv2.getWindowProperty(
            WINDOW,
            cv2.WND_PROP_VISIBLE
        ) < 1:
            break

finally:

    with lock:
        shared["running"] = False

    worker.join()

    video.release()
    cv2.destroyAllWindows()

    print("Simulator closed.")
