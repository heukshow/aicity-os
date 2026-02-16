import os
import json
import hashlib
import secrets
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

# Initialize Flask App
app = Flask(__name__, static_folder='projects/Cauchemar')
CORS(app)  # Enable CORS for all routes

# Configuration
DATA_DIR = os.path.join('projects', 'Cauchemar', 'data')
CREW_FILE = os.path.join(DATA_DIR, 'crew.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
UPLOAD_DIR = os.path.join('projects', 'Cauchemar', 'uploads')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Helper Functions
def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    # Using SHA256 as inferred from existing hashes
    hash_obj = hashlib.sha256((salt + password).encode('utf-8'))
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(stored_password, provided_password):
    try:
        salt, hash_val = stored_password.split('$')
        computed_hash = hashlib.sha256((salt + provided_password).encode('utf-8')).hexdigest()
        return hash_val == computed_hash
    except ValueError:
        # Fallback for plain text passwords (development/legacy)
        return stored_password == provided_password

# --- Routes ---

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'cauchemar.html')

# Handle /projects/Cauchemar/ prefix (from HTML links)
@app.route('/projects/Cauchemar/<path:path>')
def serve_cauchemar_files(path):
    return send_from_directory(app.static_folder, path)

# Handle /projects/HyperNovaAI/ prefix
@app.route('/projects/HyperNovaAI/')
@app.route('/projects/HyperNovaAI/index.html')
def serve_hypernova_index():
    return send_from_directory('projects/HyperNovaAI', 'index.html')

@app.route('/projects/HyperNovaAI/<path:path>')
def serve_hypernova_files(path):
    return send_from_directory('projects/HyperNovaAI', path)

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# --- API Endpoints ---

