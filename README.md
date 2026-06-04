# 👓 안경 착용 탐지 AI 서버 (Glasses Detection Server)

YOLOv5 모델과 Flask, Node-RED를 연동한 IoT 프로젝트 중앙 서버 파이프라인입니다. 클라이언트가 웹캠으로 전송한 이미지를 분석하여 안경 착용 여부를 실시간으로 판별합니다.

## 📁 폴더 구조 (Project Structure)
- `app.py`: YOLOv5 모델 기반 안경 착용 여부 판별 Flask 서버
- `best.pt`: 안경(glasses) 검출용 학습 완료 가중치 파일
- `requirements.txt`: 프로젝트 구동을 위한 파이썬 라이브러리 목록
- `node_red_flow.json`: Node-RED 플로우 백업 파일 (Import용)

## 🚀 서버 구동 방법 (How to Run)
1. **가상환경 활성화:** `source venv/bin/activate`
2. **패키지 설치:** `pip install -r requirements.txt`
3. **Flask 서버 실행:** `python app.py` (5001번 포트)

## 📡 팀원 연동 가이드 (API 규격)
- **📸 클라이언트 (카메라 담당):** `ws://[서버_IP]:1880/image` 경로로 `{"id": "기기ID", "image": "순수 base64 문자열"}` 포맷으로 전송해 주세요.
- **📊 UI / 대시보드 담당:** 결과 데이터는 JSON Object 형태로 반환됩니다. `msg.payload.result`("glasses"/"no_glasses")와 `msg.payload.confidence`(확률) 변수를 사용해 화면을 꾸며주세요.
