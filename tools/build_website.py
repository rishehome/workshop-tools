#!/usr/bin/env python3
"""Build a self-contained English GitHub Pages site using only the standard library."""
import argparse
import html
import json
import shutil
import zipfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
FORMATS = {'.step': 'STEP', '.stp': 'STEP', '.stl': 'STL', '.obj': 'OBJ', '.mtl': 'MTL'}
FORMAT_ORDER = {name: index for index, name in enumerate(FORMATS)}


def esc(value):
    return html.escape(str(value), quote=True)


def build(output):
    output = output.resolve()
    # Only replace the known generated directory; never erase arbitrary paths.
    if output != ROOT / '_site':
        raise ValueError('Output must be the repository _site directory')
    if output.is_symlink():
        raise ValueError('Output must not be a symlink')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    shutil.copytree(ROOT / 'website/assets', output / 'assets')
    (output / '.nojekyll').touch()
    shutil.copy2(ROOT / 'LICENSE.md', output / 'LICENSE.md')
    catalog = json.loads((ROOT / 'website/catalog.json').read_text())
    models = []

    def publish(path):
        relative = path.relative_to(ROOT)
        destination = output / 'files' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        return 'files/' + quote(relative.as_posix())

    for source in sorted(ROOT.rglob('object.FCStd')):
        parts = source.relative_to(ROOT).parts
        if any(p in {'.git', '_site', 'main', 'exports', 'CAM', '.venv', 'venv'} for p in parts[:-1]):
            continue
        key = source.parent.relative_to(ROOT).as_posix()
        info = catalog.get(key, {})
        name = info.get('name', source.parent.name.replace('-', ' ').capitalize())
        model = {'key': key, 'slug': key.replace('/', '-'), 'name': name,
                 'category': info.get('category', 'Workshop tools'),
                 'description': info.get('description', f'Explore the {name.lower()} design and download the available files.'),
                 'note': info.get('note', 'Inspect scale, fit and clearances before fabrication.'),
                 'source': publish(source), 'variants': []}
        folders = sorted(p for p in (source.parent / 'exports').glob('*') if p.is_dir())
        for folder in folders or [source.parent / 'main/object']:
            files = sorted((p for p in folder.glob('*') if p.is_file() and p.suffix.lower() in FORMATS),
                           key=lambda p: (FORMAT_ORDER[p.suffix.lower()], p.name))
            images = []
            for view in ['three-quarter', 'front', 'side', 'top', 'back']:
                path = folder / f'renders/solid-{view}.png'
                if path.exists():
                    images.append((view.replace('-', ' ').capitalize(), publish(path)))
            overview = folder / 'overview/product-overview.png'
            facts = folder / 'model-facts.json'
            variant = {'name': info.get('variants', {}).get(folder.name, folder.name.replace('-', ' ') if files else 'Saved design'),
                       'files': [(FORMATS[p.suffix.lower()], publish(p)) for p in files], 'images': images,
                       'overview': publish(overview) if overview.exists() else None,
                       'dimensions': json.loads(facts.read_text()).get('dimensions') if facts.exists() else None}
            if files:
                archive = output / 'downloads' / model['slug'] / (folder.name + '.zip')
                archive.parent.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
                    for path in files:
                        bundle.write(path, path.name)
                variant['archive'] = archive.relative_to(output).as_posix()
            model['variants'].append(variant)
        model['image'] = next((v['images'][0][1] for v in model['variants'] if v['images']), None)
        if not model['image']:
            diagram = source.parent / 'resources/diagram.png'
            model['image'] = publish(diagram) if diagram.exists() else None
        models.append(model)

    def shell(title, description, content, prefix=''):
        return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Rishe Workshop</title><meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#2a3d39"><meta property="og:title" content="{esc(title)} | Rishe Workshop"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website">
