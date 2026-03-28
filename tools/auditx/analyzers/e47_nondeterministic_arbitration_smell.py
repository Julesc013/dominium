"""E47 non-deterministic transition arbitration smell analyzer."""

from __future__ import annotations

import json
import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E47_NONDETERMINISTIC_ARBITRATION_SMELL"
TRANSITION_CONTROLLER_PATH = "reality/transitions/transition_controller.py"
ARBITRATION_REGISTRY_PATH = "data/registries/arbitration_rule_registry.json"
REQUIRED_ARBITRATION_RULE_IDS = (
    "arb.equal_share",
    "arb.priority_by_distance",
    "arb.server_authoritative_weighted",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"\brandom\.", re.IGNORECASE),
    re.compile(r"\bsecrets\.", re.IGNORECASE),
    re.compile(r"\btime\.time\(", re.IGNORECASE),
    re.compile(r"\bdatetime\.now\(", re.IGNORECASE),
    re.compile(r"\buuid\.uuid4\(", re.IGNORECASE),
    re.compile(r"\bos\.urandom\(", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_lines(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            for line_no, line in enumerate(handle, start=1):
                yield line_no, line.rstrip("\n")
    except OSError:
        return


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    controller_text = _read_text(repo_root, TRANSITION_CONTROLLER_PATH)
    if not controller_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.nondeterministic_arbitration_smell",
                severity="RISK",
                confidence=0.9,
                file_path=TRANSITION_CONTROLLER_PATH,
                line=1,
                evidence=["transition controller missing for arbitration determinism scan"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                related_paths=[TRANSITION_CONTROLLER_PATH],
            )
        )
    else:
        for token in (
            "_candidate_sort_key(",
            "sorted(",
            "distance_bucket_mm",
            "arbitration_rule_id",
            "region_id",
        ):
            if token in controller_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="reality.nondeterministic_arbitration_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=TRANSITION_CONTROLLER_PATH,
                    line=1,
                    evidence=[
                        "missing deterministic arbitration token",
                        token,
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                    related_paths=[TRANSITION_CONTROLLER_PATH],
                )
            )

        for line_no, line in _iter_lines(repo_root, TRANSITION_CONTROLLER_PATH):
            for pattern in FORBIDDEN_PATTERNS:
                if not pattern.search(str(line)):
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="reality.nondeterministic_arbitration_smell",
                        severity="VIOLATION",
                        confidence=0.98,
                        file_path=TRANSITION_CONTROLLER_PATH,
                        line=line_no,
                        evidence=[
                            "nondeterministic API usage in arbitration path",
                            str(line).strip()[:140],
                        ],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=[
                            "INV-TRANSITIONS-POLICY-DRIVEN",
                            "INV-NO-WALLCLOCK-IN-TRANSITION",
                        ],
                        related_paths=[TRANSITION_CONTROLLER_PATH],
                    )
                )

    registry_abs = os.path.join(repo_root, ARBITRATION_REGISTRY_PATH.replace("/", os.sep))
    try:
        registry_payload = json.load(open(registry_abs, "r", encoding="utf-8"))
    except (OSError, ValueError):
        registry_payload = {}
    rows = list((registry_payload.get("record") or {}).get("rules") or [])
    if not rows:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.nondeterministic_arbitration_smell",
                severity="RISK",
                confidence=0.86,
                file_path=ARBITRATION_REGISTRY_PATH,
                line=1,
                evidence=["arbitration rule registry is missing or empty"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                related_paths=[ARBITRATION_REGISTRY_PATH],
            )
        )
    else:
        rule_ids = sorted(
            set(str(item.get("rule_id", "")).strip() for item in rows if isinstance(item, dict) and str(item.get("rule_id", "")).strip())
        )
        for rule_id in REQUIRED_ARBITRATION_RULE_IDS:
            if rule_id in rule_ids:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="reality.nondeterministic_arbitration_smell",
                    severity="WARN",
                    confidence=0.81,
                    file_path=ARBITRATION_REGISTRY_PATH,
                    line=1,
                    evidence=["missing required arbitration rule id", rule_id],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                    related_paths=[ARBITRATION_REGISTRY_PATH],
                )
            )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
