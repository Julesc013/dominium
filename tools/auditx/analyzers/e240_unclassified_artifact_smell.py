"""E240 unclassified artifact smell analyzer."""

from __future__ import annotations

import json
import os
from typing import List, Set

from analyzers.base import make_finding


ANALYZER_ID = "E240_UNCLASSIFIED_ARTIFACT_SMELL"


class UnclassifiedArtifactSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = (
    "data/registries/info_artifact_family_registry.json",
    "data/registries/provenance_classification_registry.json",
)

_INFO_REGISTRY_REL = "data/registries/info_artifact_family_registry.json"
_CLASSIFICATION_REGISTRY_REL = "data/registries/provenance_classification_registry.json"


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _info_artifact_types(payload: dict) -> Set[str]:
    rows = list((dict(payload.get("record") or {})).get("artifact_type_mappings") or [])
    return {
        str(row.get("artifact_type_id", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("artifact_type_id", "")).strip()
    }


def _classified_artifact_types(payload: dict) -> Set[str]:
    rows = list((dict(payload.get("record") or {})).get("provenance_classifications") or [])
    return {
        str(row.get("artifact_type_id", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("artifact_type_id", "")).strip()
    }


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    info_payload = _read_json(repo_root, _INFO_REGISTRY_REL)
    class_payload = _read_json(repo_root, _CLASSIFICATION_REGISTRY_REL)
    info_types = _info_artifact_types(info_payload)
    class_types = _classified_artifact_types(class_payload)

    findings: List[object] = []
    if not info_types:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unclassified_artifact_smell",
                severity="RISK",
                confidence=0.9,
                file_path=_INFO_REGISTRY_REL,
                line=1,
                evidence=["info artifact mapping registry missing or empty"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-DERIVED-ONLY-COMPACTABLE"],
                related_paths=[_INFO_REGISTRY_REL, _CLASSIFICATION_REGISTRY_REL],
            )
        )
        return findings
    if not class_types:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unclassified_artifact_smell",
                severity="RISK",
                confidence=0.95,
                file_path=_CLASSIFICATION_REGISTRY_REL,
                line=1,
                evidence=["provenance classification registry missing or empty"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-DERIVED-ONLY-COMPACTABLE"],
                related_paths=[_INFO_REGISTRY_REL, _CLASSIFICATION_REGISTRY_REL],
            )
        )
        return findings

    missing = sorted(artifact_type for artifact_type in info_types if artifact_type not in class_types)
    if missing:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unclassified_artifact_smell",
                severity="RISK",
                confidence=0.98,
                file_path=_CLASSIFICATION_REGISTRY_REL,
                line=1,
                evidence=[
                    "artifact types mapped in META-INFO are missing provenance classification (count={})".format(len(missing)),
                    ",".join(missing[:12]),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-DERIVED-ONLY-COMPACTABLE"],
                related_paths=[_INFO_REGISTRY_REL, _CLASSIFICATION_REGISTRY_REL],
            )
        )
    return findings
