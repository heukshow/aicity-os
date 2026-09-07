# COSHUMA YouTube Shorts automation

## Goal

Turn revenue-priority COSHUMA pages (`/best/`, `/compare/`, `/tool/`) into Shorts that send tracked buyer-intent traffic back to COSHUMA. The KPI is downstream traffic and affiliate clicks, not raw views.

## Current pipeline

## Fixed COSHUMA presenter duo

Every new COSHUMA SaaS video must load these repository assets before any character generation:

- `assets/characters/COSHUMA_MALE_MASTER.png`
- `assets/characters/COSHUMA_FEMALE_MASTER.png`
- `assets/characters/COSHUMA_DUO_REFERENCE.png`

The male and female identities are permanent. Clothing, pose and background may change, but face shape, hairstyle, late-20s age range, skin tone and overall impression must remain consistent. Do not generate replacement faces. If either individual master is absent, unreadable or fails its recorded SHA-256 check, stop only that video and record `character_reference_missing`.

The default episode format is 9:16 and 30-45 seconds: a strong first-two-second hook, alternating dialogue between the two presenters, real tool UI, one presenter operating while the other guides the next action, and a natural CTA. Emphasize verified workflow efficiency, time savings, automation and business opportunity without invented revenue claims.

| Stage | Status | Implementation |
|---|---|---|
| Revenue-priority selection | Done | `scripts/youtube_shorts/select_content.py` |
| Topic/hook generation | Partial | deterministic templates in `prepare_next_short.py` |
| Script generation | Not implemented | follow-up work |
| Video rendering | Partial | existing published Shorts prove the format, but repo automation is not yet implemented |
| Quality gate | Done | `scripts/youtube_shorts/quality_gate.py` |
| Metadata + UTM | Done | `scripts/youtube_shorts/generate_metadata.py` |
| Manifest / duplicate prevention | Done | `data/youtube_shorts_manifest.json` |
| YouTube API upload | Not implemented in repository code | no `videos.insert` integration is currently present |
| Scheduled publishing | Not enabled | workflow remains manual until end-to-end upload is verified |
| GA4 landing attribution | Done | existing `affiliate-attribution.js` reads `utm_source`, `utm_medium`, `utm_campaign` |

## Authentication evidence rule

Repository code currently contains no YouTube OAuth upload integration. GitHub Actions secret values are not readable through the current integration, so the existence or absence of `YOUTUBE_*` secrets must be reported as **unverified** unless checked in an authenticated environment that can inspect repository secrets.

## Duplicate prevention

`select_content.py` skips a `(affiliate_target, campaign_slug)` already present in the manifest with `rendered`, `ready`, or `uploaded` status. A deliberate second creative for the same tool must use a distinct campaign/content slug.

## Files

- `data/youtube_shorts_manifest.json` — source page, affiliate target, campaign, COSHUMA URL, YouTube video ID, hashes and status.
- `scripts/youtube_shorts/select_content.py` — revenue-priority ranking.
- `scripts/youtube_shorts/generate_metadata.py` — title, description, hashtags and UTM URL.
- `scripts/youtube_shorts/quality_gate.py` — pre-upload validation.
- `scripts/youtube_shorts/prepare_next_short.py` — prepares the next candidate and render/upload queue task.
- `scripts/tests/test_youtube_shorts_pipeline.py` — isolated pipeline tests.
- `.github/workflows/coshuma-youtube-shorts.yml` — manual workflow for selection/queueing until rendering/upload are fully automated.

## Next milestone

Implement free deterministic script generation and ffmpeg rendering, then add a YouTube Data API upload module that reads OAuth credentials only from environment variables. Keep automatic scheduling disabled until a real end-to-end upload has been verified and the resulting video ID is written back to the manifest.
