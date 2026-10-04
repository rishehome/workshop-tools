"""Discover published STEP variants, falling back to saved CAD without exports."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def discover(root=ROOT):
    models = []
    for project in sorted(root.rglob('object.FCStd')):
        if any(part in {'.git', '_site', 'venv', '.venv', 'main', 'exports', 'CAM'} for part in project.relative_to(root).parts[:-1]):
            continue
        exports = project.parent / 'exports'
        if exports.is_dir():
            variants = sorted(p for p in exports.iterdir() if p.is_dir())
            for variant in variants:
                sources = sorted(p for p in variant.iterdir() if p.suffix.lower() in {'.step', '.stp'})
                if len(sources) != 1:
                    raise ValueError(f'Expected one STEP source in {variant}, found {len(sources)}')
                models.append((sources[0], variant))
            if variants:
                continue
        models.append((project, project.parent / 'main' / 'object'))
    return models


def select(path, root=ROOT):
    target = path.resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f'Path outside repository: {path}')
    return [(source, output) for source, output in discover(root)
            if target in (source.resolve(), output.resolve())
            or target in source.resolve().parents or target in output.resolve().parents]
