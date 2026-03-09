"""FAST test: the canonical MVP dist layout contains all required directories and files."""

from __future__ import annotations

import sys


TEST_ID = "test_dist_layout_contains_required_dirs"
TEST_TAGS = ["fast", "mvp", "dist", "layout"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.mvp.runtime_bundle import validate_dist_layout

    errors = validate_dist_layout(repo_root=repo_root)
    if errors:
        return {"status": "fail", "message": "dist layout validation failed: {}".format("; ".join(errors))}
    return {"status": "pass", "message": "MVP dist layout contains required directories and files"}
