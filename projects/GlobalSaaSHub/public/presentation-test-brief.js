(() => {
  'use strict';
  const scenario = document.getElementById('presentation-scenario');
  const brief = document.getElementById('presentation-brief');
  const copy = document.getElementById('copy-presentation-brief');
  const status = document.getElementById('presentation-copy-status');
  if (!scenario || !brief || !copy || !status) return;

  const common = '\nUse short headings and one main point per slide. Keep numbers traceable to my notes. Mark missing facts as [NEEDS INPUT]; do not invent customers, results, prices, or testimonials.\nSuggest a useful visual for each slide. Keep the deck readable on a laptop and phone.\nSource notes: [PASTE YOUR PUBLIC OR SAMPLE NOTES HERE]';
  const briefs = {
    pitch: brief.value,
    lesson: 'Create an 8-slide introductory lesson from the source notes I provide.\nAudience: a beginner learning this topic.\nSlides: 1. Learning objective; 2. Why it matters; 3. Core concept; 4. Worked example; 5. Common mistake; 6. Practice task; 7. Answer and explanation; 8. Recap and next step.' + common,
    report: 'Create an 8-slide monthly business update from the source notes I provide.\nAudience: a team lead deciding what to do next.\nSlides: 1. Executive summary; 2. Goals; 3. Actual results; 4. Comparison with the previous period; 5. What changed; 6. Risks and unknowns; 7. Proposed actions; 8. Decisions needed.\nUse only the supplied data. If a prior-period value is missing, say it is unavailable rather than calculating a change.' + common,
  };
  scenario.addEventListener('change', () => {
    brief.value = briefs[scenario.value] || briefs.pitch;
    status.textContent = '';
  });
  copy.hidden = false;
  copy.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(brief.value);
      status.textContent = 'Copied. Paste the brief into your chosen tool and add your source notes there.';
    } catch {
      brief.focus();
      brief.select();
      status.textContent = 'The brief is selected. Use your device’s Copy command.';
    }
  });
})();
