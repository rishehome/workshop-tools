import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from workshop_models import discover, select
from build_product_overview import read_config, select_image
from export_metadata import write_model_metadata


class WorkshopAssetsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def file(self, path, content=''):
        result = self.root / path
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(content)
        return result

    def test_exports_win_over_changed_cad_and_backups(self):
        self.file('tool/object.FCStd', 'newer design')
        self.file('tool/object.20260913.FCBak')
        step = self.file('tool/exports/v1/object.step')
        self.file('tool/exports/v1/object.stl')
        self.assertEqual(discover(self.root), [(step, step.parent)])

    def test_saved_cad_fallback_and_selection(self):
        cad = self.file('tool/object.FCStd')
        self.assertEqual(select(cad, self.root), [(cad, cad.parent / 'main/object')])
        with self.assertRaises(ValueError):
            select(self.root.parent, self.root)

    def test_generated_website_cad_copies_are_excluded(self):
        cad = self.file('tool/object.FCStd')
        self.file('_site/files/tool/object.FCStd')
        self.file('_site/files/tool/exports/v1/object.step')
        self.assertEqual(discover(self.root), [(cad, cad.parent / 'main/object')])

    def test_ambiguous_export_is_rejected(self):
        self.file('tool/object.FCStd')
        self.file('tool/exports/v1/a.step')
        self.file('tool/exports/v1/b.step')
        with self.assertRaises(ValueError):
            discover(self.root)

    def test_gray_views_and_photo_precedence(self):
        export = self.root / 'variant'
        for view in ('front', 'back', 'three-quarter'):
            self.file(f'variant/renders/solid-{view}.png')
        photo = self.file('variant/photos/solid-three-quarter.jpg')
        config = read_config(export)
        self.assertEqual(config['images']['hero'], 'solid-three-quarter')
        self.assertEqual(config['images']['alternate'], 'solid-front')
        self.assertEqual(select_image(export, 'solid-three-quarter'), (photo, True))
        with self.assertRaises(FileNotFoundError):
            select_image(export, 'missing')

    def test_stale_dimensions_are_rejected(self):
        source = self.file('variant/object.step', 'geometry')
        facts = {'source': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                 'dimensions': {'width': 12, 'height': 20, 'depth': 3, 'unit': 'mm'}}
        write_model_metadata(source.parent, facts)
        self.assertEqual(read_config(source.parent)['size_text'], '12 × 20 × 3 mm')
        source.write_text('updated geometry')
        with self.assertRaisesRegex(ValueError, 'Stale model facts'):
            read_config(source.parent)


if __name__ == '__main__':
    unittest.main()
