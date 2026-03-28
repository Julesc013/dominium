"""FAST test: fixed-point overflow is handled deterministically via refusal."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.fixed_point_overflow_handling"
TEST_TAGS = ["fast", "materials", "numeric"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from materials.dimension_engine import FixedPointOverflow, INT64_MAX, fixed_point_add

    try:
        fixed_point_add(INT64_MAX, 1)
    except FixedPointOverflow as exc:
        if str(getattr(exc, "reason_code", "")) != "refusal.numeric.fixed_point_overflow":
            return {"status": "fail", "message": "unexpected overflow reason code"}
        return {"status": "pass", "message": "overflow refusal emitted"}
    return {"status": "fail", "message": "expected overflow refusal for fixed_point_add(INT64_MAX, 1)"}
