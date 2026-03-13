"""FAST test: explicit install root wins the discovery order."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_explicit_install_root_used"
TEST_TAGS = ["fast", "install", "appshell", "lib"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_discovery_testlib import load_engine, seed_install_root

    discover_install, _load_runtime_install_registry = load_engine(repo_root)
    with tempfile.TemporaryDirectory(prefix="install_discovery_explicit_") as temp_root:
        install_root = os.path.join(temp_root, "install")
        seed_install_root(install_root, "install.explicit")
        result = discover_install(
            raw_args=["--install-root", install_root],
            executable_path=os.path.join(temp_root, "bin", "dominium_setup"),
            cwd=temp_root,
            env={},
            platform_id="platform.posix_min",
        )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "explicit install root did not resolve"}
    if str(result.get("resolution_source", "")).strip() != "cli_install_root":
        return {"status": "fail", "message": "explicit install root did not win the discovery order"}
    if os.path.normcase(os.path.normpath(str(result.get("resolved_install_root_path", "")))) != os.path.normcase(os.path.normpath(install_root)):
        return {"status": "fail", "message": "resolved install root drifted from explicit CLI input"}
    return {"status": "pass", "message": "explicit install root is authoritative"}
