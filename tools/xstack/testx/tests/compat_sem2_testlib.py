"""Shared fixtures for COMPAT-SEM-2 extension discipline tests."""

from __future__ import annotations

import json
import os
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def load_extension_registry(repo_root: str) -> dict:
    path = os.path.join(repo_root, "data", "registries", "extension_interpretation_registry.json")
    return json.load(open(path, "r", encoding="utf-8"))
