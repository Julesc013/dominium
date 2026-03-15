"""FAST test: setup self-update replaces the setup binary atomically."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_self_update_flow_safe"
TEST_TAGS = ["fast", "release", "update-model", "self-update"]


def run(repo_root: str):
    del repo_root
    from tools.setup.setup_cli import _copy_managed_paths

    with tempfile.TemporaryDirectory() as tmp:
        source_root = os.path.join(tmp, "source")
        install_root = os.path.join(tmp, "install")
        os.makedirs(os.path.join(source_root, "bin"), exist_ok=True)
        os.makedirs(os.path.join(install_root, "bin"), exist_ok=True)
        for rel_path, text in (
            ("bin/setup", "new-setup\n"),
            ("bin/setup.cmd", "new-cmd\n"),
            ("bin/setup.descriptor.json", "{}\n"),
        ):
            with open(os.path.join(source_root, rel_path.replace("/", os.sep)), "w", encoding="utf-8") as handle:
                handle.write(text)
        with open(os.path.join(install_root, "bin", "setup"), "w", encoding="utf-8") as handle:
            handle.write("old-setup\n")
        _copy_managed_paths(
            source_root,
            install_root,
            [
                {
                    "component_id": "binary.setup",
                    "component_kind": "binary",
                    "extensions": {"product_id": "setup"},
                }
            ],
        )
        with open(os.path.join(install_root, "bin", "setup"), "r", encoding="utf-8") as handle:
            if handle.read() != "new-setup\n":
                return {"status": "fail", "message": "setup self-update did not replace the setup binary content"}
        if os.path.exists(os.path.join(install_root, "bin", "setup.new")):
            return {"status": "fail", "message": "setup self-update left a temporary replacement file behind"}
    return {"status": "pass", "message": "setup self-update replaces the setup binary atomically"}
