# InWestMan

Publisher website for **Kostiantyn Bilous, publishing as InWestMan**, with Ledglet
product information, email support and versioned English/Ukrainian/Russian legal
pages. Related delivery: [PocketLedger #1270](https://github.com/Ruudzaki/PocketLedger/issues/1270).

## Build and verify

Python 3.10+; no runtime packages, client JavaScript, remote assets or Node build.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py
python3 -m http.server 8080 --directory dist
```

Open `http://127.0.0.1:8080/`. The generated `dist/` is ignored. Source content is
under `content/`, shared page rendering under `scripts/`, and local assets under
`assets/`. This repository contains public website source only, not private app
code or user data.

Optional browser verification, with Playwright and Chromium installed:

```sh
CHROMIUM_PATH=/usr/bin/chromium node scripts/browser_check.cjs
```

This visits every page in every language at desktop, mobile and compact/dark
sizes, checks links/overflow/network requests, and saves screenshots plus JSON
under ignored `.qa/`. It uses a separate headless browser, not a personal profile.

## Content and legal versions

- `site.json` owns the origin, language list, legal version/status and effective date.
- `content/ui.json` owns translated interface/product/support/website-privacy copy.
- `content/{en,uk,ru}/{terms,privacy}.html` owns current app legal content.
- `content/archive/2026-11-08/` preserves the previously published privacy text;
  the manifest records source hashes. Historical documents retain their identity.
- English is the editing source. Review all three translations together; archive
  an effective legal version before replacing it, update its history entry and
  generated routes, and retain immutable snapshots.
- New app-language releases must include translated site navigation, product,
  support and legal pages, equivalent language links and version-parity checks.
  Extend `site.json`, translations, corresponding archives/routes and tests.
- Material changes need an appropriate in-app notice and explicit agreement where
  needed. That integration belongs to the app change that introduces them; this
  site does not claim an unimplemented notice or purchase-acceptance flow.

Drafts use `legal_status: draft`, no effective date, a visible non-effective banner
and `noindex`. The publish build refuses drafts. After the creator reviews the
actual text/translations and applicable public disclosures, record approval in the
owning PR, set an actual effective date/status and use `--publish`. A configuration
flag is not itself proof of creator approval.

The initial product/purchase text distinguishes the planned paid beta from
currently unshipped checkout. `billing_available` deliberately remains false;
actual provider/data-flow disclosure and app proof precede any billing release.

## Publication

See [PUBLISHING.md](PUBLISHING.md) for Pages/domain setup, legal approval, legacy
compatibility and Console readback. The workflow builds review artifacts on PRs
and main pushes; **deployment is owner-triggered only** after the approved source
SHA and legal metadata match. Merging source does not automatically publish Terms.

## Public sources

- [Google Play trader declarations](https://support.google.com/googleplay/android-developer/answer/17594752)
- [Google User Data policy](https://support.google.com/googleplay/android-developer/answer/10144311)
- [One-time Play products](https://developer.android.com/google/play/billing/one-time-products)
- [Play refund rules](https://support.google.com/googleplay/answer/2479637)
- [Digital-content guarantees](https://europa.eu/youreurope/citizens/consumers/shopping/guarantees/index_en.htm)
- [Fair contract terms](https://europa.eu/youreurope/citizens/consumers/unfair-treatment/unfair-contract-terms/index_en.htm)

Sources checked 13 November 2026. Product decisions follow the creator-approved
brief; draft preparation does not establish seller/payment clearance.
