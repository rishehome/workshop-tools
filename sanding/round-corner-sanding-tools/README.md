# Round-corner sanding tools

This directory contains the FreeCAD source and published exports for hand tools intended to support sanding shaped corners. Four variants are included; their directory names identify the published corner or half-round size.

## Overviews and renders

Each preview uses its published STEP export. Gray is an illustrative finish.

### 4.75 mm corner

![4.75 mm corner sanding tool overview](exports/var1-corner-4_75mm/overview/product-overview.png)

<details><summary>Instagram Story overview</summary>

![4.75 mm corner sanding tool Instagram Story overview](exports/var1-corner-4_75mm/overview/story/product-overview.png)

</details>

| Three-quarter | Front | Side | Top | Back |
| --- | --- | --- | --- | --- |
| ![4.75 mm corner sanding tool three-quarter render](exports/var1-corner-4_75mm/renders/solid-three-quarter.png) | ![4.75 mm corner sanding tool front render](exports/var1-corner-4_75mm/renders/solid-front.png) | ![4.75 mm corner sanding tool side render](exports/var1-corner-4_75mm/renders/solid-side.png) | ![4.75 mm corner sanding tool top render](exports/var1-corner-4_75mm/renders/solid-top.png) | ![4.75 mm corner sanding tool back render](exports/var1-corner-4_75mm/renders/solid-back.png) |

### 10 mm half-round

![10 mm half-round sanding tool overview](exports/var2-half-10mm/overview/product-overview.png)

<details><summary>Instagram Story overview</summary>

![10 mm half-round sanding tool Instagram Story overview](exports/var2-half-10mm/overview/story/product-overview.png)

</details>

| Three-quarter | Front | Side | Top | Back |
| --- | --- | --- | --- | --- |
| ![10 mm half-round sanding tool three-quarter render](exports/var2-half-10mm/renders/solid-three-quarter.png) | ![10 mm half-round sanding tool front render](exports/var2-half-10mm/renders/solid-front.png) | ![10 mm half-round sanding tool side render](exports/var2-half-10mm/renders/solid-side.png) | ![10 mm half-round sanding tool top render](exports/var2-half-10mm/renders/solid-top.png) | ![10 mm half-round sanding tool back render](exports/var2-half-10mm/renders/solid-back.png) |

### 5 mm corner

![5 mm corner sanding tool overview](exports/var3-corner-5mm/overview/product-overview.png)

<details><summary>Instagram Story overview</summary>

![5 mm corner sanding tool Instagram Story overview](exports/var3-corner-5mm/overview/story/product-overview.png)

</details>

| Three-quarter | Front | Side | Top | Back |
| --- | --- | --- | --- | --- |
| ![5 mm corner sanding tool three-quarter render](exports/var3-corner-5mm/renders/solid-three-quarter.png) | ![5 mm corner sanding tool front render](exports/var3-corner-5mm/renders/solid-front.png) | ![5 mm corner sanding tool side render](exports/var3-corner-5mm/renders/solid-side.png) | ![5 mm corner sanding tool top render](exports/var3-corner-5mm/renders/solid-top.png) | ![5 mm corner sanding tool back render](exports/var3-corner-5mm/renders/solid-back.png) |

### 3 mm corner

![3 mm corner sanding tool overview](exports/var4-corner-3mm/overview/product-overview.png)

<details><summary>Instagram Story overview</summary>

![3 mm corner sanding tool Instagram Story overview](exports/var4-corner-3mm/overview/story/product-overview.png)

</details>

| Three-quarter | Front | Side | Top | Back |
| --- | --- | --- | --- | --- |
| ![3 mm corner sanding tool three-quarter render](exports/var4-corner-3mm/renders/solid-three-quarter.png) | ![3 mm corner sanding tool front render](exports/var4-corner-3mm/renders/solid-front.png) | ![3 mm corner sanding tool side render](exports/var4-corner-3mm/renders/solid-side.png) | ![3 mm corner sanding tool top render](exports/var4-corner-3mm/renders/solid-top.png) | ![3 mm corner sanding tool back render](exports/var4-corner-3mm/renders/solid-back.png) |

## Files

| Path | Purpose |
| --- | --- |
| [`object.FCStd`](object.FCStd) | Editable FreeCAD source model. |
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

The overview dimensions are measured CAD bounding extents. Tolerances, material, sanding-media specifications, and compatibility remain unverified. Treat the variant names as identifiers and verify all geometry in FreeCAD or your CAD/CAM software before manufacturing.

## Choosing a file

Use the `.FCStd` file to inspect or edit the FreeCAD model. Use the STEP file for solid CAD/CAM workflows and the STL or OBJ files for mesh-based workflows. Keep the OBJ and MTL files together when importing the OBJ into software that uses material references.

## Revision notes

The source and exports currently have no formal release or revision metadata. When updating this design, record the change and regenerate the affected exports together with the source, following [`CONTRIBUTING.md`](../../CONTRIBUTING.md).
