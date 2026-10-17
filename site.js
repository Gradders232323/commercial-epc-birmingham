(() => {
  const header = document.querySelector('.header');
  const menu = document.querySelector('.menu');
  menu?.addEventListener('click', () => {
    const open = header.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
  });

  // Keep campaign attribution through an internal page visit. Never store form details.
  const keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'gbraid', 'wbraid'];
  const storageKey = 'birmingham-quote-attribution-v1';
  const currentUrl = new URL(window.location.href);
  let saved = {};
  try { saved = JSON.parse(window.sessionStorage.getItem(storageKey) || '{}'); } catch { /* Storage can be disabled. */ }
  if (!saved || typeof saved !== 'object' || Array.isArray(saved)) saved = {};
  const attribution = {};
  for (const key of keys) {
    const value = currentUrl.searchParams.get(key) ?? saved[key];
    if (typeof value === 'string' && value.trim() && value.length <= 500) attribution[key] = value;
  }
  try { window.sessionStorage.setItem(storageKey, JSON.stringify(attribution)); } catch { /* The form still works without storage. */ }

  window.birminghamQuoteContext = () => {
    // Strip unknown query strings and fragments, which could contain personal information.
    const pageUrl = new URL(currentUrl.origin + currentUrl.pathname);
    for (const key of keys) if (attribution[key]) pageUrl.searchParams.set(key, attribution[key]);
    return { ...attribution, page_url: pageUrl.href };
  };
})();
