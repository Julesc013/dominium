"""FAST test: META-INSTR0 measurement redaction is applied for diegetic reads."""

from __future__ import annotations

import os
import sys


TEST_ID = "test_measurement_redaction_applied"
TEST_TAGS = ["fast", "meta", "instrumentation", "redaction"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from meta_instr0_testlib import authority_context, run_measurement_case

    result = run_measurement_case(
        repo_root=repo_root,
        owner_kind="domain",
        owner_id="domain.elec",
        measurement_point_id="measure.elec.voltage",
        raw_value=237,
        current_tick=41,
        authority_context_row=authority_context(
            privilege_level="operator",
            entitlements=["session.boot", "entitlement.inspect"],
        ),
        has_physical_access=True,
        available_instrument_type_ids=["instrument.multimeter"],
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "measurement observation path refused unexpectedly"}

    artifact = dict(result.get("observation_artifact") or {})
    ext = dict(artifact.get("extensions") or {})
    value = artifact.get("value")
    if str(artifact.get("artifact_family_id", "")).strip() != "OBSERVATION":
        return {"status": "fail", "message": "measurement output must be OBSERVATION artifact family"}
    if not bool(ext.get("redaction_applied", False)):
        return {"status": "fail", "message": "expected redaction_applied=true for diegetic quantized readout"}
    if str(ext.get("redaction_mode", "")).strip() != "diegetic_quantized":
        return {"status": "fail", "message": "expected diegetic_quantized redaction mode"}
    if not isinstance(value, int):
        return {"status": "fail", "message": "redacted measurement value must remain deterministic integer"}
    if int(value) % 50 != 0:
        return {"status": "fail", "message": "diegetic quantized measurement value should align to coarse quantum"}
    if "raw_value" in artifact:
        return {"status": "fail", "message": "observation artifact leaked raw_value field"}
    if not str(ext.get("raw_value_hash", "")).strip():
        return {"status": "fail", "message": "observation artifact must include raw_value_hash for traceability"}
    return {"status": "pass", "message": "measurement redaction applied with deterministic quantization"}

