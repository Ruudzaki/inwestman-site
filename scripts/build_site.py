#!/usr/bin/env python3
"""Render versioned publisher pages; publishing requires approved legal metadata."""
import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import shutil

ROUTES = {
    'home': '', 'product': 'products/ledglet', 'support': 'support',
    'website_privacy': 'privacy', 'privacy': 'products/ledglet/privacy',
    'terms': 'products/ledglet/terms', 'history': 'products/ledglet/legal-history',
    'archive': 'products/ledglet/legal-history/2026-11-08/privacy',
}


def route(lang, page):
    parts = ([lang] if lang != 'en' else []) + ([ROUTES[page]] if ROUTES[page] else [])
    return '/' + '/'.join(parts) + ('/' if parts else '')


def link(url, label, css=''):
    return f'<a href="{escape(url, quote=True)}" class="{css}">{label}</a>'


def metadata(source, publish):
    config = json.loads((source / 'site.json').read_text())
    translations = json.loads((source / 'content/ui.json').read_text())
    languages = config['languages']
    if languages != ['en', 'uk', 'ru'] or set(translations) != set(languages):
        raise ValueError('Complete supported language translations are required')
    for lang in languages:
        if set(translations[lang]) != set(translations['en']):
            raise ValueError(f'Incomplete translation: {lang}')
        for doc in ('privacy', 'terms'):
            if not (source / f'content/{lang}/{doc}.html').is_file():
                raise ValueError(f'Missing legal translation: {lang}/{doc}')
    if config['legal_status'] not in ('draft', 'approved'):
        raise ValueError('Unknown legal approval status')
    if publish and (config['legal_status'] != 'approved' or not config['effective_date']):
        raise ValueError('Creator legal-text approval and an effective date are required before publication')
    if config['legal_status'] == 'draft' and config['effective_date']:
        raise ValueError('A draft cannot claim an effective date')
    if config['effective_date']:
        date.fromisoformat(config['effective_date'])
    if config['billing_available']:
        raise ValueError('This version describes unshipped billing; update disclosures before enabling it')
    return config, translations


def legal_article(content, label):
    headings = []
    def heading(match):
        identifier = f'section-{len(headings) + 1}'
        headings.append((identifier, match.group(1)))
        return f'<h2 id="{identifier}">{match.group(1)}</h2>'
    content = re.sub(r'<h2>(.*?)</h2>', heading, content, flags=re.S)
    toc = ''.join(f'<li>{link("#" + identifier, title)}</li>' for identifier, title in headings)
    return f'<div class="legal-layout"><aside class="contents"><details open><summary>{label}</summary><ol>{toc}</ol></details></aside><article class="legal-copy">{content}</article></div>'


