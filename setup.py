"""Stamp source identity into wheel/sdist without importing the application."""
from pathlib import Path
import json
import re
import subprocess

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

ROOT = Path(__file__).resolve().parent
STAMP = 'voice_stt_client/build_identity.json'


def identity():
    # Rebuilding a wheel from the sdist must retain the original source SHA.
    if not (ROOT / '.git').exists() and (ROOT / STAMP).is_file():
        return json.loads((ROOT / STAMP).read_text(encoding='utf-8'))
    commit = 'unknown'
    dirty = None
    if (ROOT / '.git').exists():
        commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
        if not re.fullmatch(r'[0-9a-f]{40}', commit):
            raise RuntimeError('Invalid source commit')
        # Administrative run records do not alter the shipped product.
        paths = ['voice_stt_client', 'scripts', '.gitattributes', 'setup.py', 'pyproject.toml',
                 'VERSION', 'requirements.txt', 'requirements-dev.txt', 'MANIFEST.in', 'README.md', 'voice-stt-client.spec']
        dirty = bool(subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain', '--', *paths]))
    return dict(schemaVersion=1, version=(ROOT / 'VERSION').read_text().strip(),
                clientCommit=commit if not dirty else 'unknown', sourceCommit=commit, sourceDirty=dirty)


def stamp(directory):
    path = Path(directory) / STAMP
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(identity(), sort_keys=True, indent=2) + '\n', encoding='utf-8')


class BuildPy(build_py):
    def run(self):
        super().run()
        stamp(self.build_lib)

    def get_outputs(self, include_bytecode=1):
        return super().get_outputs(include_bytecode) + [str(Path(self.build_lib) / STAMP)]


class Sdist(sdist):
    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        stamp(base_dir)


if __name__ == '__main__':
    setup(cmdclass={'build_py': BuildPy, 'sdist': Sdist})
