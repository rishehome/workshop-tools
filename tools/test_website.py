"""Check the generated site's navigation and downloadable CAD packages."""
import unittest
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.images = []
        self.lang = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == 'img':
            self.images.append(attrs)


class WebsiteTests(unittest.TestCase):
    def test_all_local_links_assets_and_fragments_resolve(self):
        pages = sorted(SITE.rglob('*.html'))
        self.assertGreater(len(pages), 1, 'Build the site before testing')
        for path in pages:
            page = Page(path.read_text())
            self.assertEqual(page.lang, 'en')
            for image in page.images:
                self.assertIn('alt', image)
            for link in page.links:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                self.assertFalse(url.path.startswith('/'), 'Links must work under a GitHub project subpath')
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_relative_to(SITE), link)
                self.assertTrue(target.is_file(), f'{path.name}: {link}')
                if url.fragment:
                    self.assertIn(url.fragment, Page(target.read_text()).ids)

    def test_every_saved_object_and_published_export_is_available(self):
        sources = [p for p in ROOT.rglob('object.FCStd') if not any(part in {'.git', '_site', 'main', 'exports', 'CAM', '.venv', 'venv'} for part in p.relative_to(ROOT).parts[:-1])]
        self.assertEqual(len(sources), len(list((SITE / 'objects').glob('*.html'))))
        for source in sources:
            files = [source] + [p for p in (source.parent / 'exports').glob('*/*') if p.suffix.lower() in {'.step', '.stp', '.stl', '.obj', '.mtl'}]
            for original in files:
                copied = SITE / 'files' / original.relative_to(ROOT)
                self.assertEqual(original.read_bytes(), copied.read_bytes())
                self.assertTrue(any(str(copied.relative_to(SITE)) in p.read_text() for p in (SITE / 'objects').glob('*.html')))

    def test_zip_bundles_match_exports_and_keep_materials(self):
        archives = list((SITE / 'downloads').rglob('*.zip'))
        export_dirs = [p for p in ROOT.glob('**/exports/*') if p.is_dir() and '_site' not in p.parts]
        self.assertEqual(len(archives), len(export_dirs))
        for archive in archives:
            folder = next(p for p in export_dirs if p.name == archive.stem and p.parent.parent.relative_to(ROOT).as_posix().replace('/', '-') == archive.parent.name)
            with zipfile.ZipFile(archive) as bundle:
                self.assertIsNone(bundle.testzip())
                self.assertIn('object.obj', bundle.namelist())
                self.assertIn('object.mtl', bundle.namelist())
                for name in bundle.namelist():
                    self.assertEqual(bundle.read(name), (folder / name).read_bytes())

    def test_only_intended_public_files_are_in_output(self):
        self.assertTrue((SITE / '.nojekyll').exists())
        for path in SITE.rglob('*'):
            self.assertNotIn('.git', path.parts)
            self.assertNotEqual(path.suffix.lower(), '.fcbak')
            self.assertNotEqual(path.name, '.DS_Store')


if __name__ == '__main__':
    unittest.main()
