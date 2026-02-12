"""C5 Experience profile drift analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "C5_EXPERIENCE_PROFILE_DRIFT"


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
    exp_rel = os.path.join("data", "registries", "experience_profiles.json")
    law_rel = os.path.join("data", "registries", "law_profiles.json")
    param_rel = os.path.join("data", "registries", "parameter_bundles.json")
    exp_payload = _load_json(os.path.join(repo_root, exp_rel))
    law_payload = _load_json(os.path.join(repo_root, law_rel))
    param_payload = _load_json(os.path.join(repo_root, param_rel))
    if not isinstance(exp_payload, dict) or not isinstance(law_payload, dict) or not isinstance(param_payload, dict):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="experience_profile_drift",
                severity="RISK",
                confidence=0.85,
                file_path=exp_rel.replace("\\", "/"),
                evidence=["Experience/law/parameter registries are missing or invalid JSON."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_TEST",
                related_invariants=["INV-MODE-AS-PROFILES"],
                related_paths=[exp_rel.replace("\\", "/"), law_rel.replace("\\", "/"), param_rel.replace("\\", "/")],
            )
        )
        return findings

    law_ids = set()
    for row in ((law_payload.get("record") or {}).get("profiles") or []):
        if isinstance(row, dict):
            value = str(row.get("law_profile_id", "")).strip()
            if value:
                law_ids.add(value)

    bundle_ids = set()
    for row in ((param_payload.get("record") or {}).get("bundles") or []):
        if isinstance(row, dict):
            value = str(row.get("parameter_bundle_id", "")).strip()
            if value:
                bundle_ids.add(value)

    for row in sorted(((exp_payload.get("record") or {}).get("profiles") or []), key=lambda item: str(item.get("experience_id", "")) if isinstance(item, dict) else ""):
        if not isinstance(row, dict):
            continue
        exp_id = str(row.get("experience_id", "")).strip()
        law_id = str(row.get("law_profile_id", "")).strip()
        bundle_id = str(row.get("default_parameter_bundle_id", "")).strip()
        if exp_id and law_id and law_id not in law_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="experience_profile_drift",
                    severity="RISK",
                    confidence=0.90,
                    file_path=exp_rel.replace("\\", "/"),
                    evidence=["Experience '{}' references missing law profile '{}'".format(exp_id, law_id)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-MODE-AS-PROFILES"],
                    related_paths=[exp_rel.replace("\\", "/"), law_rel.replace("\\", "/")],
                )
            )
        if exp_id and bundle_id and bundle_id not in bundle_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="experience_profile_drift",
                    severity="WARN",
                    confidence=0.85,
                    file_path=exp_rel.replace("\\", "/"),
                    evidence=["Experience '{}' references missing parameter bundle '{}'".format(exp_id, bundle_id)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-MODE-AS-PROFILES"],
                    related_paths=[exp_rel.replace("\\", "/"), param_rel.replace("\\", "/")],
                )
            )

    return findings
