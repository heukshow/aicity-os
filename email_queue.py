"""
Simple Email Queue System
Bypasses SMTP encoding issues by saving emails to files for manual review/sending
"""

import json
import os
from datetime import datetime
from typing import Dict

EMAIL_QUEUE_DIR = os.path.join('projects', 'Cauchemar', 'data', 'email_queue')
os.makedirs(EMAIL_QUEUE_DIR, exist_ok=True)

def queue_email(to_email: str, subject: str, body_html: str, body_text: str = None, metadata: Dict = None) -> str:
    """
    Save email to queue instead of sending directly.
    Returns email ID.
    """
    email_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    email_data = {
        'id': email_id,
        'timestamp': datetime.now().isoformat(),
        'to': to_email,
        'subject': subject,
        'body_html': body_html,
        'body_text': body_text or '',
        'metadata': metadata or {},
        'status': 'queued'
    }
    
    # Save as JSON
    filepath = os.path.join(EMAIL_QUEUE_DIR, f"{email_id}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(email_data, f, indent=2, ensure_ascii=False)
    
    # Also save HTML for preview
    html_path = os.path.join(EMAIL_QUEUE_DIR, f"{email_id}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{subject}</title>
</head>
<body>
    <div style="background: #f0f0f0; padding: 20px;">
        <div style="background: white; padding: 20px; max-width: 800px; margin: 0 auto;">
            <p><strong>To:</strong> {to_email}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <hr>
            {body_html}
        </div>
    </div>
</body>
</html>
        """)
    
    print(f"[EMAIL QUEUE] Saved: {email_id} → {to_email}")
    print(f"[EMAIL QUEUE] Preview: {html_path}")
    
    return email_id

def get_queued_emails():
    """Get all queued emails"""
    emails = []
    if not os.path.exists(EMAIL_QUEUE_DIR):
        return emails
    
    for filename in os.listdir(EMAIL_QUEUE_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(EMAIL_QUEUE_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                emails.append(json.load(f))
    
    return sorted(emails, key=lambda x: x['timestamp'], reverse=True)

def mark_email_sent(email_id: str):
    """Mark email as sent"""
    filepath = os.path.join(EMAIL_QUEUE_DIR, f"{email_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['status'] = 'sent'
        data['sent_at'] = datetime.now().isoformat()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    # Test
    email_id = queue_email(
        'test@example.com',
        'Test Email',
        '<h1>Hello!</h1><p>This is a test.</p>',
        'Hello! This is a test.'
    )
    print(f"Created email: {email_id}")
    print(f"Queued emails: {len(get_queued_emails())}")
