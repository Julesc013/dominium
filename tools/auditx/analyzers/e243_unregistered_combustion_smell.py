"""E243 unregistered combustion smell analyzer."""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Mapping, Set

from analyzers.base import make_finding


ANALYZER_ID = "E243_UNREGISTERED_COMBUSTION_SMELL"


class UnregisteredCombustionSmell:
    analyzer_id = ANALYZER_ID


_REACTION_ID_PATTERN = re.compile(r"\breaction\.[A-Za-z0-9_.-]+")


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_json(path: str) -> Dict[str, object]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, Mapping):
        return {}
    return dict(payload)


def _reaction_ids(repo_root: str) -> Set[str]:
    path = os.path.join(repo_root, "data", "registries", "reaction_profile_registry.json")
    payload = _load_json(path)
    rows = list((dict(payload.get("record") or {})).get("reaction_profiles") or [])
    out: Set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        reaction_id = str(row.get("reaction_id", "")).strip()
        if reaction_id:
            out.add(reaction_id)
    return out


def _transform_ids(repo_root: str) -> Set[str]:
    path = os.path.join(repo_root, "data", "registries", "energy_transformation_registry.json")
    payload = _load_json(path)
    rows = list((dict(payload.get("record") or {})).get("energy_transformations") or [])
    out: Set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        transform_id = str(row.get("transformation_id", "")).strip()
        if transform_id:
            out.add(transform_id)
    return out


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    reaction_ids = _reaction_ids(repo_root)
    transform_ids = _transform_ids(repo_root)
    registry_rel = "data/registries/reaction_profile_registry.json"
    transform_rel = "data/registries/energy_transformation_registry.json"
    required_reactions = {
        "reaction.combustion_fuel_basic",
        "reaction.combustion_rich_mixture_stub",
        "reaction.explosive_stub",
    }
    for reaction_id in sorted(required_reactions):
        if reaction_id in reaction_ids:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unregistered_combustion_smell",
                severity="RISK",
                confidence=0.93,
                file_path=registry_rel,
                line=1,
                evidence=["required combustion reaction profile is missing", reaction_id],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REGISTER",
                related_invariants=[
                    "INV-COMBUSTION-THROUGH-REACTION-ENGINE",
                ],
                related_paths=[registry_rel],
            )
        )
    for transform_id in ("transform.chemical_to_thermal", "transform.chemical_to_electrical"):
        if transform_id in transform_ids:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unregistered_combustion_smell",
                severity="RISK",
                confidence=0.93,
                file_path=transform_rel,
                line=1,
                evidence=["required combustion energy transform missing", transform_id],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REGISTER",
                related_invariants=[
                    "INV-ENERGY-TRANSFORM-REGISTERED",
                    "INV-COMBUSTION-THROUGH-REACTION-ENGINE",
                ],
                related_paths=[transform_rel],
            )
        )

    scan_files = (
        "tools/xstack/sessionx/process_runtime.py",
        "src/models/model_engine.py",
        "src/thermal/network/thermal_network_engine.py",
    )
    for rel_path in scan_files:
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if (not snippet) or snippet.startswith("#"):
                continue
            unknown = sorted(
                token
                for token in set(_REACTION_ID_PATTERN.findall(snippet))
                if token and token not in reaction_ids
            )
            if not unknown:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.unregistered_combustion_smell",
                    severity="RISK",
                    confidence=0.81,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["unregistered reaction id literal", snippet[:140], ",".join(unknown)],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="REGISTER",
                    related_invariants=[
                        "INV-COMBUSTION-THROUGH-REACTION-ENGINE",
                    ],
                    related_paths=[rel_path, registry_rel],
                )
            )
            break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
