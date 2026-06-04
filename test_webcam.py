import base64
import json
import time

import cv2
import websocket


WS_URL = "ws://localhost:1880/image"


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot open webcam.")
        return

    print("Webcam test started.")
    print("Press SPACE to send the current frame to Node-RED.")
    print("Press ESC to exit.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Cannot read frame from webcam.")
            break

        cv2.imshow("Webcam - Press SPACE to send", frame)
        key = cv2.waitKey(1)

        if key == 27:
            break

        if key == 32:
            _, buffer = cv2.imencode(".jpg", frame)
            image_base64 = base64.b64encode(buffer).decode("utf-8")

            payload = {
                "id": "webcam_test",
                "image": image_base64,
            }

            try:
                ws = websocket.create_connection(WS_URL)
                try:
                    ws.send(json.dumps(payload))
                finally:
                    ws.close()
                print("Webcam frame sent.")
            except Exception as e:
                print("WebSocket send failed:", e)

            time.sleep(0.5)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
