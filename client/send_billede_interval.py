from opfange_bil import *
import time
import requests


if __name__ == '__main__':
    model = YOLO("yolo26n.pt")
    confidence_threshold = 0.3

    vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    assert vs.isOpened()
    vs.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    last_time = time.time() - 60*10
    time_wait = 60*10

    while True:
        if time.time() > last_time + time_wait:
            last_time = time.time()
            print("tager billede og sender")
            vs.read()
            ret, frame = vs.read()
            annotated_frame, counter = run_classification_model(model, frame, confidence_threshold)

            save_image("test/frame.jpg", annotated_frame)
            save_count("test/count.csv", counter)

            with open("test/count.csv", "rb") as count_f, open("test/frame.jpg", "rb") as image_f:
                response = requests.post(
                    "http://127.0.0.1:5000/upload",
                    files={
                        "count": count_f,
                        "image": image_f,
                    }
                )
            print(response.text.strip())

    cv2.destroyAllWindows()

