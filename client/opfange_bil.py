from ultralytics import YOLO

import cv2
import numpy as np

from collections import defaultdict
import csv

# n, s, m, l, x (sorteret efter mindste til største model)
model = YOLO("yolo26n.pt")
confidence_threshold = 0.3

vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
assert vs.isOpened()


def run_classification_model(model, frame, confidence_threshold):
    result = model(frame)[0]
    counter = defaultdict(int)

    for box in result.boxes:
        class_id = int(box.cls)
        confidence = float(box.conf)
        name = model.names[class_id]
        print(f"Detected: {name} ({confidence:.2%} confidence)")

        if confidence > confidence_threshold:
            counter[name] += 1

    # print(result.boxes.xyxy)
    # print(result.summary())

    annotated_frame = result.plot()

    return annotated_frame, counter

def save_image(path, image):
    cv2.imwrite(f'{path}', image)

def save_count(path, counter: dict):
    fields = ["name", "amount"]
    counter_sorted = sorted(counter.items(), key=lambda item: item[0])

    with open(f'{path}', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(counter_sorted)

while True:
    vs.read()
    ret, frame = vs.read()

    annotated_frame, counter = run_classification_model(model, frame, confidence_threshold)
    save_image("test/frame.jpg", annotated_frame)
    save_count("test/count.csv", counter)

    cv2.putText(annotated_frame, f"{dict(counter)}", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 1)
    cv2.imshow("YOLO", annotated_frame)

    if cv2.waitKey(0) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
