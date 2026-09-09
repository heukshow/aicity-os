import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = path.resolve(SCRIPT_DIR, '..');
const TOOLS_PATH = path.join(PROJECT_DIR, 'data', 'tools.json');
const TOOL_DIR = path.join(PROJECT_DIR, 'public', 'tool');

const tools = JSON.parse(fs.readFileSync(TOOLS_PATH, 'utf8'));
const byId = new Map(tools.filter(tool => tool?.id && tool?.official_url).map(tool => [tool.id, tool]));

const phraseAnchor = /(Prefer a non-affiliate path\?\s*)(<a\b[^>]*>)/gi;
let filesChanged = 0;
let anchorsRestored = 0;

function restoreOfficialAnchor(anchor, officialUrl) {
  let restored = anchor
    .replace(/\sdata-cta="affiliate"/gi, '')
    .replace(/\sdata-tool-id="[^"]*"/gi, '')
    .replace(/\sdata-cta-source="[^"]*"/gi, '')
    .replace(/\shref="[^"]*"/i, ` href="${officialUrl}"`)
    .replace(/\srel="[^"]*"/i, ' rel="noopener noreferrer"');

  if (!/\sdata-cta=/i.test(restored)) {
    restored = restored.replace('<a ', '<a data-cta="official" data-cta-source="non-affiliate-path" ');
  }
  if (!/\starget=/i.test(restored)) {
    restored = restored.replace('<a ', '<a target="_blank" ');
  }
  if (!/\srel=/i.test(restored)) {
    restored = restored.replace('<a ', '<a rel="noopener noreferrer" ');
  }
  return restored;
}

for (const filename of fs.readdirSync(TOOL_DIR).filter(name => name.endsWith('.html'))) {
  const toolId = filename.slice(0, -5);
  const tool = byId.get(toolId);
  if (!tool) continue;

  const file = path.join(TOOL_DIR, filename);
  const original = fs.readFileSync(file, 'utf8');
  if (!original.includes('Prefer a non-affiliate path?')) continue;

  let restoredInFile = 0;
  const updated = original.replace(phraseAnchor, (match, prefix, anchor) => {
    const restored = restoreOfficialAnchor(anchor, tool.official_url);
    if (restored !== anchor) restoredInFile += 1;
    return prefix + restored;
  });

  const validation = updated.match(/Prefer a non-affiliate path\?\s*(<a\b[^>]*>)/i)?.[1];
  if (!validation || !validation.includes(`href="${tool.official_url}"`) || /data-cta="affiliate"/i.test(validation) || /data-tool-id=/i.test(validation)) {
    throw new Error(`Non-affiliate path validation failed for ${toolId}`);
  }

  if (updated !== original) {
    fs.writeFileSync(file, updated, 'utf8');
    filesChanged += 1;
    anchorsRestored += restoredInFile;
  }
}

console.log(`preserve_non_affiliate_paths: files_changed=${filesChanged} anchors_restored=${anchorsRestored}`);