<link rel="icon" href="{prefix}assets/logo.svg" type="image/svg+xml"><link rel="preload" href="{prefix}assets/manrope-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/theme.js"></script></head>
<body><a class="skip" href="#main">Skip to content</a><header><div class="editorial-container header-inner">
<a class="brand" href="{prefix}index.html"><img src="{prefix}assets/logo.svg" width="26" height="36" alt=""><span>rishe<span class="brand-label">WORKSHOP</span></span></a>
<nav aria-label="Main navigation"><a href="{prefix}index.html#collection">Objects</a><a href="{prefix}index.html#using">Using the files</a><a href="https://github.com/rishehome/workshop-tools">GitHub ↗</a></nav>
<div class="themes" role="group" aria-label="Color theme" hidden><button data-theme="auto" aria-pressed="true">Auto</button><button data-theme="light" aria-pressed="false">Light</button><button data-theme="dark" aria-pressed="false">Dark</button></div></div></header>
<main id="main">{content}</main><footer><div class="editorial-container footer-inner"><div><span class="footer-brand">Rishe / Workshop</span><p>Practical objects. Shared with care.</p></div><div><a href="{prefix}LICENSE.md">CC BY-NC-ND 4.0 license</a><a href="https://github.com/rishehome/workshop-tools">Source repository ↗</a><a href="mailto:info@rishehome.com">Commercial licensing</a></div></div></footer></body></html>'''

    cards = []
    for model in models:
        image = f'<img src="{model["image"]}" alt="{esc(model["name"])}" loading="lazy" width="1200" height="800">' if model['image'] else '<span class="placeholder">FreeCAD source available</span>'
        count = sum(bool(v['files']) for v in model['variants'])
        status = f'{count} export variant' + ('s' if count != 1 else '') if count else 'FreeCAD source · Exports pending'
        cards.append(f'''<article class="editorial-card"><a class="card-link" href="objects/{model['slug']}.html"><div class="card-media">{image}</div><div class="card-copy"><p class="section-kicker">{esc(model['category'])}</p><h3>{esc(model['name'])}</h3><p>{esc(model['description'])}</p><div class="card-end"><span>{status}</span><span>Explore →</span></div></div></a></article>''')
        variants = []
        for variant in model['variants']:
            downloads = ''.join(f'<a class="button secondary" href="../{url}" download>Download {label}</a>' for label, url in variant['files'])
            if variant['files']:
                downloads = f'<a class="button" href="../{variant["archive"]}" download>Download all exports · ZIP ↓</a>' + downloads
            else:
                downloads = '<p class="status">No published interchange exports yet. The FreeCAD source is available above.</p>'
            dimensions = ''
            if variant['dimensions']:
                d = variant['dimensions']
                dimensions = '<dl class="dimensions">' + ''.join(f'<div><dt>{axis.capitalize()}</dt><dd>{esc(d[axis])} {esc(d["unit"])}</dd></div>' for axis in ['width', 'height', 'depth']) + '</dl><p class="small">Approximate CAD body extents; these are not fit specifications.</p>'
            gallery = ''.join(f'<a class="view" href="../{url}"><img src="../{url}" alt="{esc(model["name"])} — {esc(view.lower())} view" loading="lazy" width="1200" height="800"><span>{esc(view)}</span></a>' for view, url in variant['images'])
            overview = f'<a class="text-link" href="../{variant["overview"]}">Open product overview ↗</a>' if variant['overview'] else ''
            variants.append(f'<section class="variant editorial-card"><p class="section-kicker">{ "Published exports" if variant["files"] else "Source design" }</p><h2>{esc(variant["name"])}</h2>{dimensions}<div class="downloads">{downloads}</div>{"<p class=small>Keep OBJ and MTL together when importing. The ZIP includes both.</p>" if variant["files"] else ""}{"<div class=gallery>" + gallery + "</div>" if gallery else ""}{overview}</section>')
        hero_image = f'<div class="detail-image"><img src="../{model["image"]}" alt="{esc(model["name"])}" width="1200" height="800"></div>' if model['image'] else ''
        content = f'''<div class="editorial-container"><a class="back" href="../index.html#collection">← All objects</a><section class="detail-hero"><div><p class="section-kicker">{esc(model['category'])}</p><h1>{esc(model['name'])}</h1><p class="section-body">{esc(model['description'])}</p><a class="button" href="../{model['source']}" download>Download FreeCAD source ↓</a><p class="small">Editable .FCStd model · Source may contain newer changes than published exports.</p></div>{hero_image}</section><div class="variants">{''.join(variants)}</div><section class="before"><p class="section-kicker">Before fabrication</p><h2>Make it work for your workshop.</h2><p>{esc(model['note'])}</p><p>Verify scale, units, material suitability and geometry in your CAD/CAM software. Gray renders are illustrative; material and manufacturing process are not specified.</p><a class="text-link" href="../index.html#using">Read the file and license guide →</a></section></div>'''
        page = output / 'objects' / (model['slug'] + '.html')
        page.parent.mkdir(exist_ok=True)
        page.write_text(shell(model['name'], model['description'], content, '../'))
    first = models[0]
    content = f'''<div class="editorial-container"><section class="hero"><div><p class="section-kicker">RISHE / OPEN WORKSHOP</p><h1>A little order.<br>A better workshop.</h1><p class="section-body">Useful tools, jigs and fixtures from our workshop. Explore the objects, inspect the designs, and download the files for your own setup.</p><a class="button" href="#collection">Explore the objects ↓</a><p class="hero-note">Designed in FreeCAD. Shared for non-commercial use.</p></div><a class="hero-media" href="objects/{first['slug']}.html"><img src="{first['image']}" alt="Generic numbered bit holder CAD preview" width="1200" height="800"><span>01 / Generic bit holder <span>Explore →</span></span></a></section><section id="collection" class="collection"><div class="section-heading"><div><p class="section-kicker">The collection</p><h2>Practical tools for your workshop.</h2></div><p>{len(models):02d} designs / {sum(bool(v['files']) for m in models for v in m['variants']):02d} published variants</p></div><div class="object-grid">{''.join(cards)}</div></section><section id="using" class="using"><div><p class="section-kicker">From file to workshop</p><h2>Start with the right file.</h2><p>Inspect every model before fabrication. Check scale, units, fit, clearances and material suitability in your setup.</p></div><div><dl class="formats"><div><dt>FreeCAD / .FCStd</dt><dd>The editable source model, for inspecting and adapting the design.</dd></div><div><dt>STEP / .step</dt><dd>Solid geometry for compatible CAD and CAM workflows.</dd></div><div><dt>STL / .stl</dt><dd>A triangulated mesh for slicing and mesh workflows.</dd></div><div><dt>OBJ + MTL</dt><dd>Mesh and material reference. Keep both files together, or download the ZIP bundle.</dd></div></dl><p class="small">These reference designs are not certified tooling. Check the imported geometry before use.</p></div></section><section class="license"><p class="section-kicker">Shared with care</p><h2>For your own workshop.</h2><p>The original files are shared under CC BY-NC-ND 4.0. Non-commercial use and sharing require attribution. Commercial use and distribution of modified versions are not permitted by this license.</p><a class="button secondary" href="LICENSE.md">Read the license ↗</a><a class="text-link" href="mailto:info@rishehome.com">Ask about commercial licensing →</a></section></div>'''
    (output / 'index.html').write_text(shell('Workshop tools & free CAD downloads', 'Explore Rishe workshop tools, bit holders, sanding tools and CNC accessories. Download FreeCAD sources and published STEP, STL and OBJ exports.', content))
    print(f'Built {len(models)} object pages in {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    build(parser.parse_args().output)
