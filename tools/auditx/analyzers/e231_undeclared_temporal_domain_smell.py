"""E231 undeclared temporal domain smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E231_UNDECLARED_TEMPORAL_DOMAIN_SMELL"

_SCHEDULE_SCHEMA_REL = "schemas/schedule.schema.json"

_REQUIRED_TOKENS = {
    "schema/core/schedule.schema": (
        "temporal_domain_id",
    ),
    "core/schedule/schedule_engine.py": (
        "_normalize_temporal_domain_id(",
        "\"temporal_domain_id\": temporal_domain_id",
    ),
    "signals/aggregation/aggregation_engine.py": (
        "_normalize_temporal_domain_id(",
        "\"temporal_domain_id\": _normalize_temporal_domain_id(",
    ),
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _file_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _schema_findings(repo_root: str) -> list:
    findings = []
    abs_path = os.path.join(repo_root, _SCHEDULE_SCHEMA_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="time.undeclared_temporal_domain_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=_SCHEDULE_SCHEMA_REL,
                line=1,
                evidence=["schedule schema missing or invalid"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-SCHEDULE-DOMAIN-DECLARED",
                ],
                related_paths=[_SCHEDULE_SCHEMA_REL],
            )
        ]

    properties = payload.get("properties")
    temporal_prop = dict(properties.get("temporal_domain_id") or {}) if isinstance(properties, dict) else {}
    if not temporal_prop:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="time.undeclared_temporal_domain_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=_SCHEDULE_SCHEMA_REL,
                line=1,
                evidence=["schedule schema does not declare temporal_domain_id property"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-SCHEDULE-DOMAIN-DECLARED",
                ],
                related_paths=[_SCHEDULE_SCHEMA_REL],
            )
        )

    required = list(payload.get("required") or [])
    if "temporal_domain_id" not in required:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="time.undeclared_temporal_domain_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=_SCHEDULE_SCHEMA_REL,
                line=1,
                evidence=["schedule schema required fields omit temporal_domain_id"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-SCHEDULE-DOMAIN-DECLARED",
                ],
                related_paths=[_SCHEDULE_SCHEMA_REL],
            )
        )
    return findings


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    findings.extend(_schema_findings(repo_root))

    for rel_path, tokens in _REQUIRED_TOKENS.items():
        text = _file_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="time.undeclared_temporal_domain_smell",
                    severity="VIOLATION",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["required temporal-domain integration surface missing or unreadable"],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=[
                        "INV-SCHEDULE-DOMAIN-DECLARED",
                    ],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="time.undeclared_temporal_domain_smell",
                    severity="VIOLATION",
                    confidence=0.88,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing temporal-domain declaration token '{}'".format(token)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-SCHEDULE-DOMAIN-DECLARED",
                    ],
                    related_paths=[rel_path],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
