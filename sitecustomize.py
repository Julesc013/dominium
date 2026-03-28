"""Repo-local Python bootstrap for Dominium tooling."""

from __future__ import annotations

import os
import sys


REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.join(REPO_ROOT, "src")


def _remove_path_once(path: str) -> None:
    token = os.path.normpath(path)
    while token in sys.path:
        sys.path.remove(token)


_remove_path_once(REPO_ROOT)
sys.path.insert(0, REPO_ROOT)

if os.path.isdir(SRC_ROOT):
    _remove_path_once(SRC_ROOT)
    sys.path.insert(1, SRC_ROOT)

try:
    from tools.import_bridge import install_src_aliases
except Exception:
    install_src_aliases = None

if install_src_aliases is not None:
    install_src_aliases(REPO_ROOT)
