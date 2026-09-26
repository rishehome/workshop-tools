#!/usr/bin/env python3
"""Generate model dimensions and provenance inside model-facts.json."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from export_metadata import export_for_path, is_publishable, preferred_assembly, write_model_metadata

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', 'venv', '.venv', 'node_modules', '__pycache__', 'overview', 'photos', 'renders', 'CAM'}


def catalogue_models():
    from workshop_models import discover
    return {output.resolve(): source.resolve() for source, output in discover(ROOT)}


def discover_exports(root, photos_dir='photos'):
    registered = catalogue_models()
    root = root.resolve()
    selected = sorted(path for path in registered
                      if path == root or root in path.parents)
    if selected:
        return selected
    result = []
    for directory, folders, _ in os.walk(root):
        if 'renders' in folders or photos_dir in folders:
            candidate = Path(directory)
            if not candidate.resolve().is_relative_to(ROOT.resolve()) or is_publishable(candidate):
                result.append(candidate)
        folders[:] = sorted(f for f in folders if f not in SKIP and f != photos_dir)
    return sorted(result)


def find_source(export):
    registered = catalogue_models().get(export.resolve())
    if registered is not None:
        if registered.suffix.lower() in ('.step', '.stp', '.fcstd'):
            return registered
        raise ValueError(f'Registered source cannot provide reliable dimensions: {registered}')
    unit = export_for_path(export)
    if unit is not None:
        product = next((parent.parent for parent in unit.parents
                        if parent.name in ('exports', 'export')), None)
        assembly = preferred_assembly(unit, product) if product else None
        if assembly is not None:
            if assembly.suffix.lower() in ('.step', '.stp', '.fcstd'):
                return assembly
            raise ValueError(f'Assembly source cannot provide reliable dimensions: {assembly}')
    # Prefer exported geometry, never infer a product-root model for a variant.
    for folder in (export / 'objects', export):
        candidates = sorted(p for p in folder.glob('*') if p.is_file()
                            and p.suffix.lower() in ('.step', '.stp'))
        if len(candidates) == 1:
            return candidates[0]
        if candidates:
            raise ValueError(f'Multiple STEP files in {folder}; specify --source')
    candidates = sorted(p for p in export.glob('*') if p.suffix.lower() == '.fcstd'
                        and 'cam' not in p.stem.lower())
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError(f'No unambiguous STEP/FreeCAD design in {export}; specify --source')


def generate(export, source=None, axes='xyz', unit='mm', decimals=1, freecad_python=None):
    source = source.resolve() if source else find_source(export)
    if not source.is_file() or source.suffix.lower() not in ('.step', '.stp', '.fcstd'):
        raise ValueError(f'Expected an existing STEP, STP or FCStd source: {source}')
    owner = export_for_path(export) or export.resolve()
    runtime = freecad_python or os.environ.get('FREECAD_PYTHON')
    if not runtime:
        bundled = Path('/Applications/FreeCAD.app/Contents/Resources/bin/python')
        runtime = str(bundled) if bundled.is_file() else sys.executable
    with tempfile.TemporaryDirectory(prefix='rishe-overview-') as tmp:
        measured = Path(tmp) / 'measurements.json'
        result = subprocess.run([runtime, str(Path(__file__).with_name('measure_overview_model.py')),
                                 str(source), str(measured)], capture_output=True, text=True)
        if result.returncode:
            raise ValueError(f'FreeCAD measurement failed for {source}:\n{result.stderr[-1800:]}')
        facts = json.loads(measured.read_text())
    divisor = {'mm': 1, 'cm': 10, 'in': 25.4}[unit]
    dimensions = {key: facts['bounds_mm'][axis] / divisor
                  for key, axis in zip(('width', 'height', 'depth'), axes)}
    if any(value <= 0 for value in dimensions.values()):
        raise ValueError('Model has nonpositive extent')
    relative_source = os.path.relpath(source, owner)
    dimensions.update(unit=unit, decimals=decimals, note='Approx. · CAD body dimensions', source=relative_source)
    data = {'source': relative_source,
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'axes': axes, 'dimensions': dimensions, **facts}
    return write_model_metadata(export, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path, help='One export, or a root directory with --batch')
    parser.add_argument('--batch', action='store_true', help='Find exports with renders/ or photos/ recursively')
    parser.add_argument('--source', type=Path, help='Explicit STEP/STP/FCStd source (single export only)')
    parser.add_argument('--axes', choices=('xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'), default='xyz', help='CAD axes for width,height,depth; default xyz')
    parser.add_argument('--unit', choices=('mm', 'cm', 'in'), default='mm')
    parser.add_argument('--decimals', type=int, choices=range(4), default=1, help='Displayed precision; raw values retained')
    parser.add_argument('--freecad-python', help='Python executable with FreeCAD/Part; overrides FREECAD_PYTHON')
    parser.add_argument('--photos-dir', default='photos', help='Photo sibling folder for batch discovery')
    parser.add_argument('--dry-run', action='store_true', help='List selected sources without measuring or writing')
    args = parser.parse_args()
    if Path(args.photos_dir).name != args.photos_dir or args.photos_dir in ('.', '..', 'renders'):
        parser.error('--photos-dir must be a sibling folder name other than renders')
    root = args.path.resolve()
    if not root.is_dir():
        parser.error(f'Directory does not exist: {root}')
    if args.batch and args.source:
        parser.error('--source cannot be combined with --batch')
    exports = discover_exports(root, args.photos_dir) if args.batch else [root]
    if not exports:
        parser.error('No export directories found')
    if root.is_relative_to(ROOT.resolve()):
        invalid = [export for export in exports if not is_publishable(export)]
        if invalid:
            parser.error(f'Not a discovered workshop export or saved CAD fallback: {invalid[0]}')
    failed = 0
    for export in exports:
        try:
            source = args.source.resolve() if args.source else find_source(export)
            if args.dry_run:
                print(f'{export} <- {source}')
            else:
                print(generate(export, source, args.axes, args.unit, args.decimals, args.freecad_python))
        except (ValueError, OSError) as exc:
            failed += 1
            print(f'ERROR: {exc}', file=sys.stderr)
    print(f'{len(exports) - failed} succeeded; {failed} failed')
    raise SystemExit(1 if failed else 0)


if __name__ == '__main__':
    main()
