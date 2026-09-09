import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const toolDir = path.join(root, 'public', 'tool');

const genericFree = 'Check current free-plan availability on the vendor pricing page; COSHUMA does not infer that no free plan exists from missing catalog data.';
const genericTrial = 'Check current trial availability and billing terms on the vendor page; COSHUMA does not infer that no trial exists from missing catalog data.';
const genericRisk = 'Features, limits and prices can change. Verify the final plan and checkout terms on the vendor site.';

const compactAccess = (freePlan, trial, risk) => {
  const freeIsGeneric = freePlan.trim() === genericFree;
  const trialIsGeneric = trial.trim() === genericTrial;
  const riskIsGeneric = risk.trim() === genericRisk;

  if (freeIsGeneric && trialIsGeneric) {
    return '<div><h3 class="font-bold">Free access & trial</h3><p>Free-plan and trial availability are not confirmed here. Check the current vendor pricing page for eligibility, limits and billing terms before checkout.</p></div>';
  }

  const parts = [];
  if (freeIsGeneric) {
    parts.push('<strong>Free plan:</strong> Check the current vendor pricing page for availability and limits.');
  } else {
    parts.push(`<strong>Free plan:</strong> ${freePlan.trim()}`);
  }

  if (trialIsGeneric) {
    parts.push('<strong>Free trial:</strong> Check the current vendor page for availability and billing terms.');
  } else {
    parts.push(`<strong>Free trial:</strong> ${trial.trim()}`);
  }

  let html = `<div><h3 class="font-bold">Free access & trial</h3><p>${parts.join(' ')}</p></div>`;
  if (!riskIsGeneric && risk.trim()) {
    html += `\n<p><strong>Before you buy:</strong> ${risk.trim()}</p>`;
  } else {
    html += '\n<p>Verify current vendor terms before checkout.</p>';
  }
  return html;
};

let changed = 0;
let scanned = 0;

for (const file of fs.readdirSync(toolDir).filter((name) => name.endsWith('.html'))) {
  const filePath = path.join(toolDir, file);
  let html = fs.readFileSync(filePath, 'utf8');
  if (!html.includes('<!-- buyer-box:start -->')) continue;
  scanned += 1;

  const next = html.replace(
    /<dl><dt class="font-bold">Free plan<\/dt><dd>([\s\S]*?)<\/dd><dt class="font-bold">Free trial<\/dt><dd>([\s\S]*?)<\/dd><\/dl>\s*<p>([\s\S]*?)<\/p>/,
    (_match, freePlan, trial, risk) => compactAccess(freePlan, trial, risk),
  );

  if (next !== html) {
    fs.writeFileSync(filePath, next);
    changed += 1;
  }
}

console.log(`polish_buyer_decision_copy: scanned=${scanned} changed=${changed}`);
