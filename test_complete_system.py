# Complete System Test
import os
os.environ['FROM_EMAIL'] = 'qmfforfhem@gmail.com'

print("="*50)
print("COMPLETE SYSTEM TEST")
print("="*50)

# Test 1: Matcher
print("\n1. Testing Crew Matcher...")
import matcher

test_inquiry = {
    'project': {
        'type': 'item_hair',
        'description': 'Need a stylish hair item for collaboration',
        'budget': '100k_200k',
        'deadline': '1 week'
    },
    'client': {
        'name': 'Test Client',
        'email': 'client@test.com'
    }
}

matches = matcher.match_crew_to_project(test_inquiry)
print(f"✅ Found {len(matches)} matching crew members:")
for m in matches:
    print(f"   - {m['member']['name']} (Score: {m['score']}) - {m['reason']}")

# Test 2: Email Queue
print("\n2. Testing Email System...")
import email_manager

for match in matches:
    result = email_manager.send_crew_availability_request(
        match['member'],
        test_inquiry,
        'TEST_INQUIRY_001'
    )
    if result:
        print(f"✅ Email queued for {match['member']['name']}")

# Send client confirmation
email_manager.send_client_confirmation('client@test.com', 'TEST_INQUIRY_001', 'ko')
print("✅ Client confirmation queued")

# Check queue
print("\n3. Checking Email Queue...")
import email_queue
queued = email_queue.get_queued_emails()
print(f"✅ Total emails in queue: {len(queued)}")
for email in queued[-3:]:  # Show last 3
    print(f"   - To: {email['to']}")
    print(f"     Subject: {email['subject']}")
    print(f"     Preview: {email['id']}.html")

print("\n" + "="*50)
print("SYSTEM TEST COMPLETE!")
print("="*50)
print("\nEmail previews are in:")
print("projects/Cauchemar/data/email_queue/")
print("\nOpen the .html files to see email templates!")
