(() => {
  const frame = document.getElementById('birmingham-quote-frame');
  if (!frame) return;
  const formOrigin = 'https://gradwell-inspection-booking.info512176.chatgpt.site';
  const prefix = 'birmingham:service-quote:';
  let submitted = false;

  function sendContext() {
    frame.contentWindow?.postMessage({
      type: prefix + 'context',
      attribution: window.birminghamQuoteContext?.() || {},
    }, formOrigin);
  }

  frame.addEventListener('load', sendContext);
  window.addEventListener('message', (event) => {
    // Trust only this frame, on the exact hosted form origin. Never a wildcard.
    if (!frame.contentWindow || event.origin !== formOrigin || event.source !== frame.contentWindow) return;
    const data = event.data;
    if (!data || typeof data !== 'object' || Array.isArray(data)) return;

    if (data.type === prefix + 'ready') {
      document.getElementById('booking-loading')?.setAttribute('hidden', '');
      sendContext();
    } else if (data.type === prefix + 'resize') {
      if (typeof data.height === 'number' && Number.isFinite(data.height) && data.height >= 480 && data.height <= 6000) {
        frame.style.height = `${Math.ceil(data.height)}px`;
      }
    } else if (data.type === prefix + 'step') {
      frame.scrollIntoView({ behavior: 'auto', block: 'start' });
    } else if (data.type === prefix + 'submitted' && !submitted && (data.kind === 'enquiry' || data.kind === 'booking')) {
      submitted = true;
      // No names, addresses, phone numbers, email addresses or request payloads in analytics.
      window.gtag?.('event', 'generate_lead', {
        form_id: 'birmingham_property_services_quote',
        form_kind: data.kind,
        city: 'Birmingham',
      });
    }
  });
})();
