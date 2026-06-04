import argparse
import base64
import json

import websocket


def main():
    parser = argparse.ArgumentParser(description="Send one JPG frame to Node-RED over WebSocket.")
    parser.add_argument(
        "--image",
        default="yolov5/data/images/zidane.jpg",
        help="Path to a JPG image to send.",
    )
    parser.add_argument(
        "--url",
        default="ws://localhost:1880/image",
        help="Node-RED WebSocket URL.",
    )
    parser.add_argument("--id", default="test_client", help="Client identifier.")
    args = parser.parse_args()

    with open(args.image, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "id": args.id,
        "image": image_base64,
    }

    ws = websocket.create_connection(args.url)
    try:
        ws.send(json.dumps(payload))
    finally:
        ws.close()

    print(f"WebSocket send complete: {args.url}")


if __name__ == "__main__":
    main()
