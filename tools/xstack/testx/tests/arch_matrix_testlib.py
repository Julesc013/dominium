"""Shared ARCH-MATRIX-0 TestX helpers."""

from __future__ import annotations

import json
import os

from tools.release.arch_matrix_common import REPORT_JSON_REL, arch_matrix_violations, build_arch_matrix_report, write_arch_matrix_outputs
from tools.xstack.testx.tests.update_model_testlib import ensure_assets as ensure_update_assets


def _registry_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), "data", "registries", "target_matrix_registry.json")


def ensure_assets(repo_root: str) -> None:
    ensure_update_assets(repo_root)
    if os.path.isfile(_registry_path(repo_root)):
        return
    write_arch_matrix_outputs(repo_root, write_registry=True)


def load_registry(repo_root: str) -> dict:
    ensure_assets(repo_root)
    with open(_registry_path(repo_root), "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_report(repo_root: str) -> dict:
    ensure_assets(repo_root)
    return build_arch_matrix_report(repo_root)


def report_json_path(repo_root: str) -> str:
    return os.path.join(os.path.abspath(repo_root), REPORT_JSON_REL.replace("/", os.sep))


def current_violations(repo_root: str) -> list[dict]:
    ensure_assets(repo_root)
    return arch_matrix_violations(repo_root)


__all__ = [
    "build_report",
    "current_violations",
    "ensure_assets",
    "load_registry",
    "report_json_path",
]
