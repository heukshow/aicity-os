"""
Email Manager Module V2
Uses email queue system to avoid Windows SMTP encoding issues
"""

import os
from email_queue import queue_email
from typing import Dict

FROM_EMAIL = os.getenv('FROM_EMAIL', 'redacted-private-mailbox@example.invalid')
FROM_NAME = "Cauchemar Crew"

def send_email(to_email: str, subject: str, body_html: str, body_text: str = None) -> bool:
    """Queue an email for sending"""
    try:
        email_id = queue_email(
            to_email=to_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text or '',
            metadata={'from': FROM_EMAIL, 'from_name': FROM_NAME}
        )
        print(f"[EMAIL] Queued for {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"[EMAIL] Error: {e}")
        return False

def send_crew_availability_request(crew_member: Dict, inquiry: Dict, inquiry_id: str) -> bool:
    """Send availability request to crew member"""
    crew_name = crew_member.get('name', 'Creator')
    crew_email = crew_member.get('email')
    
    if not crew_email:
        print(f"[EMAIL] No email for: {crew_name}")
        return False
    
    client_name = inquiry.get('client', {}).get('name', 'Client')
    project_type = inquiry.get('project', {}).get('type', 'Unknown')
    budget = inquiry.get('project', {}).get('budget', 'Not specified')
    deadline = inquiry.get('project', {}).get('deadline', 'Flexible')
    description = inquiry.get('project', {}).get('description', '')
    
    type_map = {
        'item_hair': '헤어 아이템',
        'item_top': '상의 아이템',
        'item_bottom': '하의 아이템', 
        'item_shoes': '신발 아이템',
        'item_other': '기타 아이템',
        'promo_sns': 'SNS 홍보',
        'promo_video': '영상 제작',
        'other': '기타'
    }
    project_type_kr = type_map.get(project_type, project_type)
    
    # Get crew portfolio and prices
    portfolio = crew_member.get('portfolio', [])
    prices = crew_member.get('prices', {})
    
    # Build portfolio section
    portfolio_html = ""
    if portfolio:
        portfolio_html = "<h3>Your Portfolio Items:</h3><ul>"
        for item in portfolio[:3]:  # Show first 3
            if isinstance(item, dict):
                name = item.get('name', 'Item')
                price = item.get('price', 'N/A')
                portfolio_html += f"<li>{name} - {price}</li>"
        portfolio_html += "</ul>"
    
    subject = f"[Cauchemar] New Project: {project_type_kr}"
    
    body_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5;">
        <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0">🎨 New Project Request</h1>
            <p style="margin: 5px 0 0; opacity: 0.9">Cauchemar AI Manager</p>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px;">
            <p>Hello <strong>{crew_name}</strong>!</p>
            <p>A new project request matches your skills.</p>
            
            <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h2 style="color: #667eea; margin-top: 0">📋 Project Details</h2>
                <table style="width: 100%">
                    <tr><td style="padding: 8px 0; font-weight: bold">Client:</td><td>{client_name}</td></tr>
                    <tr><td style="padding: 8px 0; font-weight: bold">Type:</td><td>{project_type_kr}</td></tr>
                    <tr><td style="padding: 8px 0; font-weight: bold">Budget:</td><td>{budget}</td></tr>
                    <tr><td style="padding: 8px 0; font-weight: bold">Deadline:</td><td>{deadline if deadline else 'Flexible'}</td></tr>
                </table>
                <div style="margin-top: 15px">
                    <p style="font-weight: bold">Description:</p>
                    <p style="background: white; padding: 10px; border-radius: 5px">{description}</p>
                </div>
            </div>
            
            {portfolio_html}
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #856404; margin-top: 0">❓ Please Reply With:</h3>
                <ul>
                    <li><strong>Available:</strong> Yes/No</li>
                    <li><strong>Your Quote:</strong> Price</li>
                    <li><strong>Timeline:</strong> Days needed</li>
                    <li><strong>Questions:</strong> Any clarifications</li>
                </ul>
            </div>
            
            <p><strong>Reference ID:</strong> <code>{inquiry_id}</code></p>
            <p>Reply to this email and AI will process your response.</p>
            
            <p style="color: #666; font-size: 14px; border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px">
                Thanks,<br><strong>Cauchemar Crew AI</strong>
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    return send_email(crew_email, subject, body_html)

def send_client_confirmation(client_email: str, inquiry_id: str, language: str = 'ko') -> bool:
    """Send confirmation to client"""
    if language == 'ko':
        subject = "[Cauchemar] 문의 접수 완료"
        body_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px">
        <h2 style="color: #667eea">✅ 문의가 접수되었습니다</h2>
        <p>안녕하세요!</p>
        <p>프로젝트 문의를 받았습니다. AI가 분석 중이며, 곧 적합한 크리에이터를 매칭하여 연락드리겠습니다.</p>
        <p><strong>Reference ID:</strong> <code>{inquiry_id}</code></p>
        <p><strong>예상 응답:</strong> 24시간 이내</p>
        <p>감사합니다!<br><strong>Cauchemar Crew</strong></p>
    </div>
</body>
</html>
        """
    else:
        subject = "[Cauchemar] Inquiry Received"
        body_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px">
        <h2 style="color: #667eea">✅ Inquiry Received</h2>
        <p>Hello!</p>
        <p>We received your project inquiry. Our AI is analyzing it and will match you with a suitable creator soon.</p>
        <p><strong>Reference ID:</strong> <code>{inquiry_id}</code></p>
        <p><strong>Expected Response:</strong> Within 24 hours</p>
        <p>Thank you!<br><strong>Cauchemar Crew</strong></p>
    </div>
</body>
</html>
        """
    
    return send_email(client_email, subject, body_html)

if __name__ == '__main__':
    print("Email Manager V2 loaded")
