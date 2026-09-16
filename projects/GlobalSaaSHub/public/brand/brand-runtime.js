(() => {
  const MARK = '/brand/coshuma-mark.svg';
  const BRAND = '/brand/';

  function makeMark(sizeClass = '') {
    const img = document.createElement('img');
    img.src = MARK;
    img.alt = 'COSHUMA';
    img.className = `coshuma-brand-mark ${sizeClass}`.trim();
    img.style.width = '40px';
    img.style.height = '32px';
    img.style.objectFit = 'contain';
    img.style.flex = '0 0 auto';
    return img;
  }

  function textOf(node) {
    return (node?.textContent || '').replace(/\s+/g, ' ').trim();
  }

  function patchHomeBrand() {
    document.querySelectorAll('nav a[href="/"], header a[href="/"]').forEach((anchor) => {
      if (!/COSHUMA/i.test(anchor.textContent || '') || anchor.querySelector('.coshuma-brand-mark')) return;
      const first = anchor.firstElementChild;
      if (first && (first.querySelector('svg') || /^C$/i.test((first.textContent || '').trim()))) {
        first.replaceWith(makeMark());
      } else {
        anchor.prepend(makeMark());
      }
    });
  }

  function patchLegacyBadges() {
    document.querySelectorAll('a[href="/"] > div').forEach((node) => {
      if (!/^C$/i.test((node.textContent || '').trim())) return;
      if (!node.className || !String(node.className).includes('bg-purple')) return;
      node.replaceWith(makeMark());
    });
  }

  function isInternalOpsCopy(text) {
    if (!text) return false;
    const patterns = [
      /^Affiliate status:/i,
      /COSHUMA affiliate status/i,
      /COSHUMA CTA state/i,
      /PartnerStack application not submitted/i,
      /Waiting vendor response/i,
      /outreach thread pending/i,
      /COSHUMA (?:currently )?has not (?:submitted|verified|yet recovered|recovered|received)/i,
      /COSHUMA's? account .*?(?:pending|blocked|awaiting|upgrade|support)/i,
      /no verified (?:account[- ]specific |customer[- ]facing )?(?:referral|tracking) URL/i,
      /no .* customer referral URL .* verified/i,
      /Official non-affiliate link/i,
      /official non-affiliate (?:links|destinations)/i,
      /These buttons (?:intentionally )?remain official non-affiliate/i,
      /Tracking verification:/i,
      /exact customer-facing .* referral URL .* (?:issued|confirmed|dashboard)/i,
      /customer-facing destinations were supplied directly by the partner programs/i,
      /COSHUMA does not invent referral parameters/i,
      /uses only the exact .* (?:referral|invite) URL issued/i,
      /A click (?:does not imply|is never treated as) a (?:signup|sale)/i,
      /No clicks?, signups?, paid customers?, commissions? or revenue (?:are|is) inferred/i,
      /approval .* unknown/i,
      /application .* pending/i,
      /application .* declined/i,
      /application .* rejected/i,
      /application .* not submitted/i,
      /support resolving/i,
      /awaiting help for an upgrade/i,
      /upgrade-screen loop/i,
      /account-access evidence/i,
      /affiliate dashboard rather than a generic homepage/i,
      /Affiliate link verified in our records/i,
      /Use the exact tracked .* confirmed for COSHUMA/i,
      /partner-tagged .* approved for COSHUMA/i,
      /COSHUMA uses only the exact personal .* (?:referral|invite)/i,
      /COSHUMA (?:currently )?has a verified .* (?:route|referral|tracking)/i,
      /dashboard, onboarding page or generic homepage is never treated as an affiliate link/i
    ];
    return patterns.some((pattern) => pattern.test(text));
  }

  function sanitizeStructuredData() {
    document.querySelectorAll('script[type="application/ld+json"]').forEach((script) => {
      let data;
      try {
        data = JSON.parse(script.textContent || '');
      } catch {
        return;
      }

      const sanitizeNode = (node) => {
        if (!node || typeof node !== 'object') return;
        if (Array.isArray(node)) {
          node.forEach(sanitizeNode);
          return;
        }

        const type = node['@type'];
        const types = Array.isArray(type) ? type : [type];
        if (types.includes('FAQPage') && Array.isArray(node.mainEntity)) {
          node.mainEntity = node.mainEntity.filter((item) => {
            const question = textOf({ textContent: item?.name || '' });
            const answer = textOf({ textContent: item?.acceptedAnswer?.text || '' });
            const combined = `${question} ${answer}`.trim();
            if (/COSHUMA|affiliate link|referral link|tracking URL/i.test(question) && isInternalOpsCopy(combined)) return false;
            return !isInternalOpsCopy(combined);
          });
        }

        Object.values(node).forEach(sanitizeNode);
      };

      sanitizeNode(data);
      script.textContent = JSON.stringify(data);
    });
  }

  function removeOperationalCopy() {
    document.querySelectorAll('tr').forEach((row) => {
      const firstCell = row.querySelector('th, td');
      const label = textOf(firstCell);
      if (/^(?:COSHUMA\s+)?(?:affiliate status|CTA state)$/i.test(label)) row.remove();
    });

    document.querySelectorAll('p, li, small').forEach((node) => {
      const text = textOf(node);
      if (!isInternalOpsCopy(text)) return;
      if (/may earn .* commission/i.test(text) && !/non-affiliate|has not|not submitted|pending|declined|rejected/i.test(text)) return;
      node.remove();
    });

    document.querySelectorAll('div').forEach((node) => {
      if (node.children.length) return;
      const text = textOf(node);
      if (!isInternalOpsCopy(text)) return;
      node.remove();
    });

    document.querySelectorAll('section').forEach((section) => {
      const heading = section.querySelector(':scope > h1, :scope > h2, :scope > h3');
      const headingText = textOf(heading);
      const sectionText = textOf(section);

      if (/^How this list is gated$/i.test(headingText)) {
        section.remove();
        return;
      }

      if (/^Affiliate disclosure$/i.test(headingText)) {
        const operationalOnly = /has not verified|official non-affiliate|application not submitted|waiting vendor response|no verified customer referral URL/i.test(sectionText);
        const realDisclosure = /may earn .* commission|affiliate commission|at no extra cost/i.test(sectionText);
        if (operationalOnly && !realDisclosure) {
          section.remove();
          return;
        }
      }

      const remaining = Array.from(section.children).filter((child) => !/^H[1-3]$/.test(child.tagName));
      if (heading && remaining.length === 0) section.remove();
    });

    document.querySelectorAll(`footer a[href="${BRAND}"]`).forEach((link) => link.remove());
  }

  function patchAll() {
    patchHomeBrand();
    patchLegacyBadges();
    sanitizeStructuredData();
    removeOperationalCopy();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', patchAll, { once: true });
  } else {
    patchAll();
  }

  let passes = 0;
  const observer = new MutationObserver(() => {
    patchAll();
    passes += 1;
    if (passes > 30) observer.disconnect();
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });
})();
