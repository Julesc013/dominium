"""Shared DIST-2 distribution verification TestX helpers."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager

from tools.dist.dist_verify_common import (
    DEFAULT_BUNDLE_REL,
    build_distribution_verify_report,
    load_distribution_verify_report,
    scan_distribution_absolute_path_leaks,
    scan_forbidden_distribution_files,
)


def bundle_root(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), DEFAULT_BUNDLE_REL.replace("/", os.sep))


def load_report(repo_root: str) -> dict:
    report = load_distribution_verify_report(repo_root, platform_tag="win64")
    if report:
        return report
    return build_distribution_verify_report(bundle_root(repo_root), platform_tag="win64", repo_root=repo_root)


@contextmanager
def temp_bundle_fixture(repo_root: str):
    temp_parent = os.path.join(repo_root, "build", "tmp")
    os.makedirs(temp_parent, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dominium_dist2_test_", dir=temp_parent) as temp_root:
        yield temp_root


def write_json(path: str, payload: dict) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


__all__ = [
    "bundle_root",
    "load_report",
    "scan_distribution_absolute_path_leaks",
    "scan_forbidden_distribution_files",
    "temp_bundle_fixture",
    "write_json",
]
