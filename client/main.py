
import cv2
import sys
import json
import base64
import requests

cam = cv2.VideoCapture(0)
URL = 'http://127.0.0.1:8080/api/v1/feed/push-frame'

def encode_base64(content):
    return str(base64.b64encode(content), encoding='utf-8')

CAPTURE_FRAMES = int(sys.argv[1])

for i in range(0, CAPTURE_FRAMES):
    # Take picture 
    _, frame = cam.read()    

    # Convert frame to bytes
    img_bytes = cv2.imencode('.jpg', frame)[1].tobytes()

    # encode bytes before sending
    img_b64 = encode_base64(img_bytes)

    # Form request data
    request_data = {
        'frame': img_b64,
        'uuid': "shitcam"
    }

    response = {}
    try:
        # submit
        resp = requests.post(URL, json=request_data)
        response = resp.json()
    except Exception as e:
        print(f'Request error: \n{e}')

    print(json.dumps(response, indent=2))
