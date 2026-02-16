# Add admin APIs to app.py
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "if __name__"
insert_index = -1
for i, line in enumerate(lines):
    if 'if __name__' in line:
        insert_index = i
        break

if insert_index > 0:
    # Insert admin APIs before main
    admin_apis = """
# Admin API Endpoints for Email Queue
@app.route('/api/admin/emails', methods=['GET'])
def get_emails():
    \"\"\"Get all queued emails\"\"\"
    try:
        import email_queue
        emails = email_queue.get_queued_emails()
        return jsonify(emails)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/emails/<email_id>/sent', methods=['POST'])
def mark_email_sent(email_id):
    \"\"\"Mark email as sent\"\"\"
    try:
        import email_queue
        email_queue.mark_email_sent(email_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/emails/clear', methods=['POST'])
def clear_email_queue():
    \"\"\"Clear email queue\"\"\"
    try:
        import shutil
        queue_dir = os.path.join('projects', 'Cauchemar', 'data', 'email_queue')
        if os.path.exists(queue_dir):
            shutil.rmtree(queue_dir)
            os.makedirs(queue_dir)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

"""
    
    lines.insert(insert_index, admin_apis)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Added admin API endpoints to app.py")
else:
    print("❌ Could not find insert location")
