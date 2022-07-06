
import cv2
import base64
import numpy as np
from threading import Thread
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

SUBMIT_FRAME_ENDPOINT = '/api/v1/feed/push-frame'

def decode_base64(content):
    return base64.b64decode(content) if not isinstance(content, bytes) else content

class ImageProcessor:

    def save_frame(self, frame_bytes):
        # Set font for date
        font = cv2.FONT_HERSHEY_PLAIN

        # Convert image bytes to numpy array
        nparr = np.frombuffer(frame_bytes, np.uint8)

        # Import numpy array as cv2 frame
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Resize frame to meet server preference
        sized_frame = cv2.resize(frame,(1280,720),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
        
        # Put the current date on the frame
        cv2.putText(sized_frame, str(datetime.now()), (20, 40), font, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Show the frame for debugging
        cv2.imshow('frame', sized_frame)
        cv2.waitKey(0)

    def process_image(self, id, image_bytes):

        # Process image in short-lived thread so the camera isnt waiting for a response
        # Goal is to increase performance
        modthread = Thread(target=self.save_frame, args=(image_bytes,))
        modthread.daemon = True
        modthread.start()

        return {'msg': f'Receieved {len(image_bytes)} bytes from device {id}.'}


class Api:

    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def start(self):
        try:
            app.run(
                host=self.host,
                port=self.port
            )
            return True
        except Exception as e:
            print(f'Erro starting server\n{e}')

# Endpoint example for camera submittion without authentication
@app.route(SUBMIT_FRAME_ENDPOINT, methods=['POST'])
def submit_frame():
    response = {}
    im = ImageProcessor()

    try:
        values = request.get_json()
        
        frame_bytes_b64 = values['frame']
        device_id = values['uuid']

        # Decode base64
        frame_bytes = decode_base64(frame_bytes_b64)

        # Start image processing
        response = im.process_image(
            id=device_id,
            image_bytes=frame_bytes
        )
    except Exception as e:
        response = {'err': str(e)}
    
    return jsonify(response)
        
if __name__ == '__main__':
    # Start API and wait for camera submissions
    api = Api(
        host='127.0.0.1',
        port=8080
    )

    api.start()
