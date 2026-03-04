"""E213 missing ledger entry smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E213_MISSING_LEDGER_ENTRY_SMELL"


class MissingLedgerEntrySmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _registered_transform_ids(repo_root: str) -> set[str]:
    payload = _read_json(repo_root, "data/registries/energy_transformation_registry.json")
    rows = list(payload.get("energy_transformations") or [])
    if not isinstance(rows, list):
        rows = list((dict(payload.get("record") or {})).get("energy_transformations") or [])
    out: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("transformation_id", "")).strip()
        if token:
            out.add(token)
    return out


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_ledger_entry_smell",
                severity="RISK",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["process runtime missing; cannot verify PHYS-3 ledger entry hooks"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-ENERGY-TRANSFORM-REGISTERED",
                ],
                related_paths=[runtime_rel],
            )
        )
        return findings

    required_tokens = (
        "_record_energy_transformation_in_state(",
        "_record_boundary_flux_event_in_state(",
        "energy_ledger_hash_chain",
        "boundary_flux_hash_chain",
    )
    for token in required_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_ledger_entry_smell",
                severity="RISK",
                confidence=0.88,
                file_path=runtime_rel,
                line=1,
                evidence=["required PHYS-3 ledger integration token missing", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-ENERGY-TRANSFORM-REGISTERED",
                ],
                related_paths=[runtime_rel],
            )
        )

    required_transform_hooks = (
        "transform.kinetic_to_thermal",
        "transform.electrical_to_thermal",
        "transform.chemical_to_thermal",
        "transform.potential_to_kinetic",
    )
    registered = _registered_transform_ids(repo_root)
    for transform_id in required_transform_hooks:
        if transform_id not in registered:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.missing_ledger_entry_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path="data/registries/energy_transformation_registry.json",
                    line=1,
                    evidence=["required transform id missing in registry", transform_id],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-ENERGY-TRANSFORM-REGISTERED",
                    ],
                    related_paths=["data/registries/energy_transformation_registry.json"],
                )
            )
            continue
        if transform_id in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_ledger_entry_smell",
                severity="RISK",
                confidence=0.8,
                file_path=runtime_rel,
                line=1,
                evidence=["registered transform id is not referenced by runtime ledger routing", transform_id],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-ENERGY-TRANSFORM-REGISTERED",
                ],
                related_paths=[runtime_rel, "data/registries/energy_transformation_registry.json"],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
