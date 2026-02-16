# 📋 Directive: Zone 2. 자재 생산 (Asset Factory)

## 🎯 목표
`gemini-3-pro-image-preview` 모델을 사용하여 트렌드에 맞는 고화질 제품 이미지를 생산합니다.

## 📥 입력 (Inputs)
- `market_report.json`에서 추출된 제품 상세 묘사 및 키워드

## 🛠️ 도구 및 스크립트 (Execution)
- `execution/image_generator.py`: Gemini-3-Pro-Image를 통한 이미지 생성 스크립트

## 📤 출력 (Outputs)
- `AI_City_Project/backend/assets/product_image_1.png`: 생성된 원자재 이미지

## ⚠️ 예외 사항 (Edge Cases)
- 이미지 생성 실패: 프롬프트를 단순화하여 재시도 (Max 3회)
- 부적절한 콘텐츠 필터링: 안전한 키워드로 프롬프트 수정
