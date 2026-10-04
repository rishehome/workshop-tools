#!/usr/bin/env python3
"""Generate workshop assets, validate the website, and publish to gh-pages."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from workshop_models import ROOT, select


def run(command, cwd=ROOT, capture=False):
    return subprocess.run([str(arg) for arg in command], cwd=cwd, check=True,
                          text=True, stdout=subprocess.PIPE if capture else None).stdout


def publish(root, site, remote='origin'):
    """Publish in a temporary detached checkout without changing the source branch."""
    ref = f'refs/remotes/{remote}/gh-pages'
    run(['git', 'fetch', remote, f'refs/heads/gh-pages:{ref}'], root)
    with tempfile.TemporaryDirectory(prefix='workshop-pages-') as temporary:
        checkout = Path(temporary) / 'pages'
        run(['git', 'worktree', 'add', '--detach', checkout, ref], root)
        try:
            # This checkout was just created by us; replace only its published files.
            for path in checkout.iterdir():
                if path.name == '.git':
                    continue
                if path.is_dir() and not path.is_symlink():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            shutil.copytree(site, checkout, dirs_exist_ok=True)
            run(['git', 'add', '--all'], checkout)
            changes = run(['git', 'diff', '--cached', '--name-only'], checkout, capture=True)
            if not changes.strip():
                print('gh-pages is already up to date.', flush=True)
                return
            run(['git', 'commit', '-m', 'Update workshop website'], checkout)
            # A normal push rejects concurrent updates rather than overwriting them.
            run(['git', 'push', remote, 'HEAD:refs/heads/gh-pages'], checkout)
        finally:
            run(['git', 'worktree', 'remove', '--force', checkout], root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=Path, default=Path('.'),
                        help='Render one design or variant; default: all designs')
    parser.add_argument('--skip-renders', action='store_true',
                        help='Reuse existing renders and overviews for text/style updates')
    parser.add_argument('--build-only', action='store_true',
                        help='Generate and validate locally without publishing')
    parser.add_argument('--blender', default=os.environ.get('BLENDER'),
                        help='Blender executable (or set BLENDER)')
    parser.add_argument('--python', default=str(ROOT / 'venv/bin/python')
                        if (ROOT / 'venv/bin/python').is_file() else sys.executable,
                        help='Python with the overview dependencies; default: venv or current Python')
    parser.add_argument('--device', choices=('auto', 'cpu'), default='auto')
    parser.add_argument('--remote', default='origin', help='Git remote to publish to')
    args = parser.parse_args()
    try:
        if not args.skip_renders:
            target = (ROOT / args.path).resolve()
            models = select(target)
            if not models:
                parser.error('No workshop models matched --path')
            blender = args.blender or shutil.which('blender')
            if not blender and Path('/Applications/Blender.app/Contents/MacOS/Blender').is_file():
                blender = '/Applications/Blender.app/Contents/MacOS/Blender'
            if not blender:
                parser.error('Blender not found; use --blender or set BLENDER')
            # Check dependencies before spending time rendering.
            run([args.python, '-c', 'import jinja2; import playwright.sync_api'])
            run([blender, '--background', '--python-exit-code', '1', '--python',
                 ROOT / 'tools/render_tools.py', '--', '--path', target, '--device', args.device])
            for _, folder in models:
                run([args.python, ROOT / 'tools/build_product_overview.py', folder,
                     '--generate-info', '--scale', '1'])
        run([sys.executable, ROOT / 'tools/build_website.py'])
        run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tools', '-p', 'test_website.py'])
        if args.build_only:
            print('Validated website in _site/; nothing published.', flush=True)
        else:
            publish(ROOT, ROOT / '_site', args.remote)
            print('Website published to gh-pages.', flush=True)
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        parser.exit(1, f'Website update failed: {exc}\n')


if __name__ == '__main__':
    main()
