"""E49 unbounded micro expansion smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E49_UNBOUNDED_MICRO_EXPANSION_SMELL"
REGISTRY_PATH = "data/registries/budget_envelope_registry.json"
TRANSITION_CONTROLLER_PATH = "src/reality/transitions/transition_controller.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"


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

    registry_abs = os.path.join(repo_root, REGISTRY_PATH.replace("/", os.sep))
    try:
        registry_payload = json.load(open(registry_abs, "r", encoding="utf-8"))
    except (OSError, ValueError):
        registry_payload = {}
    envelope_rows = list((registry_payload.get("record") or {}).get("envelopes") or [])
    if not envelope_rows:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="performance.unbounded_micro_expansion_smell",
                severity="RISK",
                confidence=0.88,
                file_path=REGISTRY_PATH,
                line=1,
                evidence=["budget envelope registry is missing or empty"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-WALLCLOCK-IN-PERFORMANCE"],
                related_paths=[REGISTRY_PATH],
            )
        )
    else:
        has_positive_caps = False
        for row in envelope_rows:
            if not isinstance(row, dict):
                continue
            max_entities = int(row.get("max_micro_entities_per_shard", 0) or 0)
            max_regions = int(row.get("max_micro_regions_per_shard", 0) or 0)
            max_solver = int(row.get("max_solver_cost_units_per_tick", 0) or 0)
            if max_entities > 0 and max_regions > 0 and max_solver > 0:
                has_positive_caps = True
                break
        if not has_positive_caps:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="performance.unbounded_micro_expansion_smell",
                    severity="RISK",
                    confidence=0.84,
                    file_path=REGISTRY_PATH,
                    line=1,
                    evidence=["no positive micro/entity/solver caps found in budget envelope registry"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-WALLCLOCK-IN-PERFORMANCE"],
                    related_paths=[REGISTRY_PATH],
                )
            )

    transition_text = _read_text(repo_root, TRANSITION_CONTROLLER_PATH)
    if not transition_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="performance.unbounded_micro_expansion_smell",
                severity="RISK",
                confidence=0.9,
                file_path=TRANSITION_CONTROLLER_PATH,
                line=1,
                evidence=["transition controller missing for bounded expansion scan"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TRANSITIONS-POLICY-DRIVEN"],
                related_paths=[TRANSITION_CONTROLLER_PATH],
            )
        )
    else:
        for token in (
            "max_regions",
            "max_entities",
            "max_compute",
            "budget_outcome",
            "refused_expand_ids",
        ):
            if token in transition_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="performance.unbounded_micro_expansion_smell",
                    severity="RISK",
                    confidence=0.83,
                    file_path=TRANSITION_CONTROLLER_PATH,
                    line=1,
                    evidence=["missing bounded-expansion token", token],
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
                category="performance.unbounded_micro_expansion_smell",
                severity="RISK",
                confidence=0.9,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime missing for bounded expansion scan"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-WALLCLOCK-IN-PERFORMANCE"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
    else:
        for token in (
            "normalize_budget_envelope(",
            "compute_cost_snapshot(",
            "budget_outcome",
            "process.region_management_tick",
        ):
            if token in runtime_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="performance.unbounded_micro_expansion_smell",
                    severity="RISK",
                    confidence=0.81,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["missing bounded runtime token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-WALLCLOCK-IN-PERFORMANCE"],
                    related_paths=[PROCESS_RUNTIME_PATH],
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

