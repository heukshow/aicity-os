# Admin API endpoints for email queue management
import os
import json
from flask import Flask, jsonify

# Add these endpoints to app.py after the inquiry endpoint

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
    """Mark an email as sent"""
    try:
        import email_queue
        email_queue.mark_email_sent(email_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/emails/clear', methods=['POST'])
def clear_email_queue():
    """Clear all emails from queue"""
    try:
        import shutil
        queue_dir = os.path.join('projects', 'Cauchemar', 'data', 'email_queue')
        if os.path.exists(queue_dir):
            shutil.rmtree(queue_dir)
            os.makedirs(queue_dir)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
