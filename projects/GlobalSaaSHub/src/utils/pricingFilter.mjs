// Filter only the displayed price; never invent a price for missing evidence.
export function matchesPricingFilter(pricing, selectedPricing) {
  const text = typeof pricing === 'string' ? pricing : '';
  const lower = text.toLowerCase();
  const match = text.match(/\$([\d,]+(?:\.\d+)?)/);
  const amount = match ? Number(match[1].replaceAll(',', '')) : null;
  if (selectedPricing === 'free') return lower.includes('free') || lower.includes('trial');
  if (selectedPricing === 'under20') return (amount !== null && amount < 20) || lower.includes('free');
  if (selectedPricing === 'under50') return amount !== null && amount >= 20 && amount <= 50;
  if (selectedPricing === 'over50') return amount !== null && amount > 50;
  return true;
}
