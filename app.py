from flask import Flask, request, jsonify
import easyocr
import cv2
import numpy as np
import re

app = Flask(__name__)

reader = easyocr.Reader(['ko', 'en'])

PLATE_PATTERN = re.compile(r'\d{2,3}[가-힣]\d\{4}')

@app.route('/health')
def health():
    return jsonify({'status' : 'ok'})

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({'error' : '이미지 없음'}), 400

    file = request.files['image']
    img_array = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    result = extract_plate(image)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)