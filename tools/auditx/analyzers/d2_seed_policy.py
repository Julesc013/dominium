"""D2 Seed policy analyzer."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "D2_SEED_POLICY"
WATCH_PREFIXES = (
    "worldgen/",
    "tools/worldgen_offline/",
    "tools/xstack/sessionx/",
    "packs/",
    "schemas/worldgen_constraints.schema.json",
)

SOURCE_PATHS = (
    "worldgen/core/constraint_solver.py",
    "worldgen/core/constraint_commands.py",
    "worldgen/core/pipeline.py",
    "tools/worldgen_offline/constraints_cli.py",
    "tools/xstack/sessionx/creator.py",
)

NONDETERMINISTIC_TOKENS = (
    "import random",
    "from random import",
    "random.",
    "import secrets",
    "from secrets import",
    "secrets.",
    "uuid.uuid4(",
    "time.time(",
    "datetime.now(",
)


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _read_json(path: str) -> Tuple[Dict[str, object], str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid_json"
    if not isinstance(payload, dict):
        return {}, "invalid_object"
    return payload, ""


def _worldgen_constraint_payloads(repo_root: str) -> List[Tuple[str, Dict[str, object]]]:
    out: List[Tuple[str, Dict[str, object]]] = []
    packs_root = os.path.join(repo_root, "packs")
    if not os.path.isdir(packs_root):
        return out
    for root, dirs, files in os.walk(packs_root):
        dirs[:] = sorted(dirs)
        if "pack.json" not in files:
            continue
        manifest_path = os.path.join(root, "pack.json")
        manifest, err = _read_json(manifest_path)
        if err:
            continue
        contributions = manifest.get("contributions")
        if not isinstance(contributions, list):
            continue
        manifest_rel = os.path.relpath(manifest_path, repo_root).replace("\\", "/")
        for row in contributions:
            if not isinstance(row, dict):
                continue
            if str(row.get("type", "")).strip() != "worldgen_constraints":
                continue
            contrib_path = str(row.get("path", "")).strip()
            payload_rel = os.path.normpath(os.path.join(os.path.dirname(manifest_rel), contrib_path)).replace("\\", "/")
            payload, payload_err = _read_json(os.path.join(repo_root, payload_rel.replace("/", os.sep)))
            if payload_err:
                continue
            out.append((payload_rel, payload))
    return sorted(out, key=lambda item: item[0])


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel in SOURCE_PATHS:
        text = _read_text(os.path.join(repo_root, rel.replace("/", os.sep)))
        if not text:
            continue
        lowered = text.lower()
        for token in NONDETERMINISTIC_TOKENS:
            if token in lowered:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="worldgen.seed_policy",
                        severity="VIOLATION",
                        confidence=0.95,
                        file_path=rel,
                        evidence=[
                            "Nondeterministic seed source token detected in worldgen/seed control path.",
                            "token={}".format(token),
                        ],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-DETERMINISTIC-SEED-POLICY"],
                        related_paths=[rel],
                    )
                )

    for rel_path, payload in _worldgen_constraint_payloads(repo_root):
        policy = str(payload.get("deterministic_seed_policy", "")).strip()
        try:
            candidate_count = int(payload.get("candidate_count", 0))
        except (TypeError, ValueError):
            candidate_count = 0
        tie_break = str(payload.get("tie_break_policy", "")).strip()
        refusal_codes = sorted(
            set(str(item).strip() for item in (payload.get("refusal_codes") or []) if str(item).strip())
        )

        if policy not in ("single", "multi"):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.seed_policy",
                    severity="RISK",
                    confidence=0.88,
                    file_path=rel_path,
                    evidence=["Unsupported deterministic_seed_policy value.", "policy={}".format(policy)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-DETERMINISTIC-SEED-POLICY"],
                    related_paths=[rel_path],
                )
            )
        if candidate_count < 1:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.seed_policy",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    evidence=["candidate_count must be >= 1.", "candidate_count={}".format(candidate_count)],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-DETERMINISTIC-SEED-POLICY"],
                    related_paths=[rel_path],
                )
            )
        if policy == "single" and candidate_count != 1:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.seed_policy",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    evidence=["single policy must use exactly one candidate seed.", "candidate_count={}".format(candidate_count)],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-DETERMINISTIC-SEED-POLICY"],
                    related_paths=[rel_path],
                )
            )
        if tie_break not in ("lexicographic", "seed_order", "explicit_field"):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.seed_policy",
                    severity="WARN",
                    confidence=0.8,
                    file_path=rel_path,
                    evidence=["Unsupported tie_break_policy.", "tie_break_policy={}".format(tie_break)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=["INV-DETERMINISTIC-SEED-POLICY"],
                    related_paths=[rel_path],
                )
            )
        required_refusals = {"refusal.constraints_unsatisfiable", "refusal.search_exhausted"}
        if not required_refusals.issubset(set(refusal_codes)):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="worldgen.seed_policy",
                    severity="WARN",
                    confidence=0.78,
                    file_path=rel_path,
                    evidence=[
                        "Constraints refusal_codes missing canonical search refusal codes.",
                        "required={}".format(",".join(sorted(required_refusals))),
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=["INV-DETERMINISTIC-SEED-POLICY"],
                    related_paths=[rel_path],
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
