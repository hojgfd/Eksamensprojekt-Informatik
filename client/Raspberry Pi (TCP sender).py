import socket
import struct
import cv2

HOST = '127.0.0.1:5000'
PORT = 5001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Encode frame as JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    data = buffer.tobytes()

    # Pack size + data
    message = struct.pack("Q", len(data)) + data
    client_socket.sendall(message)

cap.release()
client_socket.close()