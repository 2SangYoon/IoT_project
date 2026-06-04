from flask import Flask, request, jsonify
import torch
import base64
import io
from PIL import Image

app = Flask(__name__)

# YOLOv5 로컬 repo + 모델 로드
model = torch.hub.load(
    './yolov5',
    'custom',
    path='./best.pt',
    source='local'
)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data or "image" not in data:
            return jsonify({
                "error": "No image field in request"
            }), 400

        image_data = data["image"]

        # data:image/jpeg;base64,... 형태면 앞부분 제거
        if "," in image_data:
            image_data = image_data.split(",")[1]

        # base64 -> 이미지
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # 추론
        results = model(image)

        # pandas dataframe 형태로 결과 추출
        detections = results.pandas().xyxy[0]

        wearing_glasses = False
        best_confidence = 0.0

        for _, row in detections.iterrows():
            class_name = row["name"]
            conf = float(row["confidence"])

            if class_name == "glasses":
                wearing_glasses = True
                if conf > best_confidence:
                    best_confidence = conf

        return jsonify({
            "result": "glasses" if wearing_glasses else "no_glasses",
            "wearing_glasses": wearing_glasses,
            "confidence": round(best_confidence, 4)
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

