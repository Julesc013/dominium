"""E239 canonical artifact compaction smell analyzer."""

from __future__ import annotations

import json
import os
from typing import Dict, List

from analyzers.base import make_finding


ANALYZER_ID = "E239_CANONICAL_ARTIFACT_COMPACTION_SMELL"


class CanonicalArtifactCompactionSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = (
    "data/registries/provenance_classification_registry.json",
)

_REGISTRY_REL = "data/registries/provenance_classification_registry.json"


def _read_registry(repo_root: str) -> dict:
    abs_path = os.path.join(repo_root, _REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    payload = _read_registry(repo_root)
    rows = list((dict(payload.get("record") or {})).get("provenance_classifications") or [])
    findings: List[object] = []
    if not rows:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.canonical_artifact_compaction_smell",
                severity="RISK",
                confidence=0.95,
                file_path=_REGISTRY_REL,
                line=1,
                evidence=["missing provenance classification rows; canonical compaction safety cannot be established"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-CANONICAL-EVENT-NOT-DISCARDED",
                    "INV-DERIVED-ONLY-COMPACTABLE",
                ],
                related_paths=[_REGISTRY_REL],
            )
        )
        return findings

    invalid: List[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        artifact_type_id = str(row.get("artifact_type_id", "")).strip()
        classification = str(row.get("classification", "")).strip().lower()
        compaction_allowed = bool(row.get("compaction_allowed", False))
        if classification == "canonical" and compaction_allowed:
            invalid.append(artifact_type_id or "<missing-artifact-type-id>")

    if invalid:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.canonical_artifact_compaction_smell",
                severity="RISK",
                confidence=0.99,
                file_path=_REGISTRY_REL,
                line=1,
                evidence=[
                    "canonical artifacts are marked compactable (count={})".format(len(invalid)),
                    ",".join(sorted(invalid)[:12]),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-CANONICAL-EVENT-NOT-DISCARDED"],
                related_paths=[_REGISTRY_REL],
            )
        )
    return findings
