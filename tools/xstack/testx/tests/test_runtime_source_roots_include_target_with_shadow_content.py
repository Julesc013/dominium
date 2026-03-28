"""FAST test: runtime source roots keep moved targets even when shadow roots still contain runtime files."""

from __future__ import annotations

import json
import os
import tempfile


TEST_ID = "test_runtime_source_roots_include_target_with_shadow_content"
TEST_TAGS = ["fast", "dist", "windows", "regression", "xi5a"]


def run(repo_root: str):
    from tools.dist.dist_tree_common import _runtime_source_roots

    temp_parent = os.path.join(repo_root, "build", "tmp")
    os.makedirs(temp_parent, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dist_runtime_roots_dual_", dir=temp_parent) as temp_root:
        data_root = os.path.join(temp_root, "data", "restructure")
        os.makedirs(data_root, exist_ok=True)
        os.makedirs(os.path.join(temp_root, "src", "worldgen"), exist_ok=True)
        os.makedirs(os.path.join(temp_root, "worldgen"), exist_ok=True)
        with open(os.path.join(temp_root, "src", "worldgen", "__init__.py"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("SHADOW = True\n")
        with open(os.path.join(temp_root, "worldgen", "__init__.py"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("TARGET = True\n")
        with open(os.path.join(temp_root, "worldgen", "earth.py"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("VALUE = 1\n")
        with open(os.path.join(data_root, "src_domain_mapping_lock_approved_v4.json"), "w", encoding="utf-8", newline="\n") as handle:
            json.dump(
                {
                    "approved_for_xi5": [
                        {
                            "source_path": "src/worldgen/earth.py",
                            "target_path": "worldgen/earth.py",
                        }
                    ]
                },
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")

        roots = _runtime_source_roots(temp_root)
        if "worldgen" not in roots:
            return {
                "status": "fail",
                "message": "runtime source roots dropped the moved target root when a shadow package still contained deferred runtime content",
            }
        if "src" not in roots:
            return {
                "status": "fail",
                "message": "runtime source roots should keep the shadow src root when deferred runtime content remains",
            }
    return {"status": "pass", "message": "runtime source roots keep target and shadow roots when both contain runtime content"}
