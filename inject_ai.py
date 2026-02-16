# Quick script to inject AI code into app.py
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the TODO section
old_code = """        # TODO: Call AI analysis (to be implemented)
        # TODO: Send email response (to be implemented)"""

new_code = """        # AI Analysis and Email Automation
        try:
            import matcher
            import email_manager
            
            matched_crew = matcher.match_crew_to_project(inquiry)
            
            if matched_crew:
                for match in matched_crew:
                    email_manager.send_crew_availability_request(match['member'], inquiry, inquiry_id)
                    print(f"[AI] Sent request to {match['member'].get('name')} (Score: {match['score']})")
                
                inquiry['ai_analysis'] = {
                    'matched_crew_count': len(matched_crew),
                    'top_match': matched_crew[0]['member'].get('name')
                }
                inquiry['status'] = 'crew_contacted'
                inquiries[-1] = inquiry
                save_json(INQUIRIES_FILE, inquiries)
            
            email_manager.send_client_confirmation(client_email, inquiry_id, language)
        except Exception as e:
            print(f"[AI] Non-critical error: {e}")"""

content = content.replace(old_code, new_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ app.py updated successfully")
