"""FAST test: PROC grammar mappings are declared in RWAM, META-ACTION, and META-INFO."""

from __future__ import annotations

import json
import os


TEST_ID = "test_proc_grammar_mappings_present"
TEST_TAGS = ["fast", "proc", "grammar"]


def _load(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid json"


def run(repo_root: str):
    rwam_payload, rwam_err = _load(repo_root, "data/meta/real_world_affordance_matrix.json")
    info_payload, info_err = _load(repo_root, "data/registries/info_artifact_family_registry.json")
    if rwam_err or info_err:
        return {"status": "fail", "message": "RWAM or info artifact family registry missing/invalid"}

    affordances = list(rwam_payload.get("affordances") or [])
    series_rows = list(rwam_payload.get("series_affordance_coverage") or [])
    proc_affordance_hit = False
    for row in affordances:
        if not isinstance(row, dict):
            continue
        implemented = {str(token).strip() for token in list(row.get("series_implemented") or [])}
        if "PROC" in implemented:
            proc_affordance_hit = True
            break
    if not proc_affordance_hit:
        return {"status": "fail", "message": "RWAM affordances missing PROC series_implemented coverage"}

    proc_series_row = next(
        (
            row
            for row in series_rows
            if isinstance(row, dict) and str(row.get("series_id", "")).strip() == "PROC"
        ),
        {},
    )
    if not proc_series_row:
        return {"status": "fail", "message": "RWAM series_affordance_coverage missing PROC row"}

    action_doc = os.path.join(repo_root, "docs", "meta", "ACTION_GRAMMAR_CONSTITUTION.md")
    info_doc = os.path.join(repo_root, "docs", "meta", "INFORMATION_GRAMMAR_CONSTITUTION.md")
    try:
        action_text = open(action_doc, "r", encoding="utf-8").read()
        info_text = open(info_doc, "r", encoding="utf-8").read()
    except OSError:
        return {"status": "fail", "message": "META grammar constitution docs missing"}

    for token in (
        "PROC-0 canonical process-step action mapping examples",
        "`sample qc instrument` -> `SENSE/MEASURE`",
    ):
        if token not in action_text:
            return {"status": "fail", "message": "META-ACTION PROC mapping token missing: {}".format(token)}

    for token in (
        "## 8) Process Artifact Mapping (PROC-0)",
        "process capsule model payloads -> `MODEL`",
    ):
        if token not in info_text:
            return {"status": "fail", "message": "META-INFO PROC mapping token missing: {}".format(token)}

    info_record = info_payload.get("record") if isinstance(info_payload.get("record"), dict) else info_payload
    families = list(info_record.get("families") or [])
    mappings = list(info_record.get("artifact_type_mappings") or [])
    family_ids = {str(row.get("info_family_id", "")).strip() for row in families if isinstance(row, dict)}
    mapping_by_artifact = {
        str(row.get("artifact_type_id", "")).strip(): str(row.get("info_family_id", "")).strip()
        for row in mappings
        if isinstance(row, dict)
    }
    if "MODEL" not in family_ids:
        return {"status": "fail", "message": "MODEL family missing from info artifact family registry"}
    expected_mappings = {
        "artifact.process.run_record": "RECORD",
        "artifact.process.qc_report": "REPORT",
        "artifact.process.capsule_model": "MODEL",
        "artifact.process.capsule_observation": "OBSERVATION",
    }
    missing = [
        "{}->{}".format(key, expected)
        for key, expected in sorted(expected_mappings.items())
        if str(mapping_by_artifact.get(key, "")).strip() != expected
    ]
    if missing:
        return {"status": "fail", "message": "missing PROC info mappings: {}".format(",".join(missing))}

    return {"status": "pass", "message": "PROC RWAM/META-ACTION/META-INFO mappings are present"}
