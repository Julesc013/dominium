"""FAST test: runtime source roots include moved targets when shadow dirs are empty."""

from __future__ import annotations

import json
import os
import tempfile


TEST_ID = "test_runtime_source_roots_include_target_when_shadow_empty"
TEST_TAGS = ["fast", "dist", "windows", "regression", "xi5a"]


def run(repo_root: str):
    from tools.dist.dist_tree_common import _runtime_source_roots

    temp_parent = os.path.join(repo_root, "build", "tmp")
    os.makedirs(temp_parent, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dist_runtime_roots_", dir=temp_parent) as temp_root:
        data_root = os.path.join(temp_root, "data", "restructure")
        os.makedirs(data_root, exist_ok=True)
        os.makedirs(os.path.join(temp_root, "src", "compat"), exist_ok=True)
        os.makedirs(os.path.join(temp_root, "compat"), exist_ok=True)
        with open(os.path.join(temp_root, "compat", "__init__.py"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("VALUE = 1\n")
        with open(os.path.join(temp_root, "compat", "capability_negotiation.py"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("def ping() -> str:\n    return 'ok'\n")
        with open(os.path.join(data_root, "src_domain_mapping_lock_approved_v4.json"), "w", encoding="utf-8", newline="\n") as handle:
            json.dump(
                {
                    "approved_for_xi5": [
                        {
                            "source_path": "compat/capability_negotiation.py",
                            "target_path": "compat/capability_negotiation.py",
                        }
                    ]
                },
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")

        roots = _runtime_source_roots(temp_root)
        if "compat" not in roots:
            return {
                "status": "fail",
                "message": "runtime source roots did not include the moved target root when the shadow dir was empty",
            }
        if "src" in roots:
            return {
                "status": "fail",
                "message": "runtime source roots should not keep an empty src shadow root active",
            }
    return {"status": "pass", "message": "runtime source roots promote moved targets when shadow dirs are empty"}
