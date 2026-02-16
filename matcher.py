"""
Crew-Project Matcher Module
Matches client inquiries with suitable crew members based on skills and availability.
"""

import json
import os
from typing import List, Dict, Optional

DATA_DIR = os.path.join('projects', 'Cauchemar', 'data')
CREW_FILE = os.path.join(DATA_DIR, 'crew.json')

# Skill mapping from inquiry project types to crew skills
SKILL_MAPPING = {
    'item_hair': ['헤어', 'hair'],
    'item_top': ['상의', 'top'],
    'item_bottom': ['하의', 'bottom'],
    'item_shoes': ['신발', 'shoes'],
    'item_other': ['액세서리', '기타', 'other'],
    'promo_sns': ['SNS홍보', 'promotion'],
    'promo_video': ['영상제작', 'video'],
    'other': []  # Any crew can handle "other"
}

def load_crew() -> List[Dict]:
    """Load crew data from crew.json"""
    try:
        with open(CREW_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading crew data: {e}")
        return []

def match_crew_to_project(inquiry: Dict) -> List[Dict]:
    """
    Match crew members to a project inquiry.
    
    Args:
        inquiry: Dict containing project details (type, budget, etc.)
    
    Returns:
        List of matched crew members, ranked by suitability
    """
    project_type = inquiry.get('project', {}).get('type', '')
    preferred_creator = inquiry.get('project', {}).get('preferred_creator', '')
    
    crew_list = load_crew()
    matched_crew = []
    
    # Get required skills for this project type
    required_skills = SKILL_MAPPING.get(project_type, [])
    
    for member in crew_list:
        # Skip if no email (can't contact them)
        if not member.get('email'):
            continue
        
        # Check if preferred creator specified
        if preferred_creator and member.get('id') == preferred_creator:
            matched_crew.insert(0, {
                'member': member,
                'score': 100,  # Highest priority
                'reason': 'Client preference'
            })
            continue
        
        # Calculate match score
        score = calculate_match_score(member, required_skills, inquiry)
        
        if score > 0:
            matched_crew.append({
                'member': member,
                'score': score,
                'reason': get_match_reason(member, required_skills)
            })
    
    # Sort by score (highest first)
    matched_crew.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top 3 candidates
    return matched_crew[:3]

def calculate_match_score(member: Dict, required_skills: List[str], inquiry: Dict) -> int:
    """
    Calculate how well a crew member matches the project requirements.
    
    Returns:
        Score from 0-100
    """
    score = 0
    
    # Base score for being available
    score += 20
    
    # Skill match (40 points)
    member_skills = member.get('skills', [])
    if not member_skills:
        # If no skills listed, check prices as fallback
        member_prices = member.get('prices', {})
        for price_cat in member_prices.keys():
            for skill in required_skills:
                if skill.lower() in price_cat.lower():
                    score += 40
                    break
    else:
        for skill in required_skills:
            if any(skill.lower() in ms.lower() for ms in member_skills):
                score += 40
                break
    
    # Official status bonus (20 points)
    if member.get('official'):
        score += 20
    
    # Experience/portfolio bonus (10 points)
    if member.get('portfolio') and len(member.get('portfolio', [])) > 0:
        score += 10
    
    # Workload penalty
    current_workload = member.get('current_workload', 0)
    if current_workload > 3:
        score -= 20  # Too busy
    
    return max(0, min(100, score))

def get_match_reason(member: Dict, required_skills: List[str]) -> str:
    """Generate a human-readable reason for the match"""
    reasons = []
    
    if member.get('official'):
        reasons.append("Official Creator")
    
    member_skills = member.get('skills', [])
    matched_skills = [s for s in required_skills if any(s.lower() in ms.lower() for ms in member_skills)]
    if matched_skills:
        reasons.append(f"Specializes in {', '.join(matched_skills)}")
    
    if member.get('portfolio') and len(member.get('portfolio', [])) > 0:
        reasons.append("Experienced portfolio")
    
    return " | ".join(reasons) if reasons else "Available creator"

def get_crew_contact_info(crew_id: str) -> Optional[Dict]:
    """Get contact information for a specific crew member"""
    crew_list = load_crew()
    for member in crew_list:
        if member.get('id') == crew_id:
            return {
                'id': member.get('id'),
                'name': member.get('name'),
                'email': member.get('email'),
                'role': member.get('role')
            }
    return None

if __name__ == '__main__':
    # Test matching
    test_inquiry = {
        'project': {
            'type': 'item_hair',
            'budget': '100k_200k',
            'description': 'Need hair item for collaboration'
        }
    }
    
    matches = match_crew_to_project(test_inquiry)
    print(f"Found {len(matches)} matching crew members:")
    for match in matches:
        print(f"  - {match['member']['name']} (Score: {match['score']}) - {match['reason']}")
