"""C7 Lens bypass smell analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "C7_LENS_BYPASS_SMELL"


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

    law_rel = "data/registries/law_profiles.json"
    lens_rel = "data/registries/lenses.json"
    law_payload = _load_json(os.path.join(repo_root, law_rel.replace("/", os.sep)))
    lens_payload = _load_json(os.path.join(repo_root, lens_rel.replace("/", os.sep)))

    if not isinstance(law_payload, dict) or not isinstance(lens_payload, dict):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="lens_bypass_smell",
                severity="RISK",
                confidence=0.88,
                file_path=law_rel,
                evidence=["Lens/law registries missing or invalid; lens gating cannot be proven."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-SURVIVAL-NO-NONDIEGETIC-LENSES", "INV-UI-ENTITLEMENT-GATING"],
                related_paths=[law_rel, lens_rel],
            )
        )
        return findings

    lenses = ((lens_payload.get("record") or {}).get("lenses") or [])
    if not isinstance(lenses, list):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="lens_bypass_smell",
                severity="WARN",
                confidence=0.80,
                file_path=lens_rel,
                evidence=["Lens registry lenses list missing/invalid."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_TEST",
                related_invariants=["INV-SURVIVAL-NO-NONDIEGETIC-LENSES"],
                related_paths=[lens_rel],
            )
        )
        return findings

    nondiegetic_ids = set()
    for row in lenses:
        if isinstance(row, dict) and str(row.get("category", "")).strip() == "nondiegetic":
            lens_id = str(row.get("lens_id", "")).strip()
            if lens_id:
                nondiegetic_ids.add(lens_id)

    profiles = ((law_payload.get("record") or {}).get("profiles") or [])
    for row in profiles:
        if not isinstance(row, dict):
            continue
        law_id = str(row.get("law_profile_id", "")).strip()
        if not law_id.startswith("law.survival") and law_id != "survival.softcore":
            continue
        allowed = [str(item).strip() for item in (row.get("allowed_lenses") or [])]
        forbidden = [str(item).strip() for item in (row.get("forbidden_lenses") or [])]
        if "lens.diegetic.*" not in allowed:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="lens_bypass_smell",
                    severity="RISK",
                    confidence=0.90,
                    file_path=law_rel,
                    evidence=["{} missing diegetic allowlist marker lens.diegetic.*".format(law_id)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-SURVIVAL-NO-NONDIEGETIC-LENSES"],
                    related_paths=[law_rel],
                )
            )
        if not any(item.startswith("lens.nondiegetic") for item in forbidden):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="lens_bypass_smell",
                    severity="RISK",
                    confidence=0.92,
                    file_path=law_rel,
                    evidence=["{} missing nondiegetic forbid rule.".format(law_id)],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-SURVIVAL-NO-NONDIEGETIC-LENSES"],
                    related_paths=[law_rel],
                )
            )

    if not nondiegetic_ids:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="lens_bypass_smell",
                severity="WARN",
                confidence=0.70,
                file_path=lens_rel,
                evidence=["Lens registry has no nondiegetic entries; bypass detection is degraded."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=["INV-SURVIVAL-NO-NONDIEGETIC-LENSES"],
                related_paths=[lens_rel],
            )
        )

    return findings
