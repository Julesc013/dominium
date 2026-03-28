"""FAST test: dimension_add refuses mismatched dimensions with canonical code."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.dimension_add_invalid_refusal"
TEST_TAGS = ["fast", "materials", "dimensions"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from materials.dimension_engine import DimensionError, dimension_add

    try:
        dimension_add({"M": 1}, {"L": 1})
    except DimensionError as exc:
        if str(getattr(exc, "reason_code", "")) != "refusal.dimension.mismatch":
            return {"status": "fail", "message": "unexpected reason_code '{}'".format(getattr(exc, "reason_code", ""))}
        return {"status": "pass", "message": "dimension mismatch refusal emitted"}
    return {"status": "fail", "message": "expected DimensionError for mismatched dimensions"}
