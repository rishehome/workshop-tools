"""Exercise publication against a local bare remote without touching GitHub."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from publish_website import publish


class PublishWebsiteTests(unittest.TestCase):
    def git(self, *args, cwd=None):
        return subprocess.check_output(['git', *map(str, args)], cwd=cwd, text=True,
                                       stderr=subprocess.STDOUT).strip()

    def test_publication_replaces_site_preserves_source_and_skips_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            remote, root, site = (base / name for name in ('remote.git', 'source', 'site'))
            self.git('init', '--bare', remote)
            self.git('init', '-b', 'main', root)
            self.git('config', 'user.name', 'Test', cwd=root)
            self.git('config', 'user.email', 'test@example.com', cwd=root)
            self.git('remote', 'add', 'origin', remote, cwd=root)
            (root / 'old.html').write_text('old website')
            self.git('add', '.', cwd=root)
            self.git('commit', '-m', 'Initial', cwd=root)
            self.git('push', 'origin', 'HEAD:gh-pages', cwd=root)
            source_head = self.git('rev-parse', 'HEAD', cwd=root)
            (root / 'local.txt').write_text('uncommitted source work')
            site.mkdir()
            (site / 'index.html').write_text('new website')
            (site / '.nojekyll').touch()
            publish(root, site)
            self.assertEqual(self.git('--git-dir', remote, 'show', 'gh-pages:index.html'), 'new website')
            self.assertEqual(self.git('--git-dir', remote, 'ls-tree', '--name-only', 'gh-pages'), '.nojekyll\nindex.html')
            self.assertEqual(self.git('branch', '--show-current', cwd=root), 'main')
            self.assertEqual(self.git('rev-parse', 'HEAD', cwd=root), source_head)
            self.assertEqual((root / 'local.txt').read_text(), 'uncommitted source work')
            self.assertEqual(len(self.git('worktree', 'list', '--porcelain', cwd=root).split('worktree ')), 2)
            published_head = self.git('--git-dir', remote, 'rev-parse', 'gh-pages')
            publish(root, site)
            self.assertEqual(self.git('--git-dir', remote, 'rev-parse', 'gh-pages'), published_head)

    def test_failed_push_cleans_up_checkout(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            remote, root, site = (base / name for name in ('remote.git', 'source', 'site'))
            self.git('init', '--bare', remote)
            self.git('init', '-b', 'main', root)
            self.git('config', 'user.name', 'Test', cwd=root)
            self.git('config', 'user.email', 'test@example.com', cwd=root)
            self.git('remote', 'add', 'origin', remote, cwd=root)
            (root / 'index.html').write_text('old')
            self.git('add', '.', cwd=root)
            self.git('commit', '-m', 'Initial', cwd=root)
            self.git('push', 'origin', 'HEAD:gh-pages', cwd=root)
            hook = remote / 'hooks/pre-receive'
            hook.write_text('#!/bin/sh\nexit 1\n')
            hook.chmod(0o755)
            site.mkdir()
            (site / 'index.html').write_text('new')
            with self.assertRaises(subprocess.CalledProcessError):
                publish(root, site)
            self.assertEqual(self.git('--git-dir', remote, 'show', 'gh-pages:index.html'), 'old')
            self.assertEqual(len(self.git('worktree', 'list', '--porcelain', cwd=root).split('worktree ')), 2)


if __name__ == '__main__':
    unittest.main()
