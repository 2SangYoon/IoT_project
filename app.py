from flask import Flask, request, jsonify
import torch
import base64
import io
from PIL import Image

app = Flask(__name__)

MODEL_PATH = "./glasses_yolov5s_finetuned.pt"

# Load the local YOLOv5 code and the fine-tuned glasses detector.
model = torch.hub.load(
    "./yolov5",
    "custom",
    path=MODEL_PATH,
    source="local",
)
model.conf = 0.05

# Keep only the glasses class in YOLOv5 detections.
# Class index: 0 = no_glasses, 1 = glasses.
model.classes = [1]


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data or "image" not in data:
            return jsonify({"error": "No image field in request"}), 400

        image_data = data["image"]

        # Accept both raw base64 and data URL style payloads.
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        results = model(image)
        detections = results.pandas().xyxy[0]

        print("Detections:")
        print(detections)

        wearing_glasses = False
        best_confidence = 0.0

        for _, row in detections.iterrows():
            class_name = row["name"]
            conf = float(row["confidence"])

            if class_name == "glasses":
                wearing_glasses = True
                best_confidence = max(best_confidence, conf)

        return jsonify({
            "result": "glasses" if wearing_glasses else "no_glasses",
            "wearing_glasses": wearing_glasses,
            "confidence": round(best_confidence, 4),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
