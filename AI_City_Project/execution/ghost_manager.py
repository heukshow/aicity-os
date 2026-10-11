import json
import os
import secrets
import time

# Local simulation state must never be written beneath tracked source directories.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVATE_STATE_DIR = os.environ.get(
    "AI_CITY_PRIVATE_STATE_DIR",
    os.path.join(PROJECT_ROOT, ".private"),
)
GHOST_DATA = os.path.join(PRIVATE_STATE_DIR, "ghost_identities.json")


class GhostManager:
    """Manages local-only simulated aliases without authentication material."""

    def __init__(self):
        self.identities = self._load_identities()

    def _load_identities(self):
        if os.path.exists(GHOST_DATA):
            with open(GHOST_DATA, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"active_ghosts": []}

    def _save_identities(self):
        os.makedirs(PRIVATE_STATE_DIR, mode=0o700, exist_ok=True)
        with open(GHOST_DATA, "w", encoding="utf-8") as f:
            json.dump(self.identities, f, indent=2)
        try:
            os.chmod(GHOST_DATA, 0o600)
        except OSError:
            # Some platforms do not support POSIX permission bits.
            pass

    def generate_ghost(self, project_name):
        """Creates a non-authentic local simulation alias for a project."""
        existing = next(
            (g for g in self.identities["active_ghosts"] if g["project"] == project_name),
            None,
        )
        if existing:
            return existing

        ghost_id = secrets.token_hex(4).upper()
        new_ghost = {
            "project": project_name,
            "alias": f"Agent_{ghost_id}",
            "official_title": "Local simulation liaison",
            "contact": f"liaison.{ghost_id}@example.invalid",
            "simulated": True,
            "created_at": str(time.time()),
        }

        self.identities["active_ghosts"].append(new_ghost)
        self._save_identities()
        print(f"👻 [Ghost] Generated local simulation alias for {project_name}: {new_ghost['alias']}")
        return new_ghost


if __name__ == "__main__":
    manager = GhostManager()
    manager.generate_ghost("Instagram_Marketing_A")
    manager.generate_ghost("Global_YouTube_Factory")
