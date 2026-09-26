#!/usr/bin/env python3
"""Internal FreeCAD worker; called by generate_overview_info.py."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    library = Path(sys.executable).resolve().parent.parent / 'lib'
    if library.is_dir():
        sys.path.insert(0, str(library))
    import FreeCAD
    import Part
    names = []
    document = None
    try:
        if args.source.suffix.lower() == '.fcstd':
            from cad_selection import design_bodies
            names = design_bodies(args.source)
            if not names:
                raise ValueError('No saved design bodies selected')
            document = FreeCAD.openDocument(str(args.source))
            shapes = [document.getObject(name).Shape for name in names]
            shape = Part.makeCompound(shapes)
        else:
            shape = Part.Shape()
            shape.read(str(args.source))
        if shape.isNull() or not shape.Solids or not shape.isValid():
            raise ValueError('Model must contain valid saved solid geometry')
        box = shape.BoundBox
        args.output.write_text(json.dumps({
            'bounds_mm': dict(zip('xyz', (box.XLength, box.YLength, box.ZLength))),
            'selected_bodies': names, 'solid_count': len(shape.Solids),
            'freecad_version': '.'.join(FreeCAD.Version()[:3]),
        }))
    finally:
        if document:
            FreeCAD.closeDocument(document.Name)


if __name__ == '__main__':
    main()
