"""Run every fastlane against progressed fixtures in an isolated project copy."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from affiliate_lifecycle_guard import protected, rank, rows

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp) / 'project'
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('node_modules', 'dist', '.git', '__pycache__'))
    # Synthetic future fixtures never leave this temporary directory.
    for name in ['tools.json', 'tools.next.json']:
        path = root / 'data' / name
        data = json.loads(path.read_text())
        for row in data:
            if rank(row) == 0:
                row.update(affiliate_status='approved', application_state='approved', affiliate_url=None,
                           affiliate_status_checked_at='2099-01-01T00:00:00Z')
        path.write_text(json.dumps(data))
    count = 0
    for script in sorted((root / 'scripts').glob('ensure_*_fastlane.mjs')):
        before = {name: json.loads((root / 'data' / name).read_text()) for name in ['tools.json', 'tools.next.json']}
        result = subprocess.run(['node', str(script)], cwd=root, text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(f'{script.name}: {result.stderr}')
        for name, data in before.items():
            after = rows(json.loads((root / 'data' / name).read_text()), name)
            for key, old in rows(data, name).items():
                if rank(old) == 0:
                    continue
                for field in ['affiliate_status', 'application_state', 'affiliate_url']:
                    if after[key].get(field) != old.get(field):
                        raise AssertionError(f'{script.name}: {name}/{key}/{field} regressed')
        count += 1
    print(f'PASS all {count} fastlane producers preserve progressed states and exact URLs')
