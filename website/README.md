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

## Manual updates and GitHub Pages

Edit `catalog.json` for introductions and variant labels, `assets/site.css`
for styling, `assets/theme.js` for theme behavior, and
`../tools/build_website.py` for page markup. Run the build command above after
each update. It regenerates HTML pages and copies the CSS, JavaScript and
download files into `_site/`. Edit the source files rather than `_site/`, which
is replaced during each build.

There is no repository Actions workflow. Publish when you are ready by copying
the complete `_site/` output into a checkout of `gh-pages`, then committing and
pushing that branch. Keep the generated `.nojekyll` file and all asset and
download directories together.

To create a separate publication checkout once, from the repository root:

```sh
git fetch origin
git worktree add --track -b gh-pages ../workshop-tools-pages origin/gh-pages
```

If you already have a `gh-pages` checkout, use that existing checkout instead.
For each update, build and validate locally, then publish:

```sh
python3 tools/build_website.py
python3 -m unittest discover -s tools -p test_website.py
git -C ../workshop-tools-pages pull --ff-only
rsync -a --delete --exclude='.git' _site/ ../workshop-tools-pages/
git -C ../workshop-tools-pages add --all
git -C ../workshop-tools-pages commit -m "Update workshop website"
git -C ../workshop-tools-pages push origin gh-pages
```

In repository **Settings → Pages**, choose **Deploy from a branch → gh-pages →
/ (root)**. GitHub serves the committed files; generating the website remains
a local, manual step.

The public URL is https://rishehome.github.io/workshop-tools/ once Pages is
enabled and a deployment succeeds.
