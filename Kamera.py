import cv2 as cv
import time
import requests

serverurl = "http://127.0.0.1:5000"
cap = cv.VideoCapture(1, cv.CAP_DSHOW)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    filename = str(time.time())+".jpg"
    cv.imwrite(filename, frame)

    # Send POST request
    with open(filename, 'rb') as f:
        files = {'image': f}
        response = requests.post(serverurl+'/upload', files=files)

    print(response.status_code, response.text)
    time.sleep(1)

cap.release()