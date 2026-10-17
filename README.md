# Commercial EPC Birmingham

A responsive static website for a Birmingham and West Midlands commercial EPC service.

## Pages

- Home: services, process, coverage, quotation entry and FAQs
- About: service approach, principles and assessment scope
- Quote: five-step, multi-service quotation and booking form

## Booking form

`/quote` embeds the Birmingham-branded shared form at
`https://gradwell-inspection-booking.info512176.chatgpt.site/birmingham-service-quote`.
The shared application owns postcode lookup, pricing, the inline calendar, validation,
and submissions. This static site does not collect or post customer details directly.

`quote-embed.js` accepts only `birmingham:service-quote:*` messages from that exact
iframe and hosted origin. The parent sends allowlisted campaign attribution and a
sanitised page URL; conversion analytics contain no customer details. There is an
always-visible direct-form fallback. Existing `/quote` canonical links are retained.

Run static and message-boundary tests with `node --test tests/*.test.mjs`.

## Run locally

Open `index.html` directly, or serve the folder with any static web server.

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Photography

The eight photographs in `images/` were supplied for the Birmingham website.
The numeric filename suffixes map to the original `IMG_<number>.HEIC` files.
Each image has a 1200 × 1600 JPEG fallback, a WebP version and a 600 × 800
WebP variant. Published files omit EXIF and location metadata; the original
HEIC files are not included. The city gallery is contextual photography,
not a claim that the pictured buildings are completed client projects.

## Publishing

The site is ready for GitHub Pages. In the repository settings, choose **Pages → Deploy from a branch**, then select the `main` branch and `/ (root)` folder.
