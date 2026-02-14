"""Failure classification helpers for deterministic gate reporting."""

from __future__ import annotations

from enum import Enum
from typing import Dict, Iterable, List


class FailureClass(str, Enum):
    MECHANICAL = "MECHANICAL"
    STRUCTURAL = "STRUCTURAL"
    SEMANTIC = "SEMANTIC"
    SECURITY = "SECURITY"
    DRIFT = "DRIFT"
    PERFORMANCE = "PERFORMANCE"
    POLICY = "POLICY"
    CACHE_CORRUPTION = "CACHE_CORRUPTION"


_MESSAGES = {
    FailureClass.MECHANICAL: "mechanical execution failure",
    FailureClass.STRUCTURAL: "structural contract failure",
    FailureClass.SEMANTIC: "semantic validation failure",
    FailureClass.SECURITY: "security policy failure",
    FailureClass.DRIFT: "governance drift detected",
    FailureClass.PERFORMANCE: "performance ceiling exceeded",
    FailureClass.POLICY: "policy contract failure",
    FailureClass.CACHE_CORRUPTION: "cache integrity failure",
}

_HINTS = {
    FailureClass.MECHANICAL: "verify tool availability, command wiring, and environment setup",
    FailureClass.STRUCTURAL: "validate schema/registry contracts and required structural invariants",
    FailureClass.SEMANTIC: "inspect invariant findings and adjust semantic logic",
    FailureClass.SECURITY: "review trust, privilege, and boundary controls",
    FailureClass.DRIFT: "reconcile artifact and policy drift against canonical baseline",
    FailureClass.PERFORMANCE: "narrow impacted groups or increase sharding granularity",
    FailureClass.POLICY: "apply remediation playbook for violated policy rules",
    FailureClass.CACHE_CORRUPTION: "clear stale cache entries and re-run to repopulate",
}


def _normalize_text(value: object) -> str:
    return str(value or "").strip().lower()


def classify_failure(runner_id: str, exit_code: int, output: str) -> Dict[str, str]:
    if int(exit_code) == 0:
        return {
            "failure_class": "",
            "failure_message": "ok",
            "remediation_hint": "",
        }

    token = _normalize_text(output)
    rid = _normalize_text(runner_id)
    if any(
        flag in token
        for flag in (
            "cache_corruption",
            "input_hash_mismatch",
            "profile_mismatch",
            "version_hash_mismatch",
            "runner_mismatch",
            "entry_hash_mismatch",
            "key_hash_mismatch",
        )
    ):
        klass = FailureClass.CACHE_CORRUPTION
    elif any(flag in token for flag in ("refuse.command_unresolvable", "invalid_runner_command", "tool_discovery")):
        klass = FailureClass.MECHANICAL
    elif "performance ceiling" in token or "performance_alert" in token:
        klass = FailureClass.PERFORMANCE
    elif "security" in rid or "securex" in rid or "refuse.security" in token:
        klass = FailureClass.SECURITY
    elif "drift" in token:
        klass = FailureClass.DRIFT
    elif any(flag in token for flag in ("schema", "registry", "migration", "structural")):
        klass = FailureClass.STRUCTURAL
    elif any(flag in token for flag in ("policy", "refuse.", "forbidden", "contract")):
        klass = FailureClass.POLICY
    else:
        klass = FailureClass.SEMANTIC

    return {
        "failure_class": klass.value,
        "failure_message": _MESSAGES[klass],
        "remediation_hint": _HINTS[klass],
    }


def aggregate_failure_classes(results: Iterable[Dict[str, object]]) -> Dict[str, object]:
    counts: Dict[str, int] = {}
    for row in results:
        if not isinstance(row, dict):
            continue
        token = str(row.get("failure_class", "")).strip().upper()
        if not token:
            continue
        counts[token] = counts.get(token, 0) + 1
    ordered = sorted(({"failure_class": key, "count": int(value)} for key, value in counts.items()), key=lambda row: row["failure_class"])
    primary = ""
    if ordered:
        primary = sorted(ordered, key=lambda row: (-int(row["count"]), str(row["failure_class"])))[0]["failure_class"]
    return {
        "failure_classes": [str(row["failure_class"]) for row in ordered],
        "failure_summary": ordered,
        "primary_failure_class": primary,
    }
