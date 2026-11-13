# Publisher review evidence — 13 November 2026

Review-only source for PocketLedger #1270. No website deployment, DNS change,
legacy replacement, Console entry or legal-text approval is claimed.

## Automated checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py
python3 scripts/build_legacy.py --preview
CHROMIUM_PATH=/usr/bin/chromium node scripts/browser_check.cjs
/path/to/actionlint -no-color -shellcheck= -pyflakes= .github/workflows/publisher-site.yml
```

Eight Python tests passed at the recorded browser source. After independent
review identified a release-state coupling in the tests, rejection cases were
moved to an explicit temporary draft fixture. The complete eight-test suite and
publish build also pass with isolated approved-source metadata; actual source
remains draft. They verify routes,
three-language equivalent navigation, local links/assets/fragments, meaningful
HTML landmarks, no script/forms/remote assets, draft publication rejection,
approved-release metadata, safe output ownership, immutable historical privacy
content and legacy-host paths/CNAME. No actual publish-mode approval was granted.

The installed system Chromium was launched in a separate headless context.
[Browser results](browser-results.json): **72 successful checks** — eight pages ×
three languages × desktop 1440px/light, mobile 390px/light, compact 320px/dark.
No horizontal overflow, third-party requests or browser runtime errors occurred.
Language links retained each equivalent document and the keyboard skip link was
reachable. Screenshot inspection found and corrected an unavailable arrow glyph
and decorative rule/text overlap before the final capture. This is browser proof,
not a formal full accessibility certification or Android-device evidence.

## Captured pages

- [English publisher homepage, desktop](previews/desktop.png)
- [Ukrainian Ledglet product page, mobile](previews/mobile-uk.png)
- [Russian Terms, compact dark](previews/terms-ru-compact-dark.png)

The current content is visibly draft/non-effective. Purchase and preview claims
are conditional; no store price is published. The old privacy source, effective
8 November 2026, remains archived and its live site is unchanged.

## Remaining acceptance

Independent Standards and Spec review, exact-head CI and creator review of the
actual three-language text are tracked in the owning PR. Before publication,
resolve applicable public operator disclosures and verify the new origin/HTTPS.
Canonical live-version proof precedes any legacy-host update or merge-ready claim
for the Android Terms action. Actual billing/privacy integration and Console
readback remain separate unperformed acceptance steps.
