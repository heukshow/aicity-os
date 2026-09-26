// Only explicitly named program evidence enters the per-program inventory.
// Account-wide balances and failed authentication attempts are not program truth.
export function programObservations(observations, tools) {
  const normalized = value => String(value || '').trim().toLowerCase();
  return (observations.accounts || []).flatMap(account => (account.evidence || []).flatMap(record => {
    const tool = tools.find(tool => record.tool_id === tool.id || normalized(record.tool) === normalized(tool.name));
    if (!tool || !record.evidence_id || !record.source || !Number.isFinite(Date.parse(record.checked_at))) return [];
    const metrics = record.metrics || {};
    if (!Object.values(metrics).some(Number.isFinite)) return [];
    if (Object.values(metrics).some(value => value !== null && (!Number.isFinite(value) || value < 0))) {
      throw new Error(`Invalid program observation: ${tool.id}`);
    }
    return [{ tool_id: tool.id, tool: tool.name, network: record.network || null,
      period: record.period || null, checked_at: record.checked_at, source: record.source,
      evidence_id: record.evidence_id, currency: record.currency || null, metrics }];
  }));
}

export function mergeProgramObservations(existing, observations) {
  const result = structuredClone(existing);
  for (const observation of observations) {
    const same = result.find(row => row.tool_id === observation.tool_id && row.evidence_id === observation.evidence_id && row.checked_at === observation.checked_at);
    if (!same) { result.push(observation); continue; }
    // Enrich only the exact same evidence, never a different reporting period.
    for (const [key, value] of Object.entries(observation.metrics)) {
      if (Number.isFinite(same.metrics[key]) && Number.isFinite(value) && same.metrics[key] !== value) {
        throw new Error(`Conflicting same-evidence metric: ${observation.tool_id}/${key}`);
      }
      if (Number.isFinite(value) || same.metrics[key] === undefined) same.metrics[key] = value;
    }
  }
  return result;
}
