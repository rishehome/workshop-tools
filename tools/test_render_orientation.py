import argparse
import json
from pathlib import Path
import tempfile
import unittest
from render_orientation import AXES, add_orientation_arguments, resolve_orientation, face_vectors


class OrientationTests(unittest.TestCase):
    def test_defaults_all_formats(self):
        with tempfile.TemporaryDirectory() as folder:
            for extension in ("step", "stp", "stl", "FCStd", "obj"):
                faces = face_vectors(resolve_orientation(Path(folder) / ("model." + extension)))
                self.assertEqual(faces["top"], (0, 0, 1))
                self.assertEqual(faces["front"], (0, -1, 0))
                self.assertEqual(faces["right"], (1, 0, 0))

    def test_all_24_frames_and_parallel_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "object.step"
            for top in AXES:
                for front in AXES:
                    if top[-1] == front[-1]:
                        with self.assertRaises(ValueError):
                            resolve_orientation(source, top, front)
                    else:
                        faces = face_vectors(resolve_orientation(source, top, front))
                        self.assertEqual(len(set(faces.values())), 6)
                        self.assertEqual(sum(v*v for v in faces["right"]), 1)
                        for a, b in (("top", "bottom"), ("front", "back"), ("right", "left")):
                            self.assertEqual(faces[a], tuple(-v for v in faces[b]))

    def test_saved_settings_overrides_and_invalid_config(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "object.step"
            config = source.with_name(source.name + ".render.json")
            config.write_text(json.dumps({"top": "+y", "front": "+z"}))
            self.assertEqual(resolve_orientation(source), {"top": "+Y", "front": "+Z"})
            self.assertEqual(resolve_orientation(source, "-X")["top"], "-X")
            for bad in ('[]', '{', '{"up":"+Z"}', '{"top":null}', '{"front":"+Z"}'):
                config.write_text(bad)
                with self.assertRaises(ValueError):
                    resolve_orientation(source)

    def test_negative_cli_axis(self):
        cli = argparse.ArgumentParser()
        add_orientation_arguments(cli)
        args = cli.parse_args(["--top-axis=-z", "--front-axis=+y"])
        self.assertEqual((args.top_axis, args.front_axis), ("-Z", "+Y"))

    def test_model_facts_precedence_and_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder)
            source = model / 'body.step'
            facts = model / 'model-facts.json'
            facts.write_text(json.dumps({'orientation': {'top': '+Y', 'front': '+Z'}}))
            self.assertEqual(resolve_orientation(source, model_dir=model), {'top': '+Y', 'front': '+Z'})
            source.with_name(source.name + '.render.json').write_text('{"top":"-X"}')
            self.assertEqual(resolve_orientation(source, model_dir=model), {'top': '-X', 'front': '+Z'})
            self.assertEqual(resolve_orientation(source, '+Y', model_dir=model)['top'], '+Y')
            facts.write_text('{"orientation": []}')
            with self.assertRaisesRegex(ValueError, 'orientation'):
                resolve_orientation(source, model_dir=model)

    def test_measurement_regeneration_preserves_orientation(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        from generate_overview_info import generate
        from export_metadata import read_model_metadata
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder)
            source = model / 'body.step'
            source.write_text('test geometry')
            (model / 'model-facts.json').write_text(json.dumps({
                'orientation': {'top': '+Y', 'front': '+Z'},
                'bounds_mm': {'x': 999, 'y': 999, 'z': 999}}))
            def measure(command, **kwargs):
                Path(command[-1]).write_text('{"bounds_mm":{"x":10,"y":20,"z":30}}')
                return SimpleNamespace(returncode=0)
            with patch('generate_overview_info.subprocess.run', side_effect=measure):
                generate(model, source)
            _, facts = read_model_metadata(model)
            self.assertEqual(facts['orientation'], {'top': '+Y', 'front': '+Z'})
            self.assertEqual(facts['bounds_mm']['x'], 10)
            self.assertEqual(resolve_orientation(source, model_dir=model), facts['orientation'])
