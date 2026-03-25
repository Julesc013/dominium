"""FAST test: Π-0 readiness matrix rows are structurally valid."""

from __future__ import annotations


TEST_ID = "test_readiness_matrix_schema_valid"
TEST_TAGS = ["fast", "pi", "blueprint", "readiness"]


def run(repo_root: str):
    from tools.xstack.testx.tests.meta_blueprint_testlib import committed_readiness_matrix

    payload = committed_readiness_matrix(repo_root)
    if str(payload.get("report_id", "")).strip() != "pi.0.readiness_matrix.v1":
        return {"status": "fail", "message": "readiness matrix report_id drifted"}
    rows = list(payload.get("rows") or [])
    if not rows:
        return {"status": "fail", "message": "readiness matrix must contain rows"}
    allowed = {
        "ready_now",
        "foundation_ready_but_not_implemented",
        "requires_new_foundation",
        "unrealistic_currently",
    }
    for row in rows:
        readiness = str(dict(row or {}).get("readiness", "")).strip()
        if readiness not in allowed:
            return {"status": "fail", "message": f"unexpected readiness value '{readiness}'"}
    first = dict(rows[0] or {})
    for key in ("capability_id", "capability_label", "required_series", "missing_building_blocks", "estimated_complexity", "confidence_level"):
        if key not in first:
            return {"status": "fail", "message": f"readiness row missing '{key}'"}
    return {"status": "pass", "message": "Π-0 readiness matrix rows are valid"}
