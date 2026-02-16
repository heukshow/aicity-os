# Google Forms API를 사용한 자동 폼 생성
# pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os.path

SCOPES = ['https://www.googleapis.com/auth/forms.body', 
          'https://www.googleapis.com/auth/drive']

def create_retreat_cafe_form():
    """Create Google Form for Retreat Cafe"""
    creds = None
    
    # Token 로드
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # 로그인 필요시
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('forms', 'v1', credentials=creds)
    
    # 폼 생성
    form = {
        "info": {
            "title": "리트리트 카페 정보 수집",
            "documentTitle": "리트리트 카페 정보"
        }
    }
    
    result = service.forms().create(body=form).execute()
    form_id = result['formId']
    
    # 질문 추가
    questions = [
        # 섹션 1: 기본 정보
        {"title": "카페 주소", "required": True, "type": "SHORT_ANSWER"},
        {"title": "전화번호", "required": True, "type": "SHORT_ANSWER"},
        {"title": "인스타그램 계정", "type": "SHORT_ANSWER", "description": "@"},
        {"title": "영업시간 - 평일", "type": "SHORT_ANSWER", "description": "예) 09:00 - 20:00"},
        {"title": "영업시간 - 주말", "type": "SHORT_ANSWER"},
        {"title": "휴무일", "type": "SHORT_ANSWER", "description": "예) 매주 월요일"},
        {"title": "오토바이 주차 가능 여부", "type": "MULTIPLE_CHOICE", 
         "choices": ["가능", "불가능"]},
        {"title": "리트리트 한 줄 소개", "type": "PARAGRAPH"},
        
        # 섹션 2: 메뉴
        {"title": "아메리카노 가격", "type": "SHORT_ANSWER", "description": "HOT / ICE"},
        {"title": "카페라떼 가격", "type": "SHORT_ANSWER", "description": "HOT / ICE"},
        {"title": "시그니처 메뉴", "type": "PARAGRAPH"},
        {"title": "논커피/디저트 메뉴", "type": "PARAGRAPH"},
        
        # 섹션 3: 원두
        {"title": "원두 1 - 이름", "type": "SHORT_ANSWER"},
        {"title": "원두 1 - 맛 특징", "type": "SHORT_ANSWER"},
        {"title": "원두 1 - 가격", "type": "SHORT_ANSWER", "description": "200g / 500g"},
        {"title": "원두 2 - 이름", "type": "SHORT_ANSWER"},
        {"title": "원두 2 - 맛 특징", "type": "SHORT_ANSWER"},
        {"title": "원두 2 - 가격", "type": "SHORT_ANSWER"},
        {"title": "배송비 & 무료배송 기준", "type": "SHORT_ANSWER"},
        
        # 섹션 4: 라이더
        {"title": "라이더 편의시설", "type": "CHECKBOX", 
         "choices": ["헬멧 보관함", "라이딩 기어 보관", "오토바이 전용 주차", "라이딩 루트 지도"]},
        {"title": "추천 라이딩 코스", "type": "PARAGRAPH"},
        {"title": "정기 모임", "type": "SHORT_ANSWER"},
        
        # 섹션 5: 기타
        {"title": "원두 온라인 주문 원하시나요?", "type": "MULTIPLE_CHOICE", 
         "choices": ["네, 원해요", "아니요, 정보만"]},
        {"title": "꼭 넣고 싶은 내용", "type": "PARAGRAPH"},
        {"title": "급한 정도", "type": "DROP_DOWN", 
         "choices": ["여유 있어요 (1-2달)", "보통이요 (2-3주)", "급해요! (1주일)"]},
    ]
    
    # 질문 업데이트
    requests_list = []
    for idx, q in enumerate(questions):
        item = {
            "title": q["title"],
            "questionItem": {
                "question": {}
            }
        }
        
        if q["type"] == "SHORT_ANSWER":
            item["questionItem"]["question"]["textQuestion"] = {}
        elif q["type"] == "PARAGRAPH":
            item["questionItem"]["question"]["textQuestion"] = {"paragraph": True}
        elif q["type"] == "MULTIPLE_CHOICE":
            item["questionItem"]["question"]["choiceQuestion"] = {
                "type": "RADIO",
                "options": [{"value": c} for c in q["choices"]]
            }
        elif q["type"] == "CHECKBOX":
            item["questionItem"]["question"]["choiceQuestion"] = {
                "type": "CHECKBOX",
                "options": [{"value": c} for c in q["choices"]]
            }
        elif q["type"] == "DROP_DOWN":
            item["questionItem"]["question"]["choiceQuestion"] = {
                "type": "DROP_DOWN",
                "options": [{"value": c} for c in q["choices"]]
            }
        
        if q.get("required"):
            item["questionItem"]["question"]["required"] = True
        
        if q.get("description"):
            item["description"] = q["description"]
        
        requests_list.append({
            "createItem": {
                "item": item,
                "location": {"index": idx}
            }
        })
    
    update_body = {"requests": requests_list}
    service.forms().batchUpdate(formId=form_id, body=update_body).execute()
    
    # 공유 링크 생성
    form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
    view_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
    
    print("✅ 구글 폼 생성 완료!")
    print(f"📝 폼 편집: {form_url}")
    print(f"👥 공유 링크: {view_url}")
    
    return view_url

if __name__ == "__main__":
    create_retreat_cafe_form()
