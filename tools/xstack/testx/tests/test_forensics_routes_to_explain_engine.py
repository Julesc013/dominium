"""FAST test: META-INSTR0 forensics points route through explain engine deterministically."""

from __future__ import annotations

import os
import sys


TEST_ID = "test_forensics_routes_to_explain_engine"
TEST_TAGS = ["fast", "meta", "instrumentation", "forensics", "explain"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from meta_instr0_testlib import authority_context, run_forensics_case

    result = run_forensics_case(
        repo_root=repo_root,
        owner_kind="domain",
        owner_id="domain.elec",
        forensics_point_id="forensics.elec.trip",
        authority_context_row=authority_context(
            privilege_level="operator",
            entitlements=["session.boot", "entitlement.inspect"],
        ),
        has_physical_access=True,
        event_id="event.meta_instr0.trip.001",
        target_id="system.meta_instr0.alpha",
        event_kind_id="elec.trip",
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "forensics route refused unexpectedly"}
    artifact = dict(result.get("explain_artifact") or {})
    ext = dict(artifact.get("extensions") or {})
    if not str(artifact.get("explain_id", "")).strip():
        return {"status": "fail", "message": "forensics route must return explain artifact with explain_id"}
    if str(ext.get("event_kind_id", "")).strip() != "elec.trip":
        return {"status": "fail", "message": "explain artifact should preserve event_kind_id"}
    if not str(ext.get("explain_artifact_type_id", "")).strip():
        return {"status": "fail", "message": "explain artifact missing explain_artifact_type_id extension"}
    if not list(artifact.get("cause_chain") or []):
        return {"status": "fail", "message": "forensics explain artifact should include non-empty cause_chain"}
    return {"status": "pass", "message": "forensics points route through explain engine"}

