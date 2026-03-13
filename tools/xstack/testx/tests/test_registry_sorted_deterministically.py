"""FAST test: runtime install registry normalization preserves deterministic ordering."""

from __future__ import annotations

import json
import os
import tempfile


TEST_ID = "test_registry_sorted_deterministically"
TEST_TAGS = ["fast", "install", "lib", "ordering"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_discovery_testlib import load_engine

    _discover_install, load_runtime_install_registry = load_engine(repo_root)
    with tempfile.TemporaryDirectory(prefix="install_registry_order_") as temp_root:
        registry_path = os.path.join(temp_root, "install_registry.json")
        with open(registry_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(
                {
                    "schema_id": "dominium.registry.install_registry",
                    "schema_version": "1.0.0",
                    "record": {
                        "registry_id": "dominium.registry.install_registry",
                        "registry_version": "1.0.0",
                        "installs": [
                            {"install_id": "install.zed", "path": "./zed", "version": "0.0.0"},
                            {"install_id": "install.alpha", "path": "./alpha", "version": "0.0.0"},
                            {"install_id": "install.alpha", "path": "./alpha_2", "version": "0.0.0"},
                        ],
                    },
                },
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")
        payload = load_runtime_install_registry(registry_path)
    installs = list(dict(payload.get("record") or {}).get("installs") or [])
    ordered = [(str(row.get("install_id", "")).strip(), str(row.get("path", "")).strip()) for row in installs]
    if ordered != [("install.alpha", "./alpha"), ("install.alpha", "./alpha_2"), ("install.zed", "./zed")]:
        return {"status": "fail", "message": "install registry rows are not sorted deterministically"}
    return {"status": "pass", "message": "install registry normalization preserves deterministic ordering"}
