"""E46 transition thrash smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E46_TRANSITION_THRASH_SMELL"
TRANSITION_CONTROLLER_PATH = "reality/transitions/transition_controller.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
TRANSITION_POLICY_REGISTRY_PATH = "data/registries/transition_policy_registry.json"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


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

    controller_text = _read_text(repo_root, TRANSITION_CONTROLLER_PATH)
    if not controller_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.transition_thrash_smell",
                severity="RISK",
                confidence=0.9,
                file_path=TRANSITION_CONTROLLER_PATH,
                line=1,
                evidence=["transition controller missing for thrash checks"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                related_paths=[TRANSITION_CONTROLLER_PATH],
            )
        )
    else:
        for token in (
            "min_transition_interval_ticks",
            "last_transition_tick",
            "if min_transition_interval_ticks > 0:",
            "current_active",
            "desired_active",
        ):
            if token in controller_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="reality.transition_thrash_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=TRANSITION_CONTROLLER_PATH,
                    line=1,
                    evidence=[
                        "missing transition anti-thrash token",
                        token,
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                    related_paths=[TRANSITION_CONTROLLER_PATH],
                )
            )

    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.transition_thrash_smell",
                severity="RISK",
                confidence=0.9,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime missing for transition thrash checks"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
    else:
        for token in (
            "compute_transition_plan(",
            "last_transition_tick",
            "row[\"last_transition_tick\"] = int(current_tick)",
            "transition_events",
        ):
            if token in runtime_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="reality.transition_thrash_smell",
                    severity="RISK",
                    confidence=0.84,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=[
                        "transition runtime missing anti-thrash integration token",
                        token,
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-TRANSITION-EVENT-RECORDED"],
                    related_paths=[PROCESS_RUNTIME_PATH],
                )
            )

    registry_abs = os.path.join(repo_root, TRANSITION_POLICY_REGISTRY_PATH.replace("/", os.sep))
    try:
        registry_payload = json.load(open(registry_abs, "r", encoding="utf-8"))
    except (OSError, ValueError):
        registry_payload = {}
    rows = list((registry_payload.get("record") or {}).get("policies") or [])
    if not rows:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.transition_thrash_smell",
                severity="RISK",
                confidence=0.85,
                file_path=TRANSITION_POLICY_REGISTRY_PATH,
                line=1,
                evidence=["transition policy registry is missing or empty"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                related_paths=[TRANSITION_POLICY_REGISTRY_PATH],
            )
        )
    else:
        has_positive_hysteresis = False
        for row in rows:
            if not isinstance(row, dict):
                continue
            policy_id = str(row.get("transition_policy_id", "")).strip() or "transition.policy.unknown"
            hysteresis = dict(row.get("hysteresis_rules") or {})
            if "min_transition_interval_ticks" not in hysteresis:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="reality.transition_thrash_smell",
                        severity="WARN",
                        confidence=0.79,
                        file_path=TRANSITION_POLICY_REGISTRY_PATH,
                        line=1,
                        evidence=["policy missing hysteresis min_transition_interval_ticks", policy_id],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                        related_paths=[TRANSITION_POLICY_REGISTRY_PATH],
                    )
                )
                continue
            value = int(hysteresis.get("min_transition_interval_ticks", 0) or 0)
            if value > 0:
                has_positive_hysteresis = True
        if not has_positive_hysteresis:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="reality.transition_thrash_smell",
                    severity="WARN",
                    confidence=0.72,
                    file_path=TRANSITION_POLICY_REGISTRY_PATH,
                    line=1,
                    evidence=["all transition policies use zero hysteresis interval"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                    related_paths=[TRANSITION_POLICY_REGISTRY_PATH],
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
