"""FAST test: dimension_add accepts identical dimensions deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.dimension_add_valid"
TEST_TAGS = ["fast", "materials", "dimensions"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from materials.dimension_engine import dimension_add

    result = dimension_add({"M": 1, "L": 2, "T": -2}, {"M": 1, "L": 2, "T": -2})
    expected = {"M": 1, "L": 2, "T": -2}
    if result != expected:
        return {"status": "fail", "message": "dimension_add returned unexpected vector"}
    return {"status": "pass", "message": "dimension_add valid path passed"}
