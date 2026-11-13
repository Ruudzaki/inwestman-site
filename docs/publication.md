# Publication — 13 November 2026

The creator reviewed the concrete EN/UK/RU legal draft in PR #1 and approved it
in the implementation conversation: “Ok, I approve. Please switch to review,
and the merge. Make the Pages reachable”. This authorizes the review transition,
merge and publication. The approved legal bodies are unchanged from
`0f2050987de7f6840826d8c75b9e3d79b3043a43`; release metadata now records version
`2026-11-13`, approved status and effective date `2026-11-13`. Product/history
introductions use release wording. Billing remains unavailable.

Both PRs were marked ready for review. Enabling Pages through the integration
returned HTTP 403 (Pages administration permission unavailable). The creator was
given the exact repository Pages settings and apex DNS records. Deployment and
live HTTPS/content readback remain pending; approval and a passing build alone
are not deployment proof. The existing `privacy.inwestman.uk` site returned
HTTP 200 and remains unchanged.

The separate seller/billing and Console release gates remain open. This
publication does not upload an app, implement checkout, change payment settings
or certify private Console entries.

## Approved artifact verification

`python3 -m unittest discover -s tests -v` passed all eight tests with the real
approved metadata. `python3 scripts/build_site.py --publish` built 24 pages.
`CHROMIUM_PATH=/usr/bin/chromium QA_OUTPUT=.qa/release node scripts/browser_check.cjs`
passed all 72 route/language/viewport/theme checks. The current committed
`docs/previews/` screenshots and `docs/browser-results.json` show the approved
release; `docs/verification.md` records the preceding draft verification.
