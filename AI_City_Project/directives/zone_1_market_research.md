# 📋 Directive: Zone 1. 시장 조사 (Market Research)

## 🎯 목표
`gemini-3-flash-preview` 모델을 사용하여 구글 검색 트렌드를 분석하고, 제작할 영상의 제목, 설명, 태그를 생성합니다.

## 📥 입력 (Inputs)
- 검색 키워드 또는 주제 (예: "2026년 전기차 트렌드")

## 🛠️ 도구 및 스크립트 (Execution)
- `execution/gemini_search_engine.py`: 구글 검색 및 트렌드 데이터 수집
- `execution/content_generator.py`: 기획서(제목/설명/태그) 생성

## 📤 출력 (Outputs)
- `AI_City_Project/.tmp/market_report.json`: 시장 조사 결과 보고서

## ⚠️ 예외 사항 (Edge Cases)
- 검색 결과가 없을 경우: 일반적인 트렌드 키워드로 대체
- API 할당량 초과: 1분 대기 후 재시도 (Self-annealing)
