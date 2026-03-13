"""FAST test: portable adjacency resolves install discovery deterministically."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_portable_manifest_detected"
TEST_TAGS = ["fast", "install", "appshell", "portable"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_discovery_testlib import load_engine, seed_install_root

    discover_install, _load_runtime_install_registry = load_engine(repo_root)
    with tempfile.TemporaryDirectory(prefix="install_discovery_portable_") as temp_root:
        install_root = os.path.join(temp_root, "portable")
        executable_path = os.path.join(install_root, "dominium_client")
        seed_install_root(install_root, "install.portable")
        result = discover_install(
            raw_args=[],
            executable_path=executable_path,
            cwd=temp_root,
            env={},
            platform_id="platform.posix_min",
        )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "portable manifest adjacency did not resolve"}
    if str(result.get("mode", "")).strip() != "portable":
        return {"status": "fail", "message": "portable discovery did not classify the mode as portable"}
    if str(result.get("resolution_source", "")).strip() != "portable_manifest":
        return {"status": "fail", "message": "portable discovery did not use install.manifest adjacency"}
    return {"status": "pass", "message": "portable manifest adjacency is deterministic"}
