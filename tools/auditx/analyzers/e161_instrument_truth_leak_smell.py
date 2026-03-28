"""E161 instrument truth leak smell analyzer for MOB-10 vehicle dashboards."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E161_INSTRUMENT_TRUTH_LEAK_SMELL"
OBSERVATION_PATH = "tools/xstack/sessionx/observation.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
INSPECTION_PATH = "inspection/inspection_engine.py"
REQUIRED_VEHICLE_INSTRUMENT_TOKENS = (
    "instrument.vehicle.pressure",
    "instrument.vehicle.oxygen",
    "instrument.vehicle.smoke_alarm",
    "instrument.vehicle.flood_alarm",
)
REQUIRED_CHANNEL_TOKENS = (
    "ch.diegetic.vehicle.pressure",
    "ch.diegetic.vehicle.oxygen",
    "ch.diegetic.vehicle.smoke_alarm",
    "ch.diegetic.vehicle.flood_alarm",
)
FORBIDDEN_OBSERVATION_TRUTH_TOKENS = (
    "compartment_states",
    "interior_leak_hazards",
    "portal_flow_params",
)


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

    observation_text = _read_text(repo_root, OBSERVATION_PATH)
    if not observation_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="diegetics.instrument_truth_leak_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=OBSERVATION_PATH,
                line=1,
                evidence=["observation file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                related_paths=[OBSERVATION_PATH],
            )
        )
    else:
        for token in REQUIRED_VEHICLE_INSTRUMENT_TOKENS + REQUIRED_CHANNEL_TOKENS:
            if token in observation_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetics.instrument_truth_leak_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=OBSERVATION_PATH,
                    line=1,
                    evidence=["missing vehicle dashboard instrument or channel token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                    related_paths=[OBSERVATION_PATH],
                )
            )
        for token in FORBIDDEN_OBSERVATION_TRUTH_TOKENS:
            if token not in observation_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetics.instrument_truth_leak_smell",
                    severity="RISK",
                    confidence=0.89,
                    file_path=OBSERVATION_PATH,
                    line=1,
                    evidence=["observation still references interior truth token directly", token],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                    related_paths=[OBSERVATION_PATH],
                )
            )

    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="diegetics.instrument_truth_leak_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
    else:
        for token in REQUIRED_VEHICLE_INSTRUMENT_TOKENS:
            if token in runtime_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetics.instrument_truth_leak_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["runtime missing expected vehicle dashboard instrument token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                    related_paths=[PROCESS_RUNTIME_PATH],
                )
            )

    inspection_text = _read_text(repo_root, INSPECTION_PATH)
    if inspection_text:
        if "section.vehicle.pressure_map" in inspection_text and "_quantize_map(" not in inspection_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetics.instrument_truth_leak_smell",
                    severity="RISK",
                    confidence=0.82,
                    file_path=INSPECTION_PATH,
                    line=1,
                    evidence=["vehicle pressure map present without quantization helper usage"],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                    related_paths=[INSPECTION_PATH],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
