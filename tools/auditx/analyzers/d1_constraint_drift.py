"""D1 Constraint drift analyzer."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Set, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "D1_CONSTRAINT_DRIFT"
WATCH_PREFIXES = (
    "packs/",
    "data/registries/worldgen_constraints_registry.json",
    "data/registries/worldgen_module_registry.json",
    "schemas/worldgen_constraints.schema.json",
    "worldgen/",
)


def _read_json(path: str) -> Tuple[Dict[str, object], str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid_json"
    if not isinstance(payload, dict):
        return {}, "invalid_object"
    return payload, ""


def _module_outputs(repo_root: str) -> Set[str]:
    path = os.path.join(repo_root, "data", "registries", "worldgen_module_registry.json")
    payload, err = _read_json(path)
    if err:
        return set()
    entries = (((payload.get("record") or {}).get("entries")) or [])
    out: Set[str] = set()
    if not isinstance(entries, list):
        return out
    for row in entries:
        if not isinstance(row, dict):
            continue
        for token in (row.get("outputs") or []):
            text = str(token).strip()
            if text:
                out.add(text)
    return out


def _constraints_registry_entries(repo_root: str) -> List[Dict[str, str]]:
    path = os.path.join(repo_root, "data", "registries", "worldgen_constraints_registry.json")
    payload, err = _read_json(path)
    if err:
        return []
    rows = (((payload.get("record") or {}).get("entries")) or [])
    out = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        constraints_id = str(row.get("constraints_id", "")).strip()
        pack_id = str(row.get("pack_id", "")).strip()
        if constraints_id:
            out.append({"constraints_id": constraints_id, "pack_id": pack_id})
    return sorted(out, key=lambda item: (item["constraints_id"], item["pack_id"]))


def _worldgen_constraint_contribs(repo_root: str) -> List[Dict[str, str]]:
    packs_root = os.path.join(repo_root, "packs")
    out: List[Dict[str, str]] = []
    if not os.path.isdir(packs_root):
        return out
    for root, dirs, files in os.walk(packs_root):
        dirs[:] = sorted(dirs)
        if "pack.json" not in files:
            continue
        manifest_path = os.path.join(root, "pack.json")
        manifest_rel = os.path.relpath(manifest_path, repo_root).replace("\\", "/")
        payload, err = _read_json(manifest_path)
        if err:
            continue
        pack_id = str(payload.get("pack_id", "")).strip()
        contributions = payload.get("contributions")
        if not isinstance(contributions, list):
            continue
        for row in contributions:
            if not isinstance(row, dict):
                continue
            if str(row.get("type", "")).strip() != "worldgen_constraints":
                continue
            contrib_id = str(row.get("id", "")).strip()
            contrib_path = str(row.get("path", "")).strip()
            rel_payload = os.path.normpath(os.path.join(os.path.dirname(manifest_rel), contrib_path)).replace("\\", "/")
            out.append(
                {
                    "manifest": manifest_rel,
                    "pack_id": pack_id,
                    "constraints_id": contrib_id,
                    "payload_path": rel_payload,
                }
            )
    return sorted(out, key=lambda item: (item["constraints_id"], item["pack_id"], item["payload_path"]))


def _targets_from_constraints(payload: Dict[str, object]) -> List[str]:
    targets: Set[str] = set()
    for row in payload.get("hard_constraints") or []:
        if isinstance(row, dict):
            text = str(row.get("target", "")).strip()
            if text:
                targets.add(text)
    for row in payload.get("soft_constraints") or []:
        if isinstance(row, dict):
            text = str(row.get("target", "")).strip()
            if text:
                targets.add(text)
    for row in payload.get("scoring_functions") or []:
        if isinstance(row, dict):
            text = str(row.get("metric", "")).strip()
            if text:
                targets.add(text)
    return sorted(targets)


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    module_outputs = _module_outputs(repo_root)
    registry_entries = _constraints_registry_entries(repo_root)
    registry_ids = {row["constraints_id"] for row in registry_entries}
    contribs = _worldgen_constraint_contribs(repo_root)
    contrib_ids = {row["constraints_id"] for row in contribs}

    for missing_id in sorted(registry_ids - contrib_ids):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="worldgen.constraint_drift",
                severity="RISK",
                confidence=0.9,
                file_path="data/registries/worldgen_constraints_registry.json",
                evidence=[
                    "Registry constraints_id has no matching pack contribution: {}".format(missing_id),
                    "Constraint registry can drift from pack content.",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-WORLDGEN-CONSTRAINTS-REGISTERED"],
                related_paths=["data/registries/worldgen_constraints_registry.json"],
            )
        )

    for row in contribs:
        payload_rel = str(row.get("payload_path", ""))
        payload_abs = os.path.join(repo_root, payload_rel.replace("/", os.sep))
        payload, err = _read_json(payload_abs)
        if err:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.constraint_drift",
                    severity="WARN",
                    confidence=0.8,
                    file_path=payload_rel,
                    evidence=["Unable to parse constraints payload JSON."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_TEST",
                    related_invariants=["INV-CONSTRAINT-SCHEMA-VALID"],
                    related_paths=[payload_rel],
                )
            )
            continue

        constraints_id = str(payload.get("constraints_id", "")).strip() or str(row.get("constraints_id", ""))
        if constraints_id not in registry_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.constraint_drift",
                    severity="RISK",
                    confidence=0.92,
                    file_path=payload_rel,
                    evidence=[
                        "Pack constraints payload is not declared in worldgen constraints registry.",
                        "constraints_id={}".format(constraints_id),
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-WORLDGEN-CONSTRAINTS-REGISTERED"],
                    related_paths=[payload_rel, "data/registries/worldgen_constraints_registry.json"],
                )
            )

        targets = _targets_from_constraints(payload)
        for target in targets:
            if not target.startswith("world.layer."):
                continue
            if target in module_outputs:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.constraint_drift",
                    severity="RISK",
                    confidence=0.86,
                    file_path=payload_rel,
                    evidence=[
                        "Constraint target/metric not found in worldgen module outputs.",
                        "target={}".format(target),
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=["INV-WORLDGEN-CONSTRAINTS-REGISTERED"],
                    related_paths=[payload_rel, "data/registries/worldgen_module_registry.json"],
                )
            )

    return sorted(
        findings,
        key=lambda item: (
            item.location.file_path,
            item.location.line_start,
            item.severity,
        ),
    )