def page_body(source, lang, page, t, config):
    product = route(lang, 'product')
    support = route(lang, 'support')
    privacy = route(lang, 'privacy')
    terms = route(lang, 'terms')
    badge = f'<span class="badge">{t["beta"]}</span>'
    mark = '<img src="/assets/ledglet.svg" width="108" height="108" alt="">'
    legal_links = f'<div class="link-row">{link(privacy, t["privacy"])}{link(terms, t["terms"])}{link(route(lang, "history"), t["history"])}</div>'
    if page == 'home':
        title = t['hero']
        body = f'''<section class="hero"><div><p class="eyebrow">{t['eyebrow']}</p><h1>{title}</h1><p class="lead">{t['intro']}</p><div class="actions">{link(product, t['explore'] + ' <span aria-hidden="true">→</span>', 'button')}{link('https://github.com/Ruudzaki', t['github'], 'text-link')}</div></div><div class="hero-art" aria-hidden="true"><div class="art-grid"></div><div class="art-monogram">iw<span>m.</span></div><div class="art-caption">INWESTMAN<br><span>Kostiantyn Bilous</span></div></div></section>
<section class="product-section" id="products"><p class="eyebrow">{t['selected']}</p><div class="product-card"><div class="product-copy"><p class="eyebrow">{t['product_tag']}</p><h2>Ledglet {badge}</h2><h3>{t['product_title']}</h3><p>{t['product_intro']}</p>{link(product, t['product_cta'] + ' <span aria-hidden="true">→</span>', 'text-link')}</div><div class="product-art" aria-hidden="true">{mark}<span>Ledglet</span><div class="art-rules"><i></i><i></i><i></i></div></div></div></section>
<section class="about"><p class="eyebrow">{t['about_label']}</p><div><h2>{t['about_title']}</h2><p>{t['about_text']}</p>{link(support, t['contact'] + ' <span aria-hidden="true">→</span>', 'text-link')}</div></section>'''
        return 'InWestMan', body
    if page == 'product':
        features = ''.join(f'<div><span class="feature-number">0{i+1}</span><h3>{t[k+"_label"]}</h3><p>{t[k+"_text"]}</p></div>' for i, k in enumerate(('local', 'daily', 'control')))
        body = f'''<section class="product-hero"><div><p class="eyebrow">{t['product_tag']}</p><h1>Ledglet</h1>{badge}<p class="lead">{t['product_pitch']}</p><p>{t['product_detail']}</p>{link('mailto:support@inwestman.uk', t['access_cta'] + ' <span aria-hidden="true">→</span>', 'button')}</div><div class="product-art large" aria-hidden="true">{mark}<span>Ledglet</span><div class="art-rules"><i></i><i></i><i></i></div></div></section>
<section class="feature-list">{features}</section><section class="offer"><p class="eyebrow">FREE / PRO</p><h2>{t['offer_title']}</h2><p class="section-lead">{t['offer_intro']}</p><div class="offer-grid"><div><h3>{t['free_title']}</h3><p>{t['free_text']}</p></div><div><h3>{t['pro_title']}</h3><p>{t['pro_text']}</p></div></div><div class="preview-note"><h3>{t['preview_title']}</h3><p>{t['preview_text']}</p></div><p class="small muted">{t['price_note']}</p></section>
<section class="about"><div><h2>{t['access_title']}</h2><p>{t['access_text']}</p></div><div><p class="eyebrow">{t['reading']}</p><p>{t['legal_intro']}</p>{legal_links}</div></section>'''
        return 'Ledglet · InWestMan', body
    if page == 'support':
        return t['support'], f'<section class="page-intro"><p class="eyebrow">INWESTMAN / LEDGLET</p><h1>{t["support_title"]}</h1><p class="lead">{t["support_intro"]}</p>{link("mailto:support@inwestman.uk", "support@inwestman.uk", "email-link")}</section><section class="reading-copy"><p>{t["support_guidance"]}</p><p>{t["support_promise"]}</p>{link(route(lang,"website_privacy"),t["website_privacy"],"text-link")}</section>'
    if page == 'website_privacy':
        return t['web_title'], f'<section class="page-intro"><p class="eyebrow">INWESTMAN</p><h1>{t["web_title"]}</h1></section><article class="reading-copy"><p>{t["web_text"]}</p><p>{link("https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement", t["hosting_privacy"])}</p><p>{t["web_email"]}</p><p>{t["web_product"]}</p>{link(privacy,t["privacy"],"text-link")}</article>'
    if page == 'history':
        title = t['history']
        current = t['current_draft'] if config['legal_status'] == 'draft' else t['current_version']
        changes = t['draft_changes'] if config['legal_status'] == 'draft' else t['release_changes']
        body = f'<section class="page-intro"><p class="eyebrow">LEDGLET</p><h1>{title}</h1><p class="lead">{t["history_intro"]}</p></section><section class="reading-copy"><h2>{current}</h2><p>{changes}</p>{legal_links}<h2>{t["archive_title"]}</h2><p>{t["archive_text"]}</p>{link(route(lang,"archive"),t["archive_link"],"text-link")}</section>'
        return title, body
    if page == 'archive':
        content = (source / f'content/archive/2026-11-08/{lang}/privacy.html').read_text()
        title = re.search(r'<h1>(.*?)</h1>', content, re.S).group(1)
        content = re.sub(r'<h1>.*?</h1>', '', content, count=1, flags=re.S)
        intro = f'<p class="archive-note">{t["archived"]}</p>'
    else:
        content = (source / f'content/{lang}/{page}.html').read_text()
        title = t[page + '_title']
        intro = ''
    return title, f'<section class="page-intro legal-intro"><p class="eyebrow">LEDGLET / INWESTMAN</p><h1>{title}</h1>{intro}<!--LEGAL_METADATA--></section>' + legal_article(content, t['contents'])


