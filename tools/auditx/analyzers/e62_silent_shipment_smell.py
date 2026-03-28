"""E62 silent shipment smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E62_SILENT_SHIPMENT_SMELL"
LOGISTICS_ENGINE_PATH = "logistics/logistics_engine.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
ALLOWED_MUTATION_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/testx/tests/",
)
MUTATION_TOKENS = (
    "state[\"logistics_manifests\"]",
    "state[\"shipment_commitments\"]",
    "state[\"logistics_node_inventories\"]",
    "state[\"logistics_provenance_events\"]",
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

    engine_text = _read_text(repo_root, LOGISTICS_ENGINE_PATH)
    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    required_engine_tokens = (
        "shipment_depart",
        "shipment_arrive",
        "shipment_lost",
        "create_manifest_and_commitment(",
        "tick_manifests(",
    )
    required_runtime_tokens = (
        "process.manifest_create",
        "process.manifest_tick",
        "_persist_logistics_state(",
    )

    if not engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.silent_shipment_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=LOGISTICS_ENGINE_PATH,
                line=1,
                evidence=["logistics engine file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-TRANSFER"],
                related_paths=[LOGISTICS_ENGINE_PATH],
            )
        )
    else:
        for token in required_engine_tokens:
            if token in engine_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.silent_shipment_smell",
                    severity="RISK",
                    confidence=0.87,
                    file_path=LOGISTICS_ENGINE_PATH,
                    line=1,
                    evidence=["logistics engine missing required shipment/provenance token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-SILENT-TRANSFER"],
                    related_paths=[LOGISTICS_ENGINE_PATH],
                )
            )

    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.silent_shipment_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-MANIFESTS-PROCESS-ONLY"],
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
                    category="materials.silent_shipment_smell",
                    severity="RISK",
                    confidence=0.85,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["process runtime missing required logistics process token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-MANIFESTS-PROCESS-ONLY"],
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
                    category="materials.silent_shipment_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["logistics state mutated outside process-only mutation boundary", token[:140]],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-MANIFESTS-PROCESS-ONLY"],
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
