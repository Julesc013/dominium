"""E99 instrument truth leak smell analyzer for interior readouts."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E99_INSTRUMENT_TRUTH_LEAK_SMELL"
OBSERVATION_PATH = "tools/xstack/sessionx/observation.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
REQUIRED_OBSERVATION_TOKENS = (
    "_instrument_channel_view(",
    "instrument.interior.pressure",
    "instrument.interior.oxygen",
    "instrument.interior.smoke",
    "instrument.interior.flood",
    "instrument.interior.alarm",
)
FORBIDDEN_OBSERVATION_TOKENS = (
    "compartment_states",
    "interior_leak_hazards",
    "portal_flow_params",
)
REQUIRED_RUNTIME_TOKENS = (
    "process.compartment_flow_tick",
    "instrument.interior.pressure",
    "instrument.interior.alarm",
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
                evidence=["observation integration file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                related_paths=[OBSERVATION_PATH],
            )
        )
    else:
        for token in REQUIRED_OBSERVATION_TOKENS:
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
                    evidence=["missing required interior instrument token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                    related_paths=[OBSERVATION_PATH],
                )
            )
        for token in FORBIDDEN_OBSERVATION_TOKENS:
            if token not in observation_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetics.instrument_truth_leak_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=OBSERVATION_PATH,
                    line=1,
                    evidence=["observation references interior truth-state token directly", token],
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
                confidence=0.9,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime integration file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
    else:
        for token in REQUIRED_RUNTIME_TOKENS:
            if token in runtime_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diegetics.instrument_truth_leak_smell",
                    severity="RISK",
                    confidence=0.85,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["runtime path missing expected interior instrumentation token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-TRUTH-LEAK-IN-INSTRUMENTS"],
                    related_paths=[PROCESS_RUNTIME_PATH],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
