"""Semantic escalation policy helpers for ControlX."""

from __future__ import annotations

from typing import Any, Dict, List


def semantic_keywords(policy: Dict[str, Any]) -> List[str]:
    record = policy.get("record", {}) if isinstance(policy, dict) else {}
    values = record.get("semantic_escalation_keywords", [])
    out = []
    if not isinstance(values, list):
        return out
    for item in values:
        token = str(item).strip().lower()
        if token:
            out.append(token)
    return sorted(set(out))


def detect_semantic_ambiguity(text: str, policy: Dict[str, Any]) -> List[str]:
    lowered = str(text or "").lower()
    found = []
    for token in semantic_keywords(policy):
        if token in lowered:
            found.append(token)
    return sorted(set(found))


def format_semantic_escalation(
    blocker_type: str,
    failed_gate: str,
    root_cause: str,
    attempted_fixes: List[str],
    remaining_options: List[str],
    recommended_option: str,
    rationale: str,
) -> str:
    lines = [
        "BLOCKER TYPE: {}".format(blocker_type),
        "FAILED GATE: {}".format(failed_gate),
        "ROOT CAUSE: {}".format(root_cause),
        "ATTEMPTED FIXES: {}".format("; ".join(item for item in attempted_fixes if item) or "none"),
        "REMAINING SEMANTIC OPTIONS: {}".format("; ".join(item for item in remaining_options if item) or "none"),
        "RECOMMENDED OPTION: {}".format(recommended_option),
        "RATIONALE: {}".format(rationale),
    ]
    return "\n".join(lines)

