import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const read = (file) => readFileSync(new URL(`../${file}`, import.meta.url), 'utf8');
const origin = 'https://gradwell-inspection-booking.info512176.chatgpt.site';
const prefix = 'birmingham:service-quote:';

function environment({ href = 'https://birminghamcommercialepc.co.uk/quote', stored = '{}', blockedStorage = false } = {}) {
  const listeners = {};
  const frameListeners = {};
  const messages = [];
  const analytics = [];
  const loading = { hidden: false, setAttribute: () => { loading.hidden = true; } };
  const frame = {
    style: {}, scrolls: 0,
    contentWindow: { postMessage: (...message) => messages.push(message) },
    addEventListener: (type, listener) => { frameListeners[type] = listener; },
    scrollIntoView: () => { frame.scrolls++; },
  };
  let storedValue = stored;
  const window = {
    location: { href },
    sessionStorage: {
      getItem: () => { if (blockedStorage) throw new Error('blocked'); return storedValue; },
      setItem: (_, value) => { if (blockedStorage) throw new Error('blocked'); storedValue = value; },
    },
    addEventListener: (type, listener) => { listeners[type] = listener; },
    gtag: (...args) => analytics.push(args),
  };
  const document = {
    querySelector: () => null,
    getElementById: (id) => id === 'birmingham-quote-frame' ? frame : loading,
  };
  const context = vm.createContext({ window, document, URL });
  vm.runInContext(read('site.js'), context);
  vm.runInContext(read('quote-embed.js'), context);
  const message = (data, overrides = {}) => listeners.message({ data, origin, source: frame.contentWindow, ...overrides });
  return { window, frame, loading, messages, analytics, message, frameListeners, saved: () => JSON.parse(storedValue) };
}

test('quote page retains canonical and analytics while offering a full-width branded shared form', () => {
  const page = read('quote.html');
  assert.match(page, /rel="canonical" href="https:\/\/birminghamcommercialepc\.co\.uk\/quote"/);
  assert.match(page, /G-J8DBCT65BY/);
  assert.match(page, /ykub63ccq0/);
  assert.match(page, /birmingham-service-quote\?embed=1/);
  assert.match(page, /title="Choose services and build your Birmingham property quotation"/);
  assert.match(page, /birmingham-service-quote" target="_blank" rel="noopener noreferrer"/);
  assert.doesNotMatch(page, /<form\b|class="[^"\n]*lime/);
  assert.match(read('styles.css'), /\.booking-shell iframe\{[^}]*width:100%/);
});

test('all routes use the unified quote page and no legacy collection remains', () => {
  for (const name of ['index.html', 'about.html', 'quote.html']) {
    assert.match(read(name), /mobile-quote-link/);
    assert.doesNotMatch(read(name), /class="quote-form"/);
  }
  assert.doesNotMatch(read('site.js'), /web3forms|fetch\(|FormData/);
  assert.match(read('index.html'), /Choose your services/);
});

test('context sends only bounded approved attribution and a sanitised page URL', () => {
  const env = environment({
    href: 'https://birminghamcommercialepc.co.uk/quote?utm_source=google&gclid=abc&email=private%40example.test&phone=123#secret',
    stored: JSON.stringify({ utm_medium: 'cpc', name: 'Private Name', utm_term: 'x'.repeat(501) }),
  });
  env.frameListeners.load();
  const [payload, target] = env.messages[0];
  assert.equal(target, origin);
  assert.equal(payload.type, prefix + 'context');
  assert.deepEqual(JSON.parse(JSON.stringify(payload.attribution)), {
    utm_source: 'google', utm_medium: 'cpc', gclid: 'abc',
    page_url: 'https://birminghamcommercialepc.co.uk/quote?utm_source=google&utm_medium=cpc&gclid=abc',
  });
  assert.doesNotMatch(JSON.stringify(env.saved()), /private|name|phone|utm_term/i);
});

test('blocked or malformed storage never prevents the form loading', () => {
  for (const options of [{ blockedStorage: true }, { stored: 'broken json' }, { stored: 'null' }, { stored: '[]' }]) {
    const env = environment(options);
    env.message({ type: prefix + 'ready' });
    assert.equal(env.loading.hidden, true);
    assert.equal(env.messages[0][0].attribution.page_url, 'https://birminghamcommercialepc.co.uk/quote');
  }
});

test('spoofed origin and other window messages are ignored for every operation', () => {
  const env = environment();
  for (const overrides of [{ origin: 'https://untrusted.example' }, { source: {} }, { origin: origin + '.example' }]) {
    for (const type of ['ready', 'resize', 'step', 'submitted']) env.message({ type: prefix + type, height: 1800, kind: 'enquiry' }, overrides);
  }
  assert.equal(env.loading.hidden, false);
  assert.equal(env.messages.length, 0);
  assert.equal(env.analytics.length, 0);
  assert.equal(env.frame.scrolls, 0);
  assert.equal(env.frame.style.height, undefined);
});

test('only finite bounded heights resize the iframe', () => {
  const env = environment();
  for (const height of [0, 479, 6001, Infinity, NaN, '1200']) env.message({ type: prefix + 'resize', height });
  assert.equal(env.frame.style.height, undefined);
  env.message({ type: prefix + 'resize', height: 1234.2 });
  assert.equal(env.frame.style.height, '1235px');
});

test('legitimate ready and step events work without tracking conversion', () => {
  const env = environment();
  env.message({ type: prefix + 'ready' });
  env.message({ type: prefix + 'step' });
  assert.equal(env.loading.hidden, true);
  assert.equal(env.messages.length, 1);
  assert.equal(env.frame.scrolls, 1);
  assert.equal(env.analytics.length, 0);
});

test('only successful known submission kinds generate one PII-free conversion event', () => {
  const env = environment();
  for (const data of [null, [], 'submitted', { type: prefix + 'submitted', kind: 'failed' }, { type: 'ced:service-quote:submitted', kind: 'booking' }]) env.message(data);
  assert.equal(env.analytics.length, 0);
  env.message({ type: prefix + 'submitted', kind: 'booking', email: 'private@example.test', address: 'private' });
  env.message({ type: prefix + 'submitted', kind: 'enquiry' });
  assert.deepEqual(JSON.parse(JSON.stringify(env.analytics)), [['event', 'generate_lead', {
    form_id: 'birmingham_property_services_quote', form_kind: 'booking', city: 'Birmingham',
  }]]);
});
