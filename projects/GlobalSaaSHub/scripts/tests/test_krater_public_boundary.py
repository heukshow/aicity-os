from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts" / "generate_seo_pages.py"
POLISH = ROOT / "scripts" / "polish_public_copy.py"
RAW_GUARD = ROOT / "scripts" / "guard_raw_public_source.py"
DIST_GUARD = ROOT / "scripts" / "guard_public_artifact_boundary.py"
POLICY = ROOT / "config" / "public_content_policy.json"

BANNED = (
    "Founder Verification",
    "Claim this official profile",
    "Profile ($49/yr)",
    "Official Embed Badge Code",
    "verified-badge.svg",
)


def _load_polish_module():
    spec = importlib.util.spec_from_file_location("polish_public_copy", POLISH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_programmatic_tool_generator_no_longer_owns_listing_admin_ui():
    source = GENERATOR.read_text(encoding="utf-8")
    for phrase in BANNED:
        assert phrase not in source


def test_legacy_listing_admin_block_is_removed_not_reworded():
    polish = _load_polish_module()
    legacy = '''
    <main><div>
      <!-- Claim Profile & Official Founder Badge Section -->
      <div class="p-6 rounded-2xl bg-[#181a29]/80 border border-purple-500/30 space-y-4">
        <span>Founder Verification</span>
        <p>Claim this official profile to update tool information, manage pricing details, and embed the verified rating badge on your website:</p>
        <a href="/#submit">Claim Krater Profile ($49/yr)</a>
        <div><div>Official Embed Badge Code:</div><textarea>verified-badge.svg</textarea></div>
      </div>
    </div></main>
    '''
    cleaned = polish.polish(legacy)
    for phrase in BANNED:
        assert phrase not in cleaned
    assert "<main><div>" in cleaned
    assert "</div></main>" in cleaned


def test_source_and_final_guards_cover_listing_admin_regression():
    raw = RAW_GUARD.read_text(encoding="utf-8")
    dist = DIST_GUARD.read_text(encoding="utf-8")
    policy = POLICY.read_text(encoding="utf-8")
    assert "LISTING_ADMIN" in raw
    assert "LISTING_ADMIN" in dist
    assert "Founder Verification" in policy
    assert "Claim Profile ($49/yr)" in policy
    assert "Official Embed Badge Code" in policy
