#!/usr/bin/env python3
"""Run with a FreeCAD-capable Python to tessellate STEP or a saved FreeCAD design into a temporary STL."""
import argparse
import json
from pathlib import Path
import sys


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('source', type=Path)
    cli.add_argument('output', type=Path)
    args = cli.parse_args()
    # The macOS FreeCAD bundle keeps extension modules outside site-packages.
    library = Path(sys.executable).resolve().parent.parent / 'lib'
    if library.is_dir():
        sys.path.insert(0, str(library))
    import FreeCAD
    import Part
    import MeshPart

    names = []
    if args.source.suffix.lower() == '.fcstd':
        from cad_selection import design_bodies
        names = design_bodies(args.source)
        if not names:
            raise ValueError(f'No solid design bodies: {args.source}')
        doc = FreeCAD.openDocument(str(args.source))
        shapes = [doc.getObject(name).Shape for name in names]
        if any(shape.isNull() or not shape.Solids for shape in shapes):
            raise ValueError(f'Selected bodies contain no saved solids: {names}')
        shape = Part.makeCompound(shapes)
        print(f'Saved FreeCAD bodies: {names}', flush=True)
    else:
        shape = Part.Shape()
        shape.read(str(args.source))
    if shape.isNull() or not shape.Faces:
        raise ValueError(f'Empty CAD shape: {args.source}')
    valid = shape.isValid()
    if not valid:
        print(f'Warning: saved CAD shape is invalid; rendering stored faces without repair: {args.source}', flush=True)
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.1,
                                 AngularDeflection=0.2, Relative=False)
    if not mesh.CountFacets:
        raise ValueError(f'Tessellation produced no triangles: {args.source}')
    mesh.write(str(args.output))
    args.output.with_suffix('.json').write_text(json.dumps({'valid': valid, 'objects': names}))
    print(f'Tessellated {args.source.name}: {mesh.CountFacets} triangles; {shape.BoundBox}')


if __name__ == '__main__':
    main()
