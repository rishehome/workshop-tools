# Rishe CNC Workshop Tools

Free tool designs, jigs, fixtures, and workshop helpers created for practical CNC-workshop use. The designs are created with FreeCAD and shared so makers and small workshops can inspect, fabricate, and adapt them for permitted personal use.

## Designs

| Design | Description | Source | Exports |
| --- | --- | --- | --- |
| [Bit holder](bit-holder/) | Workshop bit-holder design | [FreeCAD source](bit-holder/object.FCStd) | [STEP, STL, OBJ, MTL](bit-holder/exports/var1-20mmd-with-numbers/) |

Each design directory contains a short guide describing its files and known assumptions. Use that guide as the starting point before opening or fabricating a model.

## Quick start

1. Open the design-specific README, such as [`bit-holder/README.md`](bit-holder/README.md).
2. Download the `.FCStd` source if you need to inspect the FreeCAD model, or choose an exported format for your CAD/CAM workflow.
3. Verify scale, units, dimensions, fit, clearances, and material suitability in your own setup.
4. Manufacture or print only after completing your own safety and process checks.

The files are reference designs. They are not certified tooling, safety equipment, or a substitute for checking a machine, workholding setup, or material-specific process.

## File formats

- `.FCStd`: editable FreeCAD source model.
- `.FCBak`: FreeCAD backup file; normally not the primary file to distribute or edit.
- `.step`: neutral CAD exchange format for solid-model workflows.
- `.stl`: triangulated mesh format, commonly used for slicing and mesh-based workflows.
- `.obj` and `.mtl`: mesh and material-reference files used together by compatible applications.

Exported files may not preserve the parametric structure of the FreeCAD source. Check the imported model before production use.

## Repository structure

```text
.
├── README.md
├── LICENSE.md
├── assets/                 # Shared project assets
└── bit-holder/
    ├── README.md
    ├── object.FCStd        # FreeCAD source
    └── exports/            # Published interchange formats
```

For repository and export conventions, see [`CONTRIBUTING.md`](CONTRIBUTING.md). Future designs should use [`docs/design-documentation-template.md`](docs/design-documentation-template.md) as their starting point.

## License

These designs are released under the [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International license](LICENSE.md).

You may download, use, and share the original files for permitted non-commercial purposes with attribution. The license does not permit commercial use or distribution of modified versions. Read [`LICENSE.md`](LICENSE.md) before using or sharing the files.

For commercial licensing inquiries, contact info@rishehome.com or open an issue in this repository.

## Contact

Open an issue in this repository for questions, corrections, or improvement proposals. Commercial licensing questions can be sent to info@rishehome.com.

Made with FreeCAD and ☕ by **Rishe**

If you find these designs useful, you can [support us with a coffee](https://buymeacoffee.com/rishe).
