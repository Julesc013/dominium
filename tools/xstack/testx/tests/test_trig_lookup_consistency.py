"""FAST test: fixed lookup trig remains stable."""

from __future__ import annotations


TEST_ID = "test_trig_lookup_consistency"
TEST_TAGS = ["fast", "numeric", "astro"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.numeric_discipline_testlib import numeric_ops_payload

    trig = dict(numeric_ops_payload().get("trig") or {})
    if trig.get("cos_0") != 1000 or trig.get("cos_90000") != 0 or trig.get("cos_180000") != -1000:
        return {"status": "fail", "message": "cosine lookup drifted at canonical angles"}
    if trig.get("sin_0") != 0 or trig.get("sin_90000") != 1000 or trig.get("sin_180000") != 0:
        return {"status": "fail", "message": "sine lookup drifted at canonical angles"}
    if trig.get("sin_30000") != trig.get("cos_60000"):
        return {"status": "fail", "message": "lookup-table phase relationship drifted"}
    return {"status": "pass", "message": "lookup-table trig remains deterministic and self-consistent"}
