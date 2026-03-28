"""E66 silent failure smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E66_SILENT_FAILURE_SMELL"
DECAY_ENGINE_PATH = "materials/maintenance/decay_engine.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
ALLOWED_MUTATION_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/testx/tests/",
)
MUTATION_TOKENS = (
    "state[\"asset_health_states\"]",
    "state[\"failure_events\"]",
    "state[\"maintenance_commitments\"]",
    "state[\"maintenance_provenance_events\"]",
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
    findings = []

    decay_text = _read_text(repo_root, DECAY_ENGINE_PATH)
    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    required_decay_tokens = (
        "_failure_event(",
        "_provenance_event(",
        "tick_decay(",
        "failed_mode_ids",
    )
    required_runtime_tokens = (
        "process.decay_tick",
        "_persist_maintenance_state(",
        "failure_events",
        "maintenance_provenance_events",
    )

    if not decay_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.silent_failure_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=DECAY_ENGINE_PATH,
                line=1,
                evidence=["maintenance decay engine file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-FAILURES"],
                related_paths=[DECAY_ENGINE_PATH],
            )
        )
    else:
        for token in required_decay_tokens:
            if token in decay_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.silent_failure_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=DECAY_ENGINE_PATH,
                    line=1,
                    evidence=["decay engine missing required failure/provenance token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-SILENT-FAILURES"],
                    related_paths=[DECAY_ENGINE_PATH],
                )
            )

    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.silent_failure_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-FAILURES"],
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
                    category="materials.silent_failure_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["process runtime missing required failure process token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-SILENT-FAILURES"],
                    related_paths=[PROCESS_RUNTIME_PATH],
                )
            )

    candidate_files = []
    changed_tokens = sorted(set(_norm(path) for path in list(changed_files or []) if isinstance(path, str)))
    if changed_tokens:
        for rel_path in changed_tokens:
            if rel_path.endswith(".py"):
                candidate_files.append(rel_path)
    else:
        for root in ("src", "tools/xstack/sessionx"):
            abs_root = os.path.join(repo_root, root.replace("/", os.sep))
            if not os.path.isdir(abs_root):
                continue
            for walk_root, _dirs, files in os.walk(abs_root):
                for name in files:
                    if not name.endswith(".py"):
                        continue
                    candidate_files.append(_norm(os.path.relpath(os.path.join(walk_root, name), repo_root)))

    for rel_path in sorted(set(candidate_files)):
        if rel_path.startswith(ALLOWED_MUTATION_PREFIXES):
            continue
        for line_no, line in _iter_lines(repo_root, rel_path):
            token = str(line).strip()
            if not token:
                continue
            if not any(item in token for item in MUTATION_TOKENS):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.silent_failure_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["maintenance/failure state mutated outside process-only mutation boundary", token[:140]],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-SILENT-FAILURES"],
                    related_paths=[rel_path],
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

