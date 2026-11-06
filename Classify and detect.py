import json

import cv2
import numpy as np

MIN_SCORE = 0.5
SIZE = 640
STRIDES = [8, 16, 32]
FONT = cv2.FONT_HERSHEY_SIMPLEX

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "labels.json")) as file:
    coco = json.load(file)["coco"]
NAMES = [coco[key] for key in sorted(coco, key=int)]

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

net = cv2.dnn.readNetFromONNX(
    os.path.join(BASE_DIR, "detector.onnx")
)

cells = [SIZE // stride for stride in STRIDES]
GRID = np.concatenate([np.indices((n, n))[::-1].reshape(2, -1).T for n in cells])
STRIDE = np.concatenate([np.full((n * n, 1), s) for n, s in zip(cells, STRIDES)])


def detect(frame):
    height, width = frame.shape[:2]
    scale = min(SIZE / height, SIZE / width)
    small = cv2.resize(frame, (round(width * scale), round(height * scale)))
    canvas = np.full((SIZE, SIZE, 3), 114, np.uint8)
    canvas[:small.shape[0], :small.shape[1]] = small

    net.setInput(cv2.dnn.blobFromImage(canvas))
    output = net.forward()[0]

    centres = (output[:, :2] + GRID) * STRIDE
    sizes = np.exp(output[:, 2:4]) * STRIDE
    scores = output[:, 4:5] * output[:, 5:]
    class_ids = scores.argmax(axis=1)
    confidences = scores.max(axis=1)

    boxes = (np.hstack([centres - sizes / 2, sizes]) / scale).astype(int)
    keep = cv2.dnn.NMSBoxesBatched(
        boxes.tolist(), confidences.tolist(), class_ids.tolist(), MIN_SCORE, 0.5
    )
    return [(NAMES[class_ids[i]], boxes[i]) for i in keep]


video = cv2.VideoCapture(0)

while True:
    ok, frame = video.read()
    if not ok:
        break
    for name, (x, y, w, h) in detect(frame):
        hsv = np.uint8([[[NAMES.index(name) * 29 % 180, 255, 255]]])
        colour = tuple(int(c) for c in cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0])
        cv2.rectangle(frame, (x, y), (x + w, y + h), colour, 2)
        cv2.putText(frame, name, (x, y - 6), FONT, 0.6, colour, 2)
    cv2.imshow("Live detect", frame)
    if cv2.waitKey(1) & 255 == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
