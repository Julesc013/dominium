"""E300 orphan-feature smell analyzer for demand-mapping coverage."""

from __future__ import annotations

import json
import os
import re
from typing import Iterable, Set

from analyzers.base import make_finding


ANALYZER_ID = "E300_ORPHAN_FEATURE_SMELL"


class OrphanFeatureSmell:
    analyzer_id = ANALYZER_ID


PLAYER_DEMAND_MATRIX_REL = "data/meta/player_demand_matrix.json"
IMPACT_DIR_REL = "docs/impact/"
FEATURE_PATH_PREFIXES = (
    "src/",
    "engine/",
    "game/",
    "server/",
    "client/",
    "data/registries/",
    "schema/",
    "packs/system_templates/",
    "tools/domain/",
    "tools/xstack/sessionx/",
)
FEATURE_TOKEN_PATTERNS = (
    re.compile(r"\baction_template_id\b"),
    re.compile(r"\bprocess_id\b"),
    re.compile(r"\bmacro_model_set_id\b"),
    re.compile(r"\btemplate_id\b"),
    re.compile(r"\bcompiled_model_id\b"),
    re.compile(r"\bartifact_type_id\b"),
    re.compile(r"\bcoupling_contract_id\b"),
    re.compile(r"\bexplain\.[a-z0-9_.]+\b", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _load_demand_ids(repo_root: str) -> Set[str]:
    abs_path = os.path.join(repo_root, PLAYER_DEMAND_MATRIX_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    if not isinstance(payload, dict):
        return set()
    rows = list(payload.get("demands") or [])
    out: Set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        demand_id = str(row.get("demand_id", "")).strip()
        if demand_id:
            out.add(demand_id)
    return out


def _extract_demand_refs(text: str, demand_ids: Iterable[str]) -> Set[str]:
    if not text:
        return set()
    return {demand_id for demand_id in demand_ids if demand_id and demand_id in text}


def _has_feature_token(text: str) -> bool:
    if not text:
        return False
    for pattern in FEATURE_TOKEN_PATTERNS:
        if pattern.search(text):
            return True
    return False


def run(graph, repo_root, changed_files=None):
    del graph
    findings = []

    changed = sorted(_norm(path) for path in list(changed_files or []) if str(path).strip())
    if not changed:
        return findings

    demand_ids = _load_demand_ids(repo_root)
    if not demand_ids:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="planning.orphan_feature_smell",
                severity="RISK",
                confidence=0.9,
                file_path=PLAYER_DEMAND_MATRIX_REL,
                line=1,
                evidence=["player demand matrix missing or invalid"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_CONTRACT",
                related_invariants=["INV-CHANGE-MUST-REFERENCE-DEMAND"],
                related_paths=[PLAYER_DEMAND_MATRIX_REL],
            )
        )
        return findings

    impact_refs: Set[str] = set()
    changed_impact_files = sorted(
        path
        for path in changed
        if path.startswith(IMPACT_DIR_REL) and path.lower().endswith(".md")
    )
    for rel_path in changed_impact_files:
        impact_refs.update(_extract_demand_refs(_read_text(repo_root, rel_path), demand_ids))

    for rel_path in changed:
        if rel_path.startswith(("docs/", "tools/auditx/analyzers/", "tools/xstack/testx/tests/")):
            continue
        if not rel_path.startswith(FEATURE_PATH_PREFIXES):
            continue
        text = _read_text(repo_root, rel_path)
        if not _has_feature_token(text):
            continue
        refs = set(impact_refs)
        refs.update(_extract_demand_refs(text, demand_ids))
        if refs:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="planning.orphan_feature_smell",
                severity="RISK",
                confidence=0.86,
                file_path=rel_path,
                line=1,
                evidence=[
                    "feature-like change detected without demand mapping",
                    "add demand ids in docs/impact/*.md or adjacent change notes",
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-CHANGE-MUST-REFERENCE-DEMAND"],
                related_paths=[rel_path, PLAYER_DEMAND_MATRIX_REL, IMPACT_DIR_REL],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
