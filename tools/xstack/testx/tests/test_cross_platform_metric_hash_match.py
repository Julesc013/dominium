"""FAST test: GEO-3 metric replay verifier produces stable hash chains."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_cross_platform_metric_hash_match"
TEST_TAGS = ["fast", "geo", "metric", "replay", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.geo.tool_verify_metric_stability import verify_metric_stability

    first = verify_metric_stability()
    second = verify_metric_stability()
    if dict(first) != dict(second):
        return {"status": "fail", "message": "metric replay verifier is not deterministic"}
    proof_surface = dict(first.get("proof_surface") or {})
    for key in ("metric_query_hash_chain", "deterministic_fingerprint"):
        token = str(proof_surface.get(key, "") or first.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(token):
            return {"status": "fail", "message": "missing or invalid {}".format(key)}
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "metric replay verifier reported non-complete result"}
    return {"status": "pass", "message": "GEO-3 metric replay hash chains stable"}
