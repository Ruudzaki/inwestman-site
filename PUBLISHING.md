# Publisher publication and legacy-policy handoff

## Current boundary

This is the creator-selected **new** `Ruudzaki/inwestman-site` repository.
`Ruudzaki/pocketledger-privacy` continues serving its existing policy and CNAME
`privacy.inwestman.uk`. Do not change that working host while this replacement is
being reviewed. No app upload, real payment, outreach or merge is part of publishing
these website sources.

The planned canonical Terms URL is
`https://inwestman.uk/products/ledglet/terms/`, with `/uk/` and `/ru/` prefixed
translations. A planned URL is not live proof.

## 1. Review the concrete legal text

Review all three Terms and privacy versions, the personal operator identity,
version/effective date, mandatory-rights/refund wording and current feature claims.
The intended operator is Kostiantyn Bilous, publishing as InWestMan. GitHub is a
supplementary identity link. Do not invent postal address, phone, tax, registration
or merchant details from an account name. Confirm any required public seller
contact details through the actual operator/Play process before the paid release.

The proposed text intentionally makes no selected governing-law, exclusive-court,
forced-arbitration or monetary-liability-cap commitment. Review legal adequacy for
the actual seller and buyer markets before publication; do not insert arbitrary
boilerplate. Keep the separate #1242 seller-route and billing/provider gates open.

Record creator approval of the exact EN/UK/RU text in the owning PR. Only then set
`legal_status` to `approved`, set a real ISO effective date and a release version,
and replace draft-specific history wording as appropriate. Run tests and
`python3 scripts/build_site.py --publish`. Review the resulting final artifact and
commit the approved metadata. Keep source approval and actual deployment receipts.

## 2. Prepare the new Pages origin

1. In this repository, Settings → Pages → Build and deployment, choose **GitHub Actions**.
2. Use the current [GitHub custom-domain guide](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).
   Set the new site's custom domain to `inwestman.uk`. Verify domain ownership
   using GitHub's recommended account-level verification before routing it.
3. Inspect the current apex DNS/origin before changing it. During preparation,
   `inwestman.uk` returned HTTP 522 through Cloudflare; this is not a working Pages
   origin. Preserve unrelated MX/TXT/mail configuration and the existing privacy
   subdomain. DNS/provider access is an operator task, not claimed by this source.
4. For an apex domain, GitHub currently documents A records `185.199.108.153`,
   `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, or a supported ALIAS/ANAME
   to `Ruudzaki.github.io`. Refresh the official guide at execution time. Avoid a
   wildcard record. Wait for GitHub's DNS/certificate checks and enable HTTPS.
5. Deploy only the reviewed main commit using the manual workflow with `publish`
   enabled and its exact approved full SHA. The build refuses draft Terms, missing
   effective dates and the unreviewed activation of billing. No automatic deploy
   runs on a push or PR.
6. Verify the workflow's actual Pages URL, correct certificate, public/no-login
   access, mobile rendering and EN/UK/RU Terms/privacy/support links. Do not infer
   success from a passed source build or from DNS configuration alone.

## 3. Preserve the old privacy site

The existing repository and its CNAME stay unchanged through the new deployment.
Its current root and `/index.html`, `/uk/`, `/uk/index.html`, `/ru/`, `/ru/index.html`
remain independently reachable. This is the safe initial compatibility behavior.

After the new canonical policy is approved, live and checked, prepare a separate
legacy update from the one maintained current source:

```sh
python3 scripts/build_legacy.py --preview  # review only; never deploy this draft
python3 scripts/build_legacy.py            # requires approval and live EN/UK/RU version checks
```

The generator produces the old root, `/uk/index.html` and `/ru/index.html` entry
files and retains `privacy.inwestman.uk` in its CNAME. Directory URLs and explicit
`index.html` URLs both work. Review/publish that output through a separate draft PR
to the legacy repository; no automatic cross-repository write is introduced. Prefer generating full
policy copies with the legacy CNAME retained, rather than redirecting the working
site to an unverified destination. The current release includes historical
snapshots; new legal edits must be maintained here, not independently rewritten in
both repositories. Do not merge a legacy redirect/copy update until all three
replacement language routes pass actual HTTP/content readback.

## 4. App and Console handoff

- Keep the app's current privacy destination until the policy migration is proved.
- Verify the canonical Terms URLs before the Settings link PR becomes merge-ready.
- The app's Terms link does not implement checkout consent or material-change
  notices. Add those to the billing/change delivery that needs them.
- In Play Console, use the verified public app-specific Terms URL in the trader
  declaration and record non-sensitive operator readback. Do not upload phone,
  address, financial records, private screenshots or credentials into this repo.
- Confirm the 18+ intended audience against the actual Play target-audience entry;
  website wording alone does not change the Console or introduce age verification.
- #1270 stays open until text approval, live publication, legacy compatibility and
  Console readback are actually complete.

## Recovery

Cancel an uncommitted deployment if its approved source or legal content is wrong.
For a published issue, retain the previous reviewed artifact and version history;
restore an approved compatible website artifact while investigating. This has no
ability to reverse Play purchases or app database changes. Keep the old privacy
site available throughout. Record actual deployment/source/content readback before
retrying a failed or uncertain publication.