def render(source, lang, page, config, translations):
    t = translations[lang]
    title, body = page_body(source, lang, page, t, config)
    origin = config['origin']
    canonical = origin + route(lang, page)
    is_draft = config['legal_status'] == 'draft'
    status = 'archived' if page == 'archive' else config['legal_status']
    version = config['legacy_policy_version'] if page == 'archive' else config['legal_version']
    effective = config['legacy_policy_version'] if page == 'archive' else config['effective_date'] or t['not_effective']
    meta = f'<dl class="legal-meta" data-legal-status="{status}"><div><dt>{t["version"]}</dt><dd>{version}</dd></div><div><dt>{t["effective"]}</dt><dd>{effective}</dd></div></dl>'
    body = body.replace('<!--LEGAL_METADATA-->', meta)
    alternates = ''.join(f'<link rel="alternate" hreflang="{other}" href="{origin + route(other,page)}">' for other in config['languages'])
    languages = ''.join(f'<a href="{route(other,page)}" lang="{other}" hreflang="{other}"'+(' aria-current="page"' if other == lang else '')+f'>{translations[other]["lang_name"]}</a>' for other in config['languages'])
    def nav_item(target, label):
        current = ' aria-current="page"' if (page == target or (target == 'product' and page in ('privacy','terms','history','archive'))) else ''
        return f'<a href="{route(lang,target)}"{current}>{label}</a>'
    navigation = nav_item('product',t['products']) + nav_item('support',t['support'])
    banner = f'<div class="draft-banner" role="status">{t["draft"]}</div>' if is_draft else ''
    robots = 'noindex, nofollow' if is_draft or page == 'archive' else 'index, follow'
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(t['page_description'],quote=True)}"><meta name="robots" content="{robots}"><meta name="color-scheme" content="light dark"><link rel="canonical" href="{canonical}">{alternates}<link rel="stylesheet" href="/assets/site.css"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"></head>
<body><a class="skip" href="#main">{t['skip']}</a>{banner}<header class="site-header"><a class="wordmark" href="{route(lang,'home')}" aria-label="InWestMan · {t['home']}">InWestMan<span class="brand-dot">.</span></a><nav aria-label="{t['menu']}">{navigation}</nav><nav class="languages" aria-label="{t['language']}">{languages}</nav></header>
<main id="main" class="site-main">{body}</main><footer class="site-footer"><div><a class="wordmark" href="{route(lang,'home')}">InWestMan<span class="brand-dot">.</span></a><p>{t['footer_text']}</p><p class="small">© 2026 {t['operator']}</p></div><div class="footer-links">{link(route(lang,'support'),t['support'])}{link(route(lang,'privacy'),t['privacy'])}{link(route(lang,'terms'),t['terms'])}{link(route(lang,'history'),t['history'])}{link(route(lang,'website_privacy'),t['website_privacy'])}{link('https://github.com/Ruudzaki','GitHub →')}</div></footer></body></html>\n'''


def prepare_output(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output == source or source.is_relative_to(output):
        raise ValueError('Output must not contain the source tree')
    if output.exists() and not (output / '.inwestman-generated').is_file():
        raise ValueError('Output exists without the generator ownership marker')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / '.inwestman-generated').write_text('Generated output; edit content sources.\n')
    shutil.copytree(source / 'assets', output / 'assets')
    return output


def build_site(source, output, publish=False):
    source = Path(source).resolve()
    config, translations = metadata(source, publish)
    output = prepare_output(source, output)
    for lang in config['languages']:
        for page in ROUTES:
            destination = output / route(lang,page).lstrip('/') / 'index.html'
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(render(source,lang,page,config,translations))
    (output / '.nojekyll').touch()
    (output / 'CNAME').write_text('inwestman.uk\n')
    (output / 'robots.txt').write_text('User-agent: *\n' + ('Disallow: /\n' if config['legal_status'] == 'draft' else 'Allow: /\nSitemap: https://inwestman.uk/sitemap.xml\n'))
    urls = ''.join(f'<url><loc>{config["origin"] + route(lang,page)}</loc></url>' for lang in config['languages'] for page in ROUTES if page != 'archive')
    (output / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('dist'))
    parser.add_argument('--publish', action='store_true', help='Require creator-approved legal metadata')
    args = parser.parse_args()
    try:
        result = build_site(Path(__file__).resolve().parents[1], args.output, args.publish)
    except ValueError as error:
        parser.exit(2, f'{error}\n')
    print(f'Built {len(ROUTES) * 3} pages in {result}')
