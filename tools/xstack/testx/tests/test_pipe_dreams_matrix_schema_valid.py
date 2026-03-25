"""FAST test: Π-0 pipe dreams matrix rows are structurally valid."""

from __future__ import annotations


TEST_ID = "test_pipe_dreams_matrix_schema_valid"
TEST_TAGS = ["fast", "pi", "blueprint", "future"]


def run(repo_root: str):
    from tools.xstack.testx.tests.meta_blueprint_testlib import committed_pipe_dreams_matrix

    payload = committed_pipe_dreams_matrix(repo_root)
    if str(payload.get("report_id", "")).strip() != "pi.0.pipe_dreams_matrix.v1":
        return {"status": "fail", "message": "pipe dreams matrix report_id drifted"}
    rows = list(payload.get("rows") or [])
    if len(rows) < 20:
        return {"status": "fail", "message": "pipe dreams matrix must contain the advanced concept set"}
    allowed = {"near", "medium", "long", "speculative"}
    for row in rows:
        tier = str(dict(row or {}).get("feasibility_tier", "")).strip()
        if tier not in allowed:
            return {"status": "fail", "message": f"unexpected feasibility tier '{tier}'"}
    first = dict(rows[0] or {})
    for key in ("dream_id", "category", "prerequisite_foundations", "requires_sigma_phi_upsilon_before_zeta", "notes"):
        if key not in first:
            return {"status": "fail", "message": f"pipe dream row missing '{key}'"}
    return {"status": "pass", "message": "Π-0 pipe dreams matrix rows are valid"}