@app.route('/api/crew/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({'message': 'ID and password required'}), 400

    # Check Crew (crew.json)
    crew_list = load_json(CREW_FILE)
    user = next((u for u in crew_list if u['id'] == user_id), None)
    user_type = 'crew'

    # Check Users (users.json) if not in crew
    if not user:
        users_list = load_json(USERS_FILE)
        user = next((u for u in users_list if u.get('name') == user_id or u.get('email') == user_id), None) # Login with name or email (users.json structure varies, assuming name/id usage)
        # Standardize ID checking for users.json which uses 'name' as ID often
        if not user:
             user = next((u for u in users_list if u.get('id') == user_id), None)
        
        if user:
             user_type = 'user'

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Verify Password
    if verify_password(user.get('password', ''), password):
        # Generate a simple token (in production use JWT)
        token = secrets.token_hex(32)
        
        # Return user info (sanitize password)
        user_info = user.copy()
        if 'password' in user_info:
            del user_info['password']
        
        return jsonify({
            'status': 'ok',
            'token': token,
            'member': user_info,
            'type': user_type
        })
    else:
        return jsonify({'message': 'Invalid password'}), 401

@app.route('/api/crew/register', methods=['POST'])
def register():
    data = request.json
    new_id = data.get('id')
    password = data.get('password')
    
    if not new_id or not password:
         return jsonify({'message': 'Missing fields'}), 400

    # Load existing data
    crew_list = load_json(CREW_FILE)
    users_list = load_json(USERS_FILE)

    # Check duplicates
    if any(u['id'] == new_id for u in crew_list) or any(u.get('name') == new_id for u in users_list):
        return jsonify({'message': 'User ID already exists'}), 409

    # Create new user object
    new_user = {
        "id": new_id, # users.json might use 'name' but we standardize on ID for internal logic if possible, or mapping
        "name": data.get('name', new_id),
        "password": hash_password(password),
        "role": data.get('role', 'New Creator'),  # Use selected creator type or default
        "type": "creator" if "crew" in request.referrer or "register_crew" in request.referrer else "user", # Simple logic to distinguish
        "official": False,
        "description": "안녕하세요! 신규 가입한 크리에이터입니다.",
        "zepeto_id": data.get('zepeto_id', ''),
        "agreed_to_terms": data.get('agree_terms', False),
        "prices": {},
        "portfolio": [],
        "joined_at": datetime.now().isoformat()
    }
    
    # Save to crew.json for now as it seems to be the main focus
    # Or users.json? The prompt implies restoring for "Cauchemar crew website".
    # register_crew.html sends here. Let's save to crew.json if it looks like a crew registration.
    
    if "register_crew" in request.referrer or new_user['type'] == 'creator':
         crew_list.append(new_user)
         if save_json(CREW_FILE, crew_list):
             return jsonify({'status': 'ok', 'message': 'Account created'})
    else:
         users_list.append(new_user)
         if save_json(USERS_FILE, users_list):
             return jsonify({'status': 'ok', 'message': 'Account created'})

    return jsonify({'message': 'Failed to save data'}), 500

@app.route('/api/crew/update', methods=['POST'])
def update_crew():
    # Simple token check (mock)
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.json
    target_id = data.get('id')

    if not target_id:
        return jsonify({'message': 'Target ID required'}), 400

    crew_list = load_json(CREW_FILE)
    user_idx = next((i for i, u in enumerate(crew_list) if u['id'] == target_id), -1)

    if user_idx != -1:
        # Update fields
        user = crew_list[user_idx]
        if 'name' in data: user['name'] = data['name']
        if 'role' in data: user['role'] = data['role']
        if 'description' in data: user['description'] = data['description']
        if 'zepeto_id' in data: user['zepeto_id'] = data['zepeto_id']
        if 'prices' in data: user['prices'] = data['prices']
        if 'agreed_to_terms' in data: user['agreed_to_terms'] = data['agreed_to_terms']
        
        # Mock Zepeto Refresh
        if data.get('refresh_zepeto'):
             # In a real app, scrape Zepeto or use API. Here we just pretend.
             if not user.get('followers'):
                 user['followers'] = "1.2K" # Mock data
        
        crew_list[user_idx] = user
        save_json(CREW_FILE, crew_list)
        return jsonify({'status': 'ok', 'message': 'Updated'})

    return jsonify({'message': 'User not found'}), 404

@app.route('/api/inquiry/submit', methods=['POST'])
def submit_inquiry():
    try:
        # Get form data
        client_name = request.form.get('client_name')
        client_email = request.form.get('client_email')
        project_type = request.form.get('project_type')
        budget = request.form.get('budget')
        deadline = request.form.get('deadline')
        description = request.form.get('description')
        preferred_creator = request.form.get('preferred_creator')
        language = request.form.get('language', 'ko')
        
        # Validate required fields
        if not all([client_name, client_email, project_type, budget, description]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Generate unique inquiry ID
        inquiry_id = secrets.token_hex(8)
        timestamp = datetime.now().isoformat()
        
        # Handle file uploads
        uploaded_files = []
        if 'references' in request.files:
            files = request.files.getlist('references')
            for file in files[:5]:  # Max 5 files
                if file and file.filename:
                    # Sanitize filename
                    filename = f"{inquiry_id}_{len(uploaded_files)}_{file.filename}"
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    file.save(filepath)
                    uploaded_files.append(filename)
        
        # Create inquiry object
        inquiry = {
            'id': inquiry_id,
            'timestamp': timestamp,
            'client': {
                'name': client_name,
                'email': client_email,
                'language': language
            },
            'project': {
                'type': project_type,
                'budget': budget,
                'deadline': deadline,
                'description': description,
                'preferred_creator': preferred_creator,
                'reference_files': uploaded_files
            },
            'status': 'pending',  # pending, ai_analyzed, responded, in_progress, completed
            'ai_analysis': None,  # Will be filled by AI
            'email_sent': False
        }
        
        # Load existing inquiries
        INQUIRIES_FILE = os.path.join(DATA_DIR, 'inquiries.json')
        inquiries = load_json(INQUIRIES_FILE)
        inquiries.append(inquiry)
        
        # Save inquiries
        if not save_json(INQUIRIES_FILE, inquiries):
            return jsonify({'success': False, 'error': 'Failed to save inquiry'}), 500
        
        # AI Analysis and Email Automation
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
            print(f"[AI] Non-critical error: {e}")
        
        print(f"[INQUIRY] New inquiry from {client_name} ({client_email}) - ID: {inquiry_id}")
        
        return jsonify({
            'success': True,
            'inquiry_id': inquiry_id,
            'message': 'Inquiry submitted successfully'
        })
        
    except Exception as e:
        print(f"Error processing inquiry: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Admin API Endpoints for Email Queue
@app.route('/api/admin/emails', methods=['GET'])
def get_emails():
    """Get all queued emails"""
    try:
        import email_queue
        emails = email_queue.get_queued_emails()
        return jsonify(emails)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/emails/<email_id>/sent', methods=['POST'])
def mark_email_sent(email_id):
    """Mark email as sent"""
    try:
        import email_queue
        email_queue.mark_email_sent(email_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/emails/clear', methods=['POST'])
def clear_email_queue():
    """Clear email queue"""
    try:
        import shutil
        queue_dir = os.path.join('projects', 'Cauchemar', 'data', 'email_queue')
        if os.path.exists(queue_dir):
            shutil.rmtree(queue_dir)
            os.makedirs(queue_dir)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Cauchemar Server on port 8000...")
    app.run(host='0.0.0.0', port=8000, debug=True)
