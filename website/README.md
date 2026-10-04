# Workshop website

An English static catalog generated from the CAD files in this repository. Its
visual baseline follows the Rishe web repository's design system.
Manrope and the Rishe mark are bundled locally, with
no runtime dependencies or third-party font requests. The English-only site
uses that guide's color, typography, spacing, card, focus and theme conventions.

## Build and preview

From the repository root, with Python 3.12 or later:

```sh
python3 tools/build_website.py
python3 -m unittest discover -s tools -p test_website.py
python3 -m http.server 8765 --directory _site
```

Open http://localhost:8765. `_site/` is generated and ignored by Git. It contains
all pages, preview images, sources, exports, font licensing, the design license
and ZIP bundles. Links are relative so the same build works at the GitHub Pages
project path and when previewed locally.

## Content

The generator finds saved `object.FCStd` designs outside backup, generated and
CAM folders. Introductions and category labels live in `catalog.json`; unknown
designs get a fallback introduction until an entry is added. Export variants
are discovered from each design's `exports/` directory. Only existing files
are offered; models without interchange exports offer their FreeCAD source.

Render views and product overviews are reused when available. A resource
diagram is used when a model has no renders, otherwise the catalog shows a
source-file placeholder. Existing `model-facts.json` dimensions are labeled as
approximate CAD body extents, not verified fit specifications. No geometry is
regenerated as part of the website build.

## Update and publish

From the repository root, run:

```sh
python3 tools/publish_website.py
```

This generates all five transparent render views and both overview cards for
all designs, refreshes measured dimensions, builds `_site/`, validates its
links and download bundles, and commits and pushes the output to `gh-pages`.
The command stops on any generation or validation failure before publishing.
It uses a temporary detached Git worktree, removes it afterward, and leaves
your source branch selected. It uses a normal push; if another update reaches
`gh-pages` first, rerun the command rather than force-pushing.

Install the render dependencies once using the setup in
[the visual assets guide](../docs/visual-assets.md). Blender and FreeCAD are
required for rendering; the script detects their standard macOS installation
paths. Use `--blender /path/to/blender` or `BLENDER` for another Blender path,
`FREECAD_PYTHON` for another FreeCAD runtime, and `--python /path/to/python`
for the Python environment containing Jinja2 and Playwright. The script
prefers `venv/bin/python` when present. Git push access and a Git commit identity
must be configured. The remote must already have a `gh-pages` branch.

To regenerate one design and publish the complete catalog:

```sh
python3 tools/publish_website.py --path cnc/camera-mount/shapeoko-diy-mount
```

For text or style updates using existing renders and overviews:

```sh
python3 tools/publish_website.py --skip-renders
```

To generate and validate without publishing:

```sh
python3 tools/publish_website.py --build-only
python3 -m http.server 8765 --directory _site
```

Combine `--build-only` with `--path` or `--skip-renders` as needed. Use
`--device cpu` to disable automatic Metal acceleration and `--remote NAME`
to publish to another configured Git remote.

Edit `catalog.json` for introductions and variant labels, `assets/site.css`
for styling, `assets/theme.js` for theme behavior, and
`../tools/build_website.py` for page markup. Generated `_site/` files are
replaced on each build. Renders, overviews and metadata are updated in your
source checkout; commit and push those source changes separately so they
remain reproducible. The publication script commits only the generated site
to `gh-pages`.

There is no repository Actions workflow. Publishing is a local command.

In repository **Settings → Pages**, choose **Deploy from a branch → gh-pages →
/ (root)**. GitHub serves the committed files; generating the website remains
a local, manual step.

The public URL is https://rishehome.github.io/workshop-tools/ once Pages is
enabled and a deployment succeeds.
