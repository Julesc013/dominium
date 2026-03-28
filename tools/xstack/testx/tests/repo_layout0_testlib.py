"""Helpers for REPO-LAYOUT-0 TestX coverage."""

from __future__ import annotations

import json
import os
import re
import sys


def ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def seed_virtual_root_registry(source_repo_root: str, temp_root: str) -> str:
    source = os.path.join(source_repo_root, "data", "registries", "virtual_root_registry.json")
    target = os.path.join(temp_root, "data", "registries", "virtual_root_registry.json")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(source, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    _write_json(target, payload)
    return target


def load_vpath_module(repo_root: str):
    ensure_repo_root(repo_root)
    from appshell.paths import virtual_paths

    return virtual_paths


def make_portable_context(source_repo_root: str, temp_root: str) -> dict:
    seed_virtual_root_registry(source_repo_root, temp_root)
    install_root = os.path.join(temp_root, "portable")
    os.makedirs(install_root, exist_ok=True)
    _write_json(
        os.path.join(install_root, "install.manifest.json"),
        {
            "schema_version": "1.0.0",
            "install_id": "portable.install.test",
            "store_root_ref": {"root_path": "."},
        },
    )
    vpaths = load_vpath_module(source_repo_root)
    return vpaths.vpath_init(
        {
            "repo_root": temp_root,
            "product_id": "client",
            "raw_args": [],
            "executable_path": os.path.join(install_root, "dominium_client"),
        }
    )


def make_installed_context(source_repo_root: str, temp_root: str) -> dict:
    seed_virtual_root_registry(source_repo_root, temp_root)
    install_root = os.path.join(temp_root, "installs", "primary")
    store_root = os.path.join(temp_root, "installs", "store")
    os.makedirs(install_root, exist_ok=True)
    os.makedirs(store_root, exist_ok=True)
    _write_json(
        os.path.join(install_root, "install.manifest.json"),
        {
            "schema_version": "1.0.0",
            "install_id": "registered.install.test",
            "store_root_ref": {"root_path": "../store"},
        },
    )
    _write_json(
        os.path.join(temp_root, "data", "registries", "install_registry.json"),
        {
            "schema_id": "dominium.registry.install_registry",
            "schema_version": "1.0.0",
            "record": {
                "registry_id": "dominium.registry.install_registry",
                "registry_version": "1.0.0",
                "installs": [
                    {
                        "install_id": "registered.install.test",
                        "path": "../../installs/primary",
                    }
                ],
            },
        },
    )
    vpaths = load_vpath_module(source_repo_root)
    return vpaths.vpath_init(
        {
            "repo_root": temp_root,
            "product_id": "launcher",
            "raw_args": ["--install-id", "registered.install.test"],
            "executable_path": os.path.join(temp_root, "bin", "dominium_launcher"),
        }
    )


def build_report(repo_root: str) -> dict:
    ensure_repo_root(repo_root)
    from tools.release.virtual_paths_common import build_virtual_paths_report

    return build_virtual_paths_report(repo_root)


def baseline_fingerprint(repo_root: str) -> str:
    text = _read_text(os.path.join(repo_root, "docs", "audit", "VIRTUAL_PATHS_BASELINE.md"))
    match = re.search(r"Fingerprint: `([A-Fa-f0-9]{64})`", text)
    if not match:
        raise ValueError("baseline fingerprint missing")
    return match.group(1)
