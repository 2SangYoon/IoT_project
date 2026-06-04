# Glasses Detection Server

YOLOv5 기반 안경 착용 여부 판별 Flask 서버입니다. 클라이언트나 Node-RED 플로우가 base64 이미지 데이터를 `/predict`로 보내면, 서버는 안경 착용 여부와 confidence 값을 JSON으로 반환합니다.

## 구성

```text
IoT_project/
├─ app.py                         # Flask API 서버
├─ glasses_yolov5s_finetuned.pt   # 안경 탐지 fine-tuned YOLOv5 모델
├─ flows.json                     # Node-RED 플로우 예시
├─ requirements.txt               # Python 의존성 목록
└─ yolov5/                        # torch.hub.load(source="local")에 필요한 YOLOv5 코드
```

## 모델 정보

이 프로젝트는 `glasses_yolov5s_finetuned.pt`를 사용합니다.

모델 클래스는 다음과 같습니다.

```text
0 = no_glasses
1 = glasses
```

`app.py`에서는 `model.classes = [1]`로 설정해 `glasses` 클래스만 결과에 남깁니다. 그래서 응답에서 `wearing_glasses`가 `true`이면 안경이 탐지된 것입니다.


## 설치

Python 가상환경을 만든 뒤 의존성을 설치합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

PyTorch 설치가 환경에 따라 실패하면 [PyTorch 공식 설치 안내](https://pytorch.org/get-started/locally/)에서 CPU 또는 CUDA 환경에 맞는 명령어로 `torch`, `torchvision`을 먼저 설치한 뒤 다시 `requirements.txt`를 설치하세요.

## 실행

```powershell
.\.venv\Scripts\activate
python app.py
```

기본 서버 주소는 다음과 같습니다.

```text
http://127.0.0.1:5001
```

이 터미널은 모델 서버가 계속 요청을 받을 수 있도록 닫지 마세요.

## API

### POST `/predict`

요청 JSON:

```json
{
  "image": "base64 encoded image"
}
```

`data:image/jpeg;base64,...` 형태의 data URL도 사용할 수 있습니다.

응답 JSON:

```json
{
  "result": "glasses",
  "wearing_glasses": true,
  "confidence": 0.7939
}
```

필드 의미:

- `result`: `"glasses"` 또는 `"no_glasses"`
- `wearing_glasses`: 안경 탐지 여부
- `confidence`: 탐지된 `glasses` 클래스 중 가장 높은 confidence

## 테스트 예시

PowerShell에서 JPG 파일을 base64로 보내려면 다음처럼 확인할 수 있습니다.

```powershell
$bytes = [System.IO.File]::ReadAllBytes("sample.jpg")
$base64 = [Convert]::ToBase64String($bytes)
$body = @{ image = $base64 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:5001/predict" -Method Post -Body $body -ContentType "application/json"
```

## Node-RED 연동

이 프로젝트의 연동 구조는 다음과 같습니다.

```text
WebSocket client
→ Node-RED WebSocket /image
→ Node-RED function
→ HTTP POST http://localhost:5001/predict
→ Flask model server
→ Node-RED Dashboard
```

Node-RED를 프로젝트 로컬 런타임으로 설치하려면 다음 명령을 실행합니다.

```powershell
npm install --prefix .node-red node-red node-red-dashboard
```

설치 후 `flows.json`을 바로 로드해서 실행할 수 있습니다.

```powershell
.\.node-red\node_modules\.bin\node-red.cmd -u .node-red flows.json
```

Node-RED editor:

```text
http://localhost:1880
```

Dashboard:

```text
http://localhost:1880/ui
```

`flows.json`의 주요 설정은 다음과 같습니다.

- WebSocket listener path: `/image`
- Flask HTTP request URL: `http://localhost:5001/predict`
- Dashboard text format: `{{msg.payload.result}}`

클라이언트는 아래 형식으로 WebSocket에 이미지를 보내면 됩니다.

```json
{
  "id": "client_1",
  "image": "raw base64 image string"
}
```

WebSocket 주소:

```text
ws://localhost:1880/image
```

다른 노트북에서 접속하면 `localhost` 대신 Node-RED가 실행 중인 서버 IP를 사용합니다.

```text
ws://SERVER_IP:1880/image
```

플로우 내부의 HTTP 요청 노드는 기본적으로 다음 주소를 호출합니다.

```text
http://localhost:5001/predict
```

서버가 다른 PC에서 실행 중이면 Node-RED의 HTTP 요청 URL을 해당 서버 IP로 바꾸세요.

## WebSocket 테스트

`test_ws_send.py`는 JPG 파일 하나를 Node-RED WebSocket으로 보내는 테스트 스크립트입니다.

```powershell
.\.venv\Scripts\activate
python test_ws_send.py
```

기본 테스트 이미지는 `yolov5/data/images/zidane.jpg`입니다. 다른 이미지를 보내려면:

```powershell
python test_ws_send.py --image path\to\image.jpg
```

성공하면 Node-RED Debug 창과 Dashboard에서 `glasses` 또는 `no_glasses` 결과를 확인할 수 있습니다.
