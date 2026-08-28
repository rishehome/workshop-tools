# Round-corner sanding tools

This directory contains the FreeCAD source and published exports for hand tools intended to support sanding shaped corners. Four variants are included; their directory names identify the published corner or half-round size.

## Files

| Path | Purpose |
| --- | --- |
| [`object.FCStd`](object.FCStd) | Editable FreeCAD source model. |
| [`object.20260828-122322.FCBak`](object.20260828-122322.FCBak) | FreeCAD backup retained as a recovery copy, not the canonical source. |
| [`exports/var1-corner-4_75mm/`](exports/var1-corner-4_75mm/) | Export package for the 4.75 mm corner variant. |
| [`exports/var2-half-10mm/`](exports/var2-half-10mm/) | Export package for the 10 mm half-round variant. |
| [`exports/var3-corner-5mm/`](exports/var3-corner-5mm/) | Export package for the 5 mm corner variant. |
| [`exports/var4-corner-3mm/`](exports/var4-corner-3mm/) | Export package for the 3 mm corner variant. |

Every export package contains the following files:

| File | Purpose |
| --- | --- |
| `object.step` | Solid CAD exchange export. |
| `object.stl` | Mesh export. |
| `object.obj` | Mesh export. |
| `object.mtl` | Material reference associated with the OBJ export. |

## Before use

- Confirm the model opens correctly and is at the expected scale and unit system.
- Verify that the variant name and the resulting profile suit the workpiece corner being sanded.
- Check fit, clearance, orientation, sanding-media attachment, and grip in the actual setup.
- Select a material and manufacturing process appropriate to the intended use and loading.
- Perform a test fit or test piece before relying on a finished tool.

No authoritative dimensions, tolerances, material specification, sanding-media specification, or compatibility claim is currently recorded in this repository. Treat the variant names as identifiers and verify all geometry in FreeCAD or your CAD/CAM software before manufacturing.

## Choosing a file

Use the `.FCStd` file to inspect or edit the FreeCAD model. Use the STEP file for solid CAD/CAM workflows and the STL or OBJ files for mesh-based workflows. Keep the OBJ and MTL files together when importing the OBJ into software that uses material references.

## Revision notes

The source and exports currently have no formal release or revision metadata. When updating this design, record the change and regenerate the affected exports together with the source, following [`CONTRIBUTING.md`](../../CONTRIBUTING.md).
