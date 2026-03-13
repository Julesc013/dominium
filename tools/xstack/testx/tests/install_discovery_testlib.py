"""Helpers for INSTALL-DISCOVERY-0 TestX coverage."""

from __future__ import annotations

import json
import os
import re
import sys


def ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _manifest_payload(install_id: str, root_path: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "install_id": install_id,
        "install_version": "0.0.0",
        "store_root_ref": {"root_path": root_path},
        "semantic_contract_registry_hash": "0" * 64,
    }


def seed_install_root(install_root: str, install_id: str, root_path: str = ".") -> str:
    os.makedirs(install_root, exist_ok=True)
    manifest_path = os.path.join(install_root, "install.manifest.json")
    _write_json(manifest_path, _manifest_payload(install_id, root_path))
    return manifest_path


def load_engine(repo_root: str):
    ensure_repo_root(repo_root)
    from src.lib.install import discover_install, load_runtime_install_registry

    return discover_install, load_runtime_install_registry


def build_report(repo_root: str) -> dict:
    ensure_repo_root(repo_root)
    from tools.release.install_discovery_common import build_install_discovery_report

    return build_install_discovery_report(repo_root)


def baseline_fingerprint(repo_root: str) -> str:
    path = os.path.join(repo_root, "docs", "audit", "INSTALL_DISCOVERY_BASELINE.md")
    text = open(path, "r", encoding="utf-8").read()
    match = re.search(r"Fingerprint: `([A-Fa-f0-9]{64})`", text)
    if not match:
        raise ValueError("install discovery baseline fingerprint missing")
    return match.group(1)
