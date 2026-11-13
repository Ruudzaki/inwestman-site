#!/usr/bin/env python3
"""Prepare old privacy-host pages from the canonical source after live verification."""
import argparse
from html import escape
from pathlib import Path
import re
from urllib.request import urlopen

from build_site import metadata, prepare_output, render, route


def verify_canonical(config):
    for lang in config['languages']:
        url = config['origin'] + route(lang, 'privacy')
        with urlopen(url, timeout=20) as response:
            if response.status != 200 or response.geturl() != url:
                raise ValueError(f'Canonical policy is not verified: {url}')
            body = response.read().decode('utf-8')
        if 'data-legal-status="approved"' not in body or escape(config['legal_version']) not in body:
            raise ValueError(f'Canonical policy version/approval mismatch: {url}')


def build_legacy(source, output, preview=False):
    source = Path(source).resolve()
    config, translations = metadata(source, publish=not preview)
    if not preview:
        verify_canonical(config)
    output = prepare_output(source, output)
    for lang in config['languages']:
        html = render(source, lang, 'privacy', config, translations)
        # Navigation goes to the canonical publisher; style assets stay available
        # on the legacy host even if the main site subsequently has an outage.
        html = re.sub(r'<a([^>]*?)href="(/[^\"]*)"',
                      lambda match: f'<a{match[1]}href="{config["origin"]}{match[2]}"', html)
        target = output / ('' if lang == 'en' else lang) / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html)
    (output / 'CNAME').write_text('privacy.inwestman.uk\n')
    (output / '.nojekyll').touch()
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('legacy-dist'))
    parser.add_argument('--preview', action='store_true', help='Build review-only output without live verification')
    args = parser.parse_args()
    try:
        target = build_legacy(Path(__file__).resolve().parents[1], args.output, args.preview)
    except (ValueError, OSError) as error:
        parser.exit(2, f'{error}\n')
    print(f'Built legacy policy output in {target}; no repository or deployment was changed')
