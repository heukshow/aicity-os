# Test email sending with proper encoding
import os
os.environ['SMTP_HOST'] = 'smtp.gmail.com'
os.environ['SMTP_PORT'] = '587'
os.environ['SMTP_USER'] = 'qmfforfhem@gmail.com'
os.environ['SMTP_PASSWORD'] = 'wzcglgsulhcgscuo'
os.environ['FROM_EMAIL'] = 'qmfforfhem@gmail.com'

import email_manager

print("Testing email system...")

# Simple test email
result = email_manager.send_email(
    to_email='qmfforfhem@gmail.com',
    subject='Test from Cauchemar AI',
    body_html='<h1>Hello!</h1><p>Email system is working!</p>',
    body_text='Hello! Email system is working!'
)

print(f"Email sent: {result}")

if result:
    print("\n✅ SUCCESS: Email sent successfully!")
    print("Check your inbox at qmfforfhem@gmail.com")
else:
    print("\n❌ FAILED: Could not send email")
