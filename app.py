from flask import Flask, request, jsonify
import easyocr
import cv2
import numpy as np
import re

app = Flask(__name__)

reader = easyocr.Reader(['ko', 'en'])

PLATE_PATTERN = re.compile(r'\d{2,3}[가-힣]\d{4}')

DELIVERY_BRANDS = [
    # 치킨
    "BBQ", "교촌", "bhc", "굽네치킨", "네네치킨", "60계치킨",
    "노랑통닭", "처갓집", "푸라닭", "맥시칸치킨", "호식이두마리치킨",
    # 피자
    "피자헛", "도미노", "파파존스", "미스터피자",
    # 버거
    "맥도날드", "버거킹", "롯데리아", "KFC", "써브웨이", "맘스터치",
    # 중식/분식
    "홍콩반점", "김가네", "죠스떡볶이", "엽기떡볶이",
    # 기타
    "스타벅스", "이디야", "빽다방", "컴포즈커피"
]

def extract_info(image):
    results = reader.readtext(image)
    
    plate = None
    brands = []
    
    for (bbox, text, conf) in results:
        cleaned = text.replace(" ", "")
        
        # 번호판 패턴 체크
        if PLATE_PATTERN.match(cleaned) and conf > 0.5:
            plate = {"plate": cleaned, "confidence": conf}
        
        # 브랜드명 체크 (한글 2글자 이상, 숫자 아닌 것)
        elif len(cleaned) >= 2 and not cleaned.isdigit() and conf > 0.7:
            brands.append({"brand": cleaned, "confidence": conf})
    
    return {
        "plate": plate["plate"] if plate else "UNKNOWN",
        "brands": brands 
    }

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

    result = extract_info(image)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)