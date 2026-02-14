"""C8 Run-meta input smell analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "C8_RUN_META_INPUT_SMELL"
DERIVED_ARTIFACTS_REL = "data/registries/derived_artifacts.json"


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    path = os.path.join(repo_root, DERIVED_ARTIFACTS_REL.replace("/", os.sep))
    payload = _load_json(path)
    if not isinstance(payload, dict):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="run_meta_input_smell",
                severity="RISK",
                confidence=0.90,
                file_path=DERIVED_ARTIFACTS_REL,
                evidence=["Derived artifact registry missing/invalid; run-meta input safety cannot be proven."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DERIVED-ARTIFACT-CONTRACT"],
                related_paths=[DERIVED_ARTIFACTS_REL],
            )
        )
        return findings

    rows = ((payload.get("record") or {}).get("artifacts") or [])
    if not isinstance(rows, list):
        return findings
    for row in rows:
        if not isinstance(row, dict):
            continue
        artifact_id = str(row.get("artifact_id", "")).strip()
        artifact_class = str(row.get("artifact_class", "")).strip().upper()
        path_rel = str(row.get("path", "")).replace("\\", "/").strip("/")
        used_for_gating = bool(row.get("used_for_gating"))
        canonical_hash_required = bool(row.get("canonical_hash_required"))
        if artifact_class != "RUN_META":
            continue
        evidence = []
        if used_for_gating:
            evidence.append("{} marks RUN_META as used_for_gating=true".format(artifact_id or path_rel))
        if canonical_hash_required:
            evidence.append("{} marks RUN_META as canonical_hash_required=true".format(artifact_id or path_rel))
        if evidence:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="run_meta_input_smell",
                    severity="VIOLATION",
                    confidence=0.98,
                    file_path=DERIVED_ARTIFACTS_REL,
                    evidence=evidence,
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-DERIVED-ARTIFACT-CONTRACT"],
                    related_paths=[DERIVED_ARTIFACTS_REL, path_rel] if path_rel else [DERIVED_ARTIFACTS_REL],
                )
            )
    return findings
