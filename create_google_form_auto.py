# Google Forms API 자동화 - OAuth 인증 후 완전 자동
import os
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/forms.body',
          'https://www.googleapis.com/auth/forms.responses.readonly',
          'https://www.googleapis.com/auth/drive']

def get_credentials():
    """OAuth 인증 - 처음 한번만 브라우저 열림"""
    creds = None
    
    if os.path.exists('google_token.pickle'):
        with open('google_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.json 필요 (구글 클라우드에서 다운로드)
            if not os.path.exists('credentials.json'):
                print("❌ credentials.json 파일이 필요합니다!")
                print("📥 다운로드: https://console.cloud.google.com/apis/credentials")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('google_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def create_retreat_form():
    """리트리트 카페 구글 폼 자동 생성"""
    print("🔐 구글 API 인증 중...")
    creds = get_credentials()
    
    if not creds:
        return
    
    print("✅ 인증 완료! 폼 생성 시작...")
    
    service = build('forms', 'v1', credentials=creds)
    
    # 1. 폼 생성
    form = {
        "info": {
            "title": "리트리트 카페 정보 수집 🏍️☕",
            "documentTitle": "리트리트 카페 정보"
        }
    }
    
    result = service.forms().create(body=form).execute()
    form_id = result['formId']
    print(f"📝 폼 생성 완료! ID: {form_id}")
    
    # 2. 질문 25개 추가
    requests = []
    location_idx = 0
    
    questions = [
        # 기본 정보 (8개)
        {"title": "카페 주소", "type": "TEXT", "required": True},
        {"title": "전화번호", "type": "TEXT", "required": True},
        {"title": "인스타그램 계정", "type": "TEXT", "description": "@"},
        {"title": "영업시간 - 평일", "type": "TEXT", "description": "예) 09:00 - 20:00"},
        {"title": "영업시간 - 주말", "type": "TEXT"},
        {"title": "휴무일", "type": "TEXT", "description": "예) 매주 월요일"},
        {"title": "오토바이 주차", "type": "MULTIPLE_CHOICE", "choices": ["가능", "불가능"]},
        {"title": "리트리트 한 줄 소개", "type": "PARAGRAPH_TEXT"},
        
        # 메뉴 (4개)
        {"title": "아메리카노 가격", "type": "TEXT", "description": "HOT / ICE"},
        {"title": "카페라떼 가격", "type": "TEXT", "description": "HOT / ICE"},
        {"title": "시그니처 메뉴", "type": "PARAGRAPH_TEXT"},
        {"title": "논커피/디저트 메뉴", "type": "PARAGRAPH_TEXT"},
        
        # 원두 (7개)
        {"title": "원두 1 - 이름", "type": "TEXT"},
        {"title": "원두 1 - 맛 특징", "type": "TEXT"},
        {"title": "원두 1 - 가격", "type": "TEXT", "description": "200g / 500g"},
        {"title": "원두 2 - 이름", "type": "TEXT"},
        {"title": "원두 2 - 맛 특징", "type": "TEXT"},
        {"title": "원두 2 - 가격", "type": "TEXT"},
        {"title": "배송비 & 무료배송 기준", "type": "TEXT"},
        
        # 라이더 (3개)
        {"title": "라이더 편의시설", "type": "CHECKBOX", 
         "choices": ["헬멧 보관함", "라이딩 기어 보관", "오토바이 전용 주차", "라이딩 루트 지도"]},
        {"title": "추천 라이딩 코스", "type": "PARAGRAPH_TEXT"},
        {"title": "정기 모임", "type": "TEXT"},
        
        # 기타 (3개)
        {"title": "원두 온라인 주문 원하시나요?", "type": "MULTIPLE_CHOICE", 
         "choices": ["네, 원해요", "아니요, 정보만"]},
        {"title": "꼭 넣고 싶은 내용", "type": "PARAGRAPH_TEXT"},
        {"title": "급한 정도", "type": "DROP_DOWN", 
         "choices": ["여유 있어요 (1-2달)", "보통이요 (2-3주)", "급해요! (1주일)"]},
    ]
    
    for q in questions:
        question_item = {
            "title": q["title"],
            "questionItem": {
                "question": {}
            }
        }
        
        # 질문 타입별 설정
        if q["type"] == "TEXT":
            question_item["questionItem"]["question"]["textQuestion"] = {}
        elif q["type"] == "PARAGRAPH_TEXT":
            question_item["questionItem"]["question"]["textQuestion"] = {"paragraph": True}
        elif q["type"] == "MULTIPLE_CHOICE":
            question_item["questionItem"]["question"]["choiceQuestion"] = {
                "type": "RADIO",
                "options": [{"value": c} for c in q["choices"]]
            }
        elif q["type"] == "CHECKBOX":
            question_item["questionItem"]["question"]["choiceQuestion"] = {
                "type": "CHECKBOX",
                "options": [{"value": c} for c in q["choices"]]
            }
        elif q["type"] == "DROP_DOWN":
            question_item["questionItem"]["question"]["choiceQuestion"] = {
                "type": "DROP_DOWN",
                "options": [{"value": c} for c in q["choices"]]
            }
        
        if q.get("required"):
            question_item["questionItem"]["question"]["required"] = True
        
        if q.get("description"):
            question_item["description"] = q["description"]
        
        requests.append({
            "createItem": {
                "item": question_item,
                "location": {"index": location_idx}
            }
        })
        location_idx += 1
    
    # 모든 질문 한번에 추가
    update = {"requests": requests}
    service.forms().batchUpdate(formId=form_id, body=update).execute()
    
    print(f"✅ 질문 {len(questions)}개 추가 완료!")
    
    # 3. 공유 링크 생성
    view_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
    responses_url = f"https://docs.google.com/forms/d/{form_id}/edit#responses"
    
    print("\n" + "="*60)
    print("🎉 구글 폼 생성 완료!")
    print("="*60)
    print(f"👥 친구 공유용 링크:\n{view_url}\n")
    print(f"📊 응답 확인 링크:\n{responses_url}\n")
    print("="*60)
    
    # 링크 파일로 저장
    with open('retreat_form_links.txt', 'w', encoding='utf-8') as f:
        f.write(f"리트리트 카페 정보 수집 폼\n")
        f.write(f"생성일시: {result.get('info', {}).get('title', '')}\n\n")
        f.write(f"친구 공유용 링크:\n{view_url}\n\n")
        f.write(f"응답 확인 링크:\n{responses_url}\n")
    
    print("💾 링크가 retreat_form_links.txt에 저장되었습니다!")
    
    return view_url

if __name__ == "__main__":
    create_retreat_form()
