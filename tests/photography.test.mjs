import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';

const root = new URL('../', import.meta.url);
const pages = ['index.html', 'about.html', 'quote.html', '404.html'];
const read = (file) => readFileSync(new URL(file, root), 'utf8');
const families = [
  'birmingham-cadbury-8171',
  'birmingham-retail-atrium-6146',
  'birmingham-changing-skyline-2742',
  'birmingham-city-street-4943',
  'birmingham-glass-offices-2707',
  'birmingham-canal-evening-4719',
  'birmingham-historic-centre-2661',
  'birmingham-forum-4939',
];
const expectedAssets = families.flatMap((family) => [
  `images/${family}.jpg`,
  `images/${family}.webp`,
  `images/${family}-small.webp`,
]);
const attributes = (tag) => Object.fromEntries(
  [...tag.matchAll(/([\w:-]+)\s*=\s*(["'])(.*?)\2/gs)].map(([, name, , value]) => [name, value]),
);
const imageTags = (html) => [...html.matchAll(/<img\b[^>]*>/gi)].map(([tag]) => attributes(tag));

test('only the eight supplied photo families are shipped, with responsive formats', () => {
  assert.deepEqual(
    readdirSync(new URL('images/', root)).map((name) => `images/${name}`).sort(),
    [...expectedAssets].sort(),
  );
  for (const file of expectedAssets) {
    const data = readFileSync(new URL(file, root));
    assert.ok(data.length > 0, `${file} must not be empty`);
    if (file.endsWith('.webp')) {
      assert.equal(data.toString('ascii', 0, 4), 'RIFF', `${file} must be a WebP file`);
      assert.equal(data.toString('ascii', 8, 12), 'WEBP', `${file} must be a WebP file`);
    } else {
      assert.equal(data.readUInt16BE(0), 0xffd8, `${file} must be a JPEG file`);
    }
  }
});

test('all eight supplied photographs appear on the homepage with accessible dimensions', () => {
  const images = imageTags(read('index.html'));
  assert.deepEqual(
    [...new Set(images.map(({ src }) => src))].sort(),
    families.map((family) => `images/${family}.jpg`).sort(),
  );
  for (const page of pages) {
    for (const image of imageTags(read(page))) {
      assert.ok(image.alt?.trim(), `${page}: ${image.src} needs descriptive alternative text`);
      assert.ok(Number(image.width) > 0, `${page}: ${image.src} needs an intrinsic width`);
      assert.ok(Number(image.height) > 0, `${page}: ${image.src} needs an intrinsic height`);
    }
  }
});

test('rendered image and responsive source references resolve to supplied assets', () => {
  const referenced = new Set();
  for (const page of pages) {
    for (const [tag] of read(page).matchAll(/<(?:img|source)\b[^>]*>/gi)) {
      const { src, srcset } = attributes(tag);
      const sources = [src, ...(srcset?.split(',').map((entry) => entry.trim().split(/\s+/)[0]) ?? [])].filter(Boolean);
      assert.ok(sources.length, `${page}: image elements must have a source`);
      for (const file of sources) {
        assert.ok(expectedAssets.includes(file), `${page}: unexpected photograph ${file}`);
        assert.ok(existsSync(new URL(file, root)), `${page}: missing photograph ${file}`);
        referenced.add(file);
      }
    }
  }
  for (const file of expectedAssets) {
    assert.ok(referenced.has(file), `${file} must be used by a rendered image or responsive source`);
  }
});

test('social cards use the replacement photography on each indexable page', () => {
  const expected = 'https://birminghamcommercialepc.co.uk/images/birmingham-forum-4939.jpg';
  for (const page of pages.filter((name) => name !== '404.html')) {
    const metas = [...read(page).matchAll(/<meta\b[^>]*>/gi)].map(([tag]) => attributes(tag));
    for (const key of ['og:image', 'twitter:image']) {
      const matching = metas.filter((meta) => meta.property === key || meta.name === key);
      assert.equal(matching.length, 1, `${page}: one ${key} is required`);
      assert.equal(matching[0].content, expected, `${page}: ${key} must use the supplied photo`);
    }
  }
});

test('previous photography is removed from pages, metadata and deployed files', () => {
  for (const extension of ['jpg', 'png', 'webp']) {
    assert.equal(existsSync(new URL(`birmingham-property.${extension}`, root)), false);
  }
  for (const file of [...pages, 'styles.css', 'site.js', 'quote-embed.js', 'robots.txt', 'sitemap.xml']) {
    assert.doesNotMatch(read(file), /birmingham-property\.(?:jpe?g|png|webp)/i, `${file} retains a previous photo reference`);
  }
});
