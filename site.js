const WEB3FORMS_ACCESS_KEY = 'd64d1e94-de71-401e-a2d8-bdfae8ea74b5';
const WEB3FORMS_WEBHOOK_URL =
  'https://gradwell-web3forms-gateway.soft-cake-36e6.workers.dev/web3forms/commercial_epc/fd01f5cdd51407873c52d5c93577a9cb8e005db29a34d1a975e711f2b12fc11d';
const FORM_ID = 'birmingham_commercial_epc_quote';

const header = document.querySelector('.header');
const menu = document.querySelector('.menu');

menu?.addEventListener('click', () => {
  const open = header.classList.toggle('open');
  menu.setAttribute('aria-expanded', String(open));
});

document.querySelectorAll('.quote-form').forEach((form) => {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const button = form.querySelector('button[type="submit"]');
    const note = form.querySelector('.form-note');
    const originalLabel = button.textContent;
    const pageUrl = new URL(window.location.href);
    const formData = new FormData(form);

    button.disabled = true;
    button.textContent = 'Sending enquiry…';
    note.removeAttribute('role');
    note.textContent = 'Sending your property details securely…';

    formData.set('access_key', WEB3FORMS_ACCESS_KEY);
    formData.set('webhook', WEB3FORMS_WEBHOOK_URL);
    formData.set('subject', 'New Commercial EPC quote enquiry — Birmingham');
    formData.set('from_name', 'Birmingham Commercial EPC website');
    formData.set('business_key', 'commercial_epc');
    formData.set('form_id', FORM_ID);
    formData.set('service', 'Commercial EPC');
    formData.set('city', 'Birmingham');
    formData.set('page_url', pageUrl.href);
    formData.set('submitted_at', new Date().toISOString());
    formData.set(
      'property_address',
      String(formData.get('address') || ''),
    );
    formData.set('message', String(formData.get('details') || ''));

    for (const key of [
      'utm_source',
      'utm_medium',
      'utm_campaign',
      'utm_term',
      'utm_content',
      'gclid',
      'gbraid',
      'wbraid',
    ]) {
      const value = pageUrl.searchParams.get(key);
      if (value) formData.set(key, value);
    }

    try {
      const response = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || 'Unable to send your enquiry.');
      }

      window.gtag?.('event', 'generate_lead', {
        form_id: FORM_ID,
        service: 'Commercial EPC',
        city: 'Birmingham',
      });
      form.reset();
      button.textContent = 'Enquiry sent ✓';
      note.setAttribute('role', 'status');
      note.textContent =
        'Thank you — your details have been sent. We’ll be in touch about your quotation.';
    } catch (error) {
      button.disabled = false;
      button.textContent = originalLabel;
      note.setAttribute('role', 'alert');
      note.textContent =
        'Sorry, your enquiry could not be sent. Please try again in a moment.';
    }
  });
});
