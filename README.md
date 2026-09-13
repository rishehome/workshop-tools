# Rishe CNC Workshop Tools

Free tool designs, jigs, fixtures, and workshop helpers created for practical CNC-workshop use. The designs are created with FreeCAD and shared so makers and small workshops can inspect, fabricate, and adapt them for permitted personal use.

## Designs

| Design | Description | Source | Exports |
| --- | --- | --- | --- |
| [Generic bit holder](bit-holder/generic/README.md) | General workshop bit-holder design | [FreeCAD source](bit-holder/generic/object.FCStd) | [STEP, STL, OBJ, MTL](bit-holder/generic/exports/var1-20mmd-with-numbers/) |
| [Shapeoko 5 bit holder](bit-holder/shapeoko-5/) | Separately maintained Shapeoko 5 variant; verify fit against your setup | [FreeCAD source](bit-holder/shapeoko-5/object.FCStd) | [STEP, STL, OBJ, MTL](bit-holder/shapeoko-5/exports/var1-20mmd-with-numbers/) |
| [Round-corner sanding tools](sanding/round-corner-sanding-tools/) | Sanding-tool variants for shaped corners | [FreeCAD source](sanding/round-corner-sanding-tools/object.FCStd) | [4.75 mm corner, 10 mm half-round, 5 mm corner, 3 mm corner](sanding/round-corner-sanding-tools/exports/) |

Start with the design guide where available. The generic bit holder and sanding
tools have guides; the Shapeoko 5 directory currently contains the source and
exports without a dedicated README. Variant names identify the files, not a
verified specification or fit guarantee.

## Quick start

1. Choose a design above and read its guide where available, such as the [generic bit-holder guide](bit-holder/generic/README.md).
2. Download the `.FCStd` source if you need to inspect the FreeCAD model, or choose an exported format for your CAD/CAM workflow.
3. Verify scale, units, dimensions, fit, clearances, and material suitability in your own setup.
4. Manufacture or print only after completing your own safety and process checks.

The files are reference designs. They are not certified tooling, safety equipment, or a substitute for checking a machine, workholding setup, or material-specific process.

## Number the bit-holder sections in FreeCAD

The separate `freecad-tools` repository contains **Number selected faces**, a
standalone macro for engraving consecutive numbers into flat label areas.
If both repositories are checked out beside one another, open the
[macro guide](../freecad-tools/macros/README.md) or
[NumberSelectedFaces.FCMacro](../freecad-tools/macros/NumberSelectedFaces.FCMacro)
directly. These sibling links require that local checkout layout; the macro is
not bundled with this repository.

1. Open the desired bit-holder `.FCStd` source. Select the flat label faces on
   one object in the exact numbering order, using Ctrl-click or Cmd-click as
   configured in FreeCAD. Select the label surfaces, not the curved hole walls.
2. For **1–24**, select 24 faces and leave **First number** at `1`. For a
   four-column layout, select left to right across a row, then continue to the
   next row. The macro uses selection order; it does not detect rows.
3. Open the macro with **File → Open**, then run **Macro → Execute** (**F6**).
   Opening the file alone does not execute it.
4. Choose a TTF/OTF outline font, text height, pocket depth, and rotation.
   Defaults are **3 mm** height and **0.5 mm** depth; adjust them to the actual
   label area and remaining material. Use the dialog's **Help** button for details.
5. Click **OK**, inspect the new engraved solid, and save the document. Export
   only the new result when preparing STEP or STL files.

**Text rotation** accepts **−360° to +360°** for all selected labels. Viewed
straight at the face from outside the solid, `90` turns counterclockwise and
`-90` turns clockwise; `180` turns the text upside down relative to its default
orientation. Rotation follows the face plane, not the camera.

The macro centers each number and rejects text that does not fit or cuts that
cannot reach the requested depth. Two-digit numbers are wider; reduce the height
if needed. Depth starts at each selected surface, including recessed label faces.

The result is a **separate static solid** and the original is hidden, not deleted.
It does not update automatically when the source or recorded settings change.
Use **Edit → Undo**, reselect the original faces, and rerun to adjust it. The
macro creates CAD geometry, not CAM operations or G-code. Existing exports are
not regenerated automatically; export the intended result after editing.

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
├── bit-holder/
│   ├── generic/
│   │   ├── README.md
│   │   ├── object.FCStd    # Generic bit-holder source
│   │   └── exports/        # STEP, STL, OBJ and MTL by variant
│   └── shapeoko-5/
│       ├── object.FCStd    # Shapeoko 5 variant source
│       └── exports/        # STEP, STL, OBJ and MTL by variant
└── sanding/
    └── round-corner-sanding-tools/
        ├── README.md
        ├── object.FCStd    # FreeCAD source
        └── exports/        # Published interchange formats
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
