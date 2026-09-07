# Test email sending with credentials supplied through environment variables
import os

os.environ.setdefault('SMTP_HOST', 'smtp.gmail.com')
os.environ.setdefault('SMTP_PORT', '587')

smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')
if not smtp_user or not smtp_password:
    raise RuntimeError('Set SMTP_USER and SMTP_PASSWORD in the environment before running this test.')

os.environ.setdefault('FROM_EMAIL', smtp_user)
test_recipient = os.getenv('TEST_EMAIL_TO', smtp_user)

import email_manager

print('Testing email system...')

result = email_manager.send_email(
    to_email=test_recipient,
    subject='Test from Cauchemar AI',
    body_html='<h1>Hello!</h1><p>Email system is working!</p>',
    body_text='Hello! Email system is working!'
)

print(f'Email sent: {result}')

if result:
    print('\n✅ SUCCESS: Email sent successfully!')
    print(f'Check the inbox at {test_recipient}')
else:
    print('\n❌ FAILED: Could not send email')
