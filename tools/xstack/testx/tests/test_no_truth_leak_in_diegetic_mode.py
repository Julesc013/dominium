"""STRICT test: META-INSTR0 diegetic measurement path does not leak truth-level raw state."""

from __future__ import annotations

import os
import re
import sys


TEST_ID = "test_no_truth_leak_in_diegetic_mode"
TEST_TAGS = ["strict", "meta", "instrumentation", "epistemic", "diegetic"]


FORBIDDEN_PATTERN = re.compile(r"\b(truth_model|truthmodel|universe_state|render_model)\b", re.IGNORECASE)
ENGINE_TARGET = "meta/instrumentation/instrumentation_engine.py"


def _read(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return open(abs_path, "r", encoding="utf-8").read()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)

    from meta_instr0_testlib import authority_context, run_measurement_case

    engine_text = _read(repo_root, ENGINE_TARGET)
    for line_no, line in enumerate(engine_text.splitlines(), start=1):
        if FORBIDDEN_PATTERN.search(str(line)):
            return {
                "status": "fail",
                "message": "forbidden truth token found in {}:{} ({})".format(
                    ENGINE_TARGET,
                    line_no,
                    str(line).strip(),
                ),
            }

    observed = run_measurement_case(
        repo_root=repo_root,
        owner_kind="domain",
        owner_id="domain.elec",
        measurement_point_id="measure.elec.voltage",
        raw_value=237,
        current_tick=73,
        authority_context_row=authority_context(
            privilege_level="operator",
            entitlements=["session.boot", "entitlement.inspect"],
        ),
        has_physical_access=True,
        available_instrument_type_ids=["instrument.multimeter"],
    )
    if str(observed.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "measurement observation refused unexpectedly in diegetic mode"}

    artifact = dict(observed.get("observation_artifact") or {})
    ext = dict(artifact.get("extensions") or {})
    value = artifact.get("value")
    if str(artifact.get("artifact_family_id", "")).strip() != "OBSERVATION":
        return {"status": "fail", "message": "diegetic measurement must emit OBSERVATION artifact"}
    if "raw_value" in artifact:
        return {"status": "fail", "message": "diegetic measurement leaked raw_value field"}
    if not str(ext.get("raw_value_hash", "")).strip():
        return {"status": "fail", "message": "diegetic measurement missing raw_value_hash trace token"}
    if not isinstance(value, int):
        return {"status": "fail", "message": "diegetic measurement output must be integer"}
    if int(value) == 237:
        return {"status": "fail", "message": "diegetic measurement leaked unredacted raw reading"}
    return {"status": "pass", "message": "diegetic instrumentation path does not leak truth-level raw state"}

