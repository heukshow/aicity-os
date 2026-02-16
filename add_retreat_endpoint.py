# Backend for retreat info form

from flask import request, jsonify
import json
import os
from datetime import datetime

# Add this to app.py

@app.route('/api/retreat_info', methods=['POST'])
def save_retreat_info():
    try:
        data = request.get_json()
        
        # Save to file
        filepath = 'projects/retreat_cafe_info.json'
        
        # Add timestamp
        data['submitted_at'] = datetime.now().isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Retreat Cafe info saved to {filepath}")
        print(f"📋 Data: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        return jsonify({'success': True, 'message': '정보가 저장되었습니다!'})
    
    except Exception as e:
        print(f"❌ Error saving retreat info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
