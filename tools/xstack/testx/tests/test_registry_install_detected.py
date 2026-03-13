"""FAST test: installed-mode registry discovery resolves a registered install."""

from __future__ import annotations

import json
import os
import tempfile


TEST_ID = "test_registry_install_detected"
TEST_TAGS = ["fast", "install", "appshell", "installed"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_discovery_testlib import load_engine, seed_install_root

    discover_install, _load_runtime_install_registry = load_engine(repo_root)
    with tempfile.TemporaryDirectory(prefix="install_discovery_registry_") as temp_root:
        config_root = os.path.join(temp_root, "config")
        install_root = os.path.join(temp_root, "installs", "primary")
        registry_path = os.path.join(config_root, "dominium", "install_registry.json")
        seed_install_root(install_root, "install.registered", "../store")
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        with open(registry_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(
                {
                    "schema_id": "dominium.registry.install_registry",
                    "schema_version": "1.0.0",
                    "record": {
                        "registry_id": "dominium.registry.install_registry",
                        "registry_version": "1.0.0",
                        "installs": [
                            {
                                "install_id": "install.registered",
                                "path": "../../installs/primary",
                                "version": "0.0.0",
                                "contract_registry_hash": "0" * 64,
                            }
                        ],
                    },
                },
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")
        result = discover_install(
            raw_args=[],
            executable_path=os.path.join(temp_root, "bin", "dominium_launcher"),
            cwd=temp_root,
            env={"XDG_CONFIG_HOME": config_root, "HOME": temp_root},
            platform_id="platform.posix_min",
        )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "registry-backed install did not resolve"}
    if str(result.get("mode", "")).strip() != "installed":
        return {"status": "fail", "message": "registry-backed install did not classify the mode as installed"}
    if "installed_registry" not in str(result.get("resolution_source", "")).strip():
        return {"status": "fail", "message": "registry-backed install did not resolve through the install registry"}
    return {"status": "pass", "message": "registry-backed install discovery is deterministic"}
