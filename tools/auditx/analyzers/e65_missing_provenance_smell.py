"""E65 missing provenance smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E65_MISSING_PROVENANCE_SMELL"
CONSTRUCTION_ENGINE_PATH = "src/materials/construction/construction_engine.py"
EVENT_TYPE_REGISTRY_PATH = "data/registries/provenance_event_type_registry.json"
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

    engine_text = _read_text(repo_root, CONSTRUCTION_ENGINE_PATH)
    registry_text = _read_text(repo_root, EVENT_TYPE_REGISTRY_PATH)
    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    required_engine_tokens = (
        "event.construct_project_created",
        "event.construct_step_started",
        "event.construct_step_completed",
        "event.material_consumed",
        "event.batch_created",
        "event.install_part",
    )
    required_registry_tokens = (
        "event.construct_project_created",
        "event.construct_step_started",
        "event.construct_step_completed",
        "event.install_part",
        "event.deconstruct_part",
        "event.material_consumed",
        "event.batch_created",
    )
    required_runtime_tokens = (
        "construction_provenance_events",
        "_persist_construction_state(",
        "process.construction_project_tick",
    )

    if not engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.missing_provenance_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=CONSTRUCTION_ENGINE_PATH,
                line=1,
                evidence=["construction engine file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-PROVENANCE-EVENTS-REQUIRED"],
                related_paths=[CONSTRUCTION_ENGINE_PATH],
            )
        )
    else:
        for token in required_engine_tokens:
            if token in engine_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.missing_provenance_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=CONSTRUCTION_ENGINE_PATH,
                    line=1,
                    evidence=["construction engine missing required provenance event token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-PROVENANCE-EVENTS-REQUIRED"],
                    related_paths=[CONSTRUCTION_ENGINE_PATH],
                )
            )

    if not registry_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.missing_provenance_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=EVENT_TYPE_REGISTRY_PATH,
                line=1,
                evidence=["provenance event type registry missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-PROVENANCE-EVENTS-REQUIRED"],
                related_paths=[EVENT_TYPE_REGISTRY_PATH],
            )
        )
    else:
        for token in required_registry_tokens:
            if token in registry_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.missing_provenance_smell",
                    severity="RISK",
                    confidence=0.84,
                    file_path=EVENT_TYPE_REGISTRY_PATH,
                    line=1,
                    evidence=["provenance event type registry missing canonical event token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-PROVENANCE-EVENTS-REQUIRED"],
                    related_paths=[EVENT_TYPE_REGISTRY_PATH],
                )
            )

    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.missing_provenance_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-PROVENANCE-EVENTS-REQUIRED"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
    else:
        for token in required_runtime_tokens:
            if token in runtime_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.missing_provenance_smell",
                    severity="RISK",
                    confidence=0.82,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["process runtime missing required provenance persistence token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-PROVENANCE-EVENTS-REQUIRED"],
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

