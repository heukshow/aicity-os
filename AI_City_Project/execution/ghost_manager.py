import os
import json
import secrets

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GHOST_DATA = os.path.join(PROJECT_ROOT, 'directives', 'ghost_identities.json')

class GhostManager:
    """Manages anonymous 'Ghost Identities' for external-facing projects."""
    
    def __init__(self):
        self.identities = self._load_identities()

    def _load_identities(self):
        if os.path.exists(GHOST_DATA):
            with open(GHOST_DATA, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"active_ghosts": []}

    def _save_identities(self):
        with open(GHOST_DATA, 'w', encoding='utf-8') as f:
            json.dump(self.identities, f, indent=2)

    def generate_ghost(self, project_name):
        """Creates a new anonymous identity for a specific project."""
        # Check if already exists
        existing = next((g for g in self.identities["active_ghosts"] if g["project"] == project_name), None)
        if existing:
            return existing

        # Generate new credentials
        ghost_id = secrets.token_hex(4).upper()
        new_ghost = {
            "project": project_name,
            "alias": f"Agent_{ghost_id}",
            "official_title": "Coshuma Project Liaison",
            "email_alias": f"liaison.{ghost_id}@coshuma.ai", # Simulated domain
            "verification_code": secrets.token_urlsafe(16),
            "created_at": str(os.path.getmtime(GHOST_DATA)) if os.path.exists(GHOST_DATA) else "just_now"
        }
        
        self.identities["active_ghosts"].append(new_ghost)
        self._save_identities()
        print(f"👻 [Ghost] Generated new identity for {project_name}: {new_ghost['alias']}")
        return new_ghost

if __name__ == "__main__":
    manager = GhostManager()
    manager.generate_ghost("Instagram_Marketing_A")
    manager.generate_ghost("Global_YouTube_Factory")
