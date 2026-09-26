"""Workshop measurement metadata; visualization never implies fabrication approval."""
import json
from pathlib import Path

FILENAME = 'model-facts.json'


def export_for_path(path):
    path = Path(path).resolve()
    return path if (path / FILENAME).is_file() else None


def is_publishable(path):
    from workshop_models import discover
    return Path(path).resolve() in {output.resolve() for _, output in discover()}


def preferred_assembly(export, product):
    return None


def read_model_metadata(path):
    owner = export_for_path(path)
    return (owner, json.loads((owner / FILENAME).read_text())) if owner else (None, None)


def write_model_metadata(path, facts):
    path.mkdir(parents=True, exist_ok=True)
    destination = path / FILENAME
    temporary = destination.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(facts, indent=2) + '\n')
    temporary.replace(destination)
    return destination
