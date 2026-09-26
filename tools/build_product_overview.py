#!/usr/bin/env python3
"""Render a product export as a branded PNG overview."""
import argparse
import base64
import copy
import hashlib
import sys
import json
import mimetypes
import tempfile
from pathlib import Path
from export_metadata import read_model_metadata

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / 'design-templates/product-overview'
EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')
FORMATS = {'landscape': (1536, 1024), 'story': (1080, 1920)}


def select_image(export, stem, photos_dir='photos'):
    """Prefer photographs per slot, regardless of extension; never cross exports."""
    if not stem or Path(stem).name != stem:
        raise ValueError('Image names must be plain filenames or stems')
    stem = Path(stem).stem if Path(stem).suffix.lower() in EXTENSIONS else stem
    for folder in (photos_dir, 'renders'):
        directory = export / folder
        candidates = sorted(directory.iterdir()) if directory.is_dir() else []
        for extension in EXTENSIONS:
            for path in candidates:
                if path.is_file() and path.stem == stem and path.suffix.lower() == extension:
                    return path, folder != 'renders'
    raise FileNotFoundError(f'No image for {stem!r} in {export / photos_dir} or {export / "renders"}')


def data_uri(path):
    mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def provenance_path(path):
    """Use repository-relative paths in committed provenance when possible."""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def read_config(export, photos_dir="photos"):
    product = next((p for p in (export, *export.parents) if (p / 'info.json').is_file()), None)
    info = json.loads((product / 'info.json').read_text()) if product else {}
    name = info.get('name', export.name)
    if isinstance(name, dict):
        name = name.get('latin') or next(iter(name.values()))
    config = {'name': name, 'category': 'Workshop tool', 'feature_title': 'The details.',
              'feature_text': '', 'feature_note': '', 'caption': '', 'dimensions': None,
              'alternate_title': 'Another perspective', 'collection': 'RISHE / WORKSHOP',
              'images': {'hero': 'solid-three-quarter', 'detail': 'solid-front', 'alternate': 'solid-front'}}
    available = sorted({p.stem for folder in (photos_dir, 'renders')
                        for p in (export / folder).glob('*')
                        if p.is_file() and p.suffix.lower() in EXTENSIONS})
    preferences = {'hero': ('solid-three-quarter', 'solid-front'),
                   'detail': ('solid-front', 'solid-three-quarter'),
                   'alternate': ('solid-front', 'solid-back')}
    for slot, choices in preferences.items():
        config['images'][slot] = next((stem for stem in choices if stem in available),
                                     available[0] if available else config['images'][slot])
    metadata_root, facts = read_model_metadata(export)
    if facts:
        source = metadata_root / facts['source']
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != facts['source_sha256']:
            raise ValueError(f'Stale model facts in {metadata_root / "model-facts.json"}; rerun with --generate-info')
        config['dimensions'] = facts['dimensions']
    # Optional product defaults, followed by export-specific overrides.
    paths = ([product / 'overview.json'] if product and product != export else []) + [export / 'overview.json']
    for path in paths:
        if path.is_file():
            overrides = json.loads(path.read_text())
            config['images'].update(overrides.pop('images', {}))
            config.update(overrides)
    crop = {'scale': 2.5, 'x': 55, 'y': 55}
    crop.update(config.get('detail_crop', {}))
    for key, lower, upper in (('scale', 1, 5), ('x', 0, 100), ('y', 0, 100)):
        value = crop[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not lower <= value <= upper:
            raise ValueError(f'detail_crop.{key} must be between {lower} and {upper}')
    config['detail_crop'] = crop
    dimensions = config.get('dimensions')
    if dimensions:
        for key in ('width', 'height', 'depth'):
            value = dimensions.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value < float('inf'):
                raise ValueError(f'dimensions.{key} must be a positive finite number')
        if dimensions.get('unit') not in ('mm', 'cm', 'in'):
            raise ValueError('dimensions.unit must be mm, cm, or in')
        decimals = dimensions.get('decimals')
        if decimals is not None and (type(decimals) is not int or not 0 <= decimals <= 3):
            raise ValueError('dimensions.decimals must be an integer from 0 to 3')
        spec = f'.{decimals}f' if decimals is not None else 'g'
        config['size_text'] = ' × '.join(format(dimensions[k], spec) for k in ('width', 'height', 'depth')) + ' ' + dimensions['unit']
    return config


def build(export, args):
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
    config = read_config(export, args.photos_dir)
    sources = {}
    source_paths = {}
    images = {}
    for slot in ('hero', 'detail', 'alternate'):
        path, photograph = select_image(export, config['images'][slot], args.photos_dir)
        images[slot] = {'uri': data_uri(path), 'photograph': photograph}
        source_paths[slot] = path
        sources[slot] = {'path': provenance_path(path), 'type': 'photo' if photograph else 'render'}
    count = sum(image['photograph'] for image in images.values())
    config['status'] = ('Product photography' if count == 3 else 'Photos & render previews' if count else 'Render preview')
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True, undefined=StrictUndefined)
    width, height = FORMATS[args.format]
    html = env.get_template('overview.html.j2').render(product=config, images=images,
        font=data_uri(TEMPLATE_DIR / 'fonts/manrope-latin.woff2'), layout=args.format)
    output = args.output.resolve() if args.output else export / 'overview'
    if args.format == 'story':
        output = output / 'story'
    output.mkdir(parents=True, exist_ok=True)
    # HTML is an internal rendering implementation detail. Remove output from
    # older generator versions and render the page directly in memory.
    html_path = output / 'product-overview.html'
    html_path.unlink(missing_ok=True)
    (output / 'sources.json').write_text(json.dumps({'export': provenance_path(export), 'images': sources,
        'dimensions': config.get('dimensions'), 'config': config,
        'template_sha256': hashlib.sha256((TEMPLATE_DIR / 'overview.html.j2').read_bytes()).hexdigest(),
        'story_styles_sha256': hashlib.sha256((TEMPLATE_DIR / 'story.css.j2').read_bytes()).hexdigest(),
        'font_sha256': hashlib.sha256((TEMPLATE_DIR / 'fonts/manrope-latin.woff2').read_bytes()).hexdigest(),
        'image_sha256': {slot: hashlib.sha256(path.read_bytes()).hexdigest() for slot, path in source_paths.items()},
        'scale': args.scale, 'format': args.format, 'canvas': [width, height]}, indent=2) + '\n')
    from playwright.sync_api import sync_playwright
    with tempfile.TemporaryDirectory(prefix='rishe-overview-') as temporary:
        render_page = Path(temporary) / 'index.html'
        render_page.write_text(html, encoding='utf-8')
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=args.scale)
                page.goto(render_page.as_uri())
                page.evaluate('window.overviewReady')
                page.evaluate('document.fonts.ready')
                page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')
                overflow = page.locator('[data-fit]').evaluate_all('(els) => els.filter(e => e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1).map(e => ({text:e.textContent,width:e.clientWidth,scrollWidth:e.scrollWidth,height:e.clientHeight,scrollHeight:e.scrollHeight}))')
                if overflow:
                    raise ValueError(f'Text exceeds template space; shorten copy: {overflow}')
                clipped = page.locator('[data-fit]').evaluate_all('''(els) => els.filter(e => {
                    const card = e.closest('.card');
                    if (!card || !e.textContent.trim()) return false;
                    const r = e.getBoundingClientRect(), c = card.getBoundingClientRect();
                    return r.bottom > c.bottom + 1 || r.right > c.right + 1 || r.left < c.left - 1 || r.top < c.top - 1;
                }).map(e => e.textContent)''')
                if clipped:
                    raise ValueError(f'Text clipped by card; shorten copy: {clipped}')
                outside = page.locator('header, main, .card, footer').evaluate_all('(els) => els.filter(e => {const r=e.getBoundingClientRect(); return r.left < 0 || r.top < 0 || r.right > innerWidth + 1 || r.bottom > innerHeight + 1}).map(e => e.className || e.tagName)')
                if outside:
                    raise ValueError(f'Layout exceeds canvas: {outside}')
                page.screenshot(path=str(output / 'product-overview.png'))
            finally:
                browser.close()
    print(f'Created {output}')
    for slot, source in sources.items():
        print(f'  {slot}: {source["type"]} — {source["path"]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('export', type=Path, help='Export directory containing renders/ and optionally photos/')
    parser.add_argument('--format', choices=(*FORMATS, 'all'), default='all', help='Main landscape, Instagram Story, or both (default)')
    parser.add_argument('--batch', action='store_true', help='Recursively build every directory containing renders/ or photos/')
    parser.add_argument('--dry-run', action='store_true', help='List exports, selected images and metadata action without writing')
    parser.add_argument('--generate-info', action='store_true', help='Measure CAD and refresh model facts in model-facts.json before rendering')
    parser.add_argument('--source', type=Path, help='Explicit STEP/STP/FCStd for --generate-info; single export only')
    parser.add_argument('--axes', choices=('xyz','xzy','yxz','yzx','zxy','zyx'), help='CAD axes for width,height,depth; uses saved axes or xyz')
    parser.add_argument('--unit', choices=('mm','cm','in'), help='Generated dimension unit; uses saved unit or mm')
    parser.add_argument('--decimals', type=int, choices=range(4), help='Generated dimension precision; saved value or 1')
    parser.add_argument('--freecad-python', help='FreeCAD Python executable; overrides FREECAD_PYTHON')
    parser.add_argument('--photos-dir', default='photos', help='Sibling folder name (default: photos)')
    parser.add_argument('--output', type=Path, help='Default: EXPORT/overview/')
    parser.add_argument('--scale', type=int, choices=(1, 2, 3), default=2, help='Multiply preset dimensions; default 2; use 1 for native social sizes')
    args = parser.parse_args()
    if Path(args.photos_dir).name != args.photos_dir or args.photos_dir in ('.', '..', 'renders'):
        parser.error('--photos-dir must be a sibling folder name other than renders')
    export = args.export.resolve()
    if not export.is_dir():
        parser.error(f'Export directory does not exist: {export}')
    if args.batch and args.source:
        parser.error('--source cannot be combined with --batch')
    if not args.generate_info and any(v is not None for v in (args.source, args.axes, args.unit, args.decimals, args.freecad_python)):
        parser.error('CAD options require --generate-info')
    from generate_overview_info import discover_exports, find_source, generate
    from export_metadata import is_publishable
    exports = discover_exports(export, args.photos_dir) if args.batch else [export]
    if not exports:
        parser.error('No exports found')
    if export.is_relative_to(ROOT.resolve()):
        invalid = [item for item in exports if not is_publishable(item)]
        if invalid:
            parser.error(f'Not a discovered workshop export or saved CAD fallback: {invalid[0]}')
    failed = 0
    for item in exports:
        try:
            current_args = copy.copy(args)
            if args.batch and args.output:
                current_args.output = args.output.resolve() / item.relative_to(export)
            if args.dry_run:
                print(item)
                print(f'  formats: {args.format}; scale: {args.scale}')
                if args.generate_info:
                    try:
                        print(f'  measure: {args.source or find_source(item)}')
                    except ValueError as exc:
                        print(f'  measure: unavailable ({exc})')
                else:
                    config = read_config(item, args.photos_dir)
                    for slot, stem in config['images'].items():
                        print(f'  {slot}: {select_image(item, stem, args.photos_dir)[0]}')
                continue
            if args.generate_info:
                _, saved = read_model_metadata(item)
                saved = saved or {}
                dims = saved.get('dimensions', {})
                try:
                    generate(item, args.source, args.axes or saved.get('axes', 'xyz'),
                             args.unit or dims.get('unit', 'mm'),
                             args.decimals if args.decimals is not None else dims.get('decimals', 1),
                             args.freecad_python)
                except ValueError as exc:
                    if args.source or saved:
                        raise
                    print(f'WARNING [{item}]: dimensions skipped: {exc}', file=sys.stderr)
            for layout in (FORMATS if args.format == 'all' else [args.format]):
                current_args.format = layout
                build(item, current_args)
        except Exception as exc:
            failed += 1
            print(f'ERROR [{item}]: {exc}', file=sys.stderr)
    print(f'{len(exports) - failed} succeeded; {failed} failed')
    raise SystemExit(1 if failed else 0)


if __name__ == '__main__':
    main()
