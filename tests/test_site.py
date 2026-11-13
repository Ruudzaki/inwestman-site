import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_site import build_site
from build_legacy import build_legacy

SOURCE = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.links = []
        self.ids = []
        self.lang = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for attr in ('href', 'src'):
            if attr in attrs:
                self.links.append((tag, attr, attrs[attr]))


class PublisherSiteTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'source'
        shutil.copytree(SOURCE / 'content', self.source / 'content')
        shutil.copytree(SOURCE / 'assets', self.source / 'assets')
        config = json.loads((SOURCE / 'site.json').read_text())
        # Draft rejection is a fixture, not an assumption about the real release.
        config.update(legal_status='draft', effective_date=None, legal_version='2026-11-13-draft-1')
        (self.source / 'site.json').write_text(json.dumps(config))
        self.output = Path(self.temp.name) / 'site'
        build_site(self.source, self.output)

    def test_every_page_has_equivalent_languages_and_accessible_landmarks(self):
        pages = list(self.output.rglob('*.html'))
        self.assertEqual(24, len(pages))
        for page in pages:
            text = page.read_text()
            document = Document(text)
            self.assertEqual(1, document.tags.count('h1'), page)
            self.assertIn('main', document.tags, page)
            self.assertEqual(len(document.ids), len(set(document.ids)), page)
            self.assertIn(document.lang, ('en', 'uk', 'ru'))
            self.assertEqual(3, text.count('rel="alternate" hreflang='), page)
            for tag in ('script', 'form', 'iframe', 'video'):
                self.assertNotIn(tag, document.tags, page)

    def test_all_local_links_assets_and_fragment_targets_resolve(self):
        for page in self.output.rglob('*.html'):
            current = '/' + page.relative_to(self.output).as_posix()
            for tag, attr, link in Document(page.read_text()).links:
                parsed = urlsplit(urljoin('https://inwestman.uk' + current, link))
                if attr == 'src' or tag == 'link':
                    self.assertIn(parsed.netloc, ('', 'inwestman.uk'), (page, link))
                if parsed.scheme not in ('http', 'https') or parsed.netloc != 'inwestman.uk':
                    continue
                target = self.output / unquote(parsed.path).lstrip('/')
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.is_file(), (page, link, target))
                if parsed.fragment:
                    self.assertIn(parsed.fragment, Document(target.read_text()).ids, (page, link))

    def test_legal_drafts_do_not_fabricate_approval_effective_date_or_checkout(self):
        for lang in ('en', 'uk', 'ru'):
            prefix = '' if lang == 'en' else lang + '/'
            terms = (self.output / prefix / 'products/ledglet/terms/index.html').read_text()
            self.assertIn('2026-11-13-draft-1', terms)
            self.assertIn('data-legal-status="draft"', terms)
            self.assertIn('noindex', terms)
            self.assertNotIn('$5.99', terms)
            self.assertEqual(11, terms.count('<h2 id='))
        with self.assertRaisesRegex(ValueError, 'approval'):
            build_site(self.source, Path(self.temp.name) / 'published', publish=True)

    def test_approved_release_has_a_real_effective_date_and_current_history(self):
        source = self.source
        config = json.loads((SOURCE / 'site.json').read_text())
        config.update(legal_status='approved', effective_date='2026-11-14', legal_version='2026-11-14')
        (source / 'site.json').write_text(json.dumps(config))
        output = Path(self.temp.name) / 'approved-site'
        build_site(source, output, publish=True)
        terms = (output / 'products/ledglet/terms/index.html').read_text()
        self.assertIn('data-legal-status="approved"', terms)
        self.assertIn('2026-11-14', terms)
        self.assertNotIn('Draft for review', terms)
        history = (output / 'products/ledglet/legal-history/index.html').read_text()
        self.assertIn('Current version', history)
        self.assertNotIn('Current review draft', history)

    def test_legacy_preview_preserves_language_entry_paths_and_cname(self):
        output = Path(self.temp.name) / 'legacy'
        build_legacy(self.source, output, preview=True)
        self.assertEqual('privacy.inwestman.uk', (output / 'CNAME').read_text().strip())
        for lang in ('en', 'uk', 'ru'):
            target = output / ('' if lang == 'en' else lang) / 'index.html'
            document = Document(target.read_text())
            self.assertEqual(lang, document.lang)
            for tag, attr, url in document.links:
                if tag == 'a' and not url.startswith(('#', 'mailto:')):
                    self.assertTrue(url.startswith('https://'), url)
            self.assertTrue((output / 'assets/site.css').is_file())
        with self.assertRaisesRegex(ValueError, 'approval'):
            build_legacy(self.source, Path(self.temp.name) / 'unapproved-legacy')

    def test_output_ownership_prevents_deleting_unrelated_files(self):
        unrelated = Path(self.temp.name) / 'unrelated'
        unrelated.mkdir()
        (unrelated / 'keep.txt').write_text('preserve')
        with self.assertRaisesRegex(ValueError, 'ownership'):
            build_site(SOURCE, unrelated)
        self.assertEqual('preserve', (unrelated / 'keep.txt').read_text())
        with self.assertRaises(ValueError):
            build_site(SOURCE, SOURCE)

    def test_missing_translation_blocks_generation(self):
        source = self.source
        data = json.loads((source / 'content/ui.json').read_text())
        del data['uk']['terms']
        (source / 'content/ui.json').write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'translation'):
            build_site(source, Path(self.temp.name) / 'incomplete')

    def test_original_privacy_versions_are_preserved_byte_for_byte_in_source(self):
        manifest = json.loads((SOURCE / 'content/archive/manifest.json').read_text())
        for path, expected in manifest.items():
            self.assertEqual(expected, hashlib.sha256((SOURCE / path).read_bytes()).hexdigest())
        for lang in ('en', 'uk', 'ru'):
            current = (SOURCE / f'content/{lang}/privacy.html').read_text()
            original = (SOURCE / f'content/archive/2026-11-08/{lang}/privacy.html').read_text()
            self.assertEqual(original.count('<h2>'), current.count('<h2>'))
            for endpoint in ('bank.gov.ua', 'api.frankfurter', 'support@inwestman.uk'):
                self.assertIn(endpoint, current)


if __name__ == '__main__':
    unittest.main()
