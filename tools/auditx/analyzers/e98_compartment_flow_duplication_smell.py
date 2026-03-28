"""E98 compartment flow duplication smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E98_COMPARTMENT_FLOW_DUPLICATION_SMELL"
REQUIRED_FILES = {
    "interior/compartment_flow_builder.py": (
        "normalize_flow_channel(",
        "build_compartment_flow_channels(",
        "channel.interior.",
    ),
    "interior/compartment_flow_engine.py": (
        "tick_flow_channels(",
        "build_compartment_flow_channels(",
        "_pressure_from_air_mass(",
    ),
}
SCAN_EXCLUDE_PREFIXES = (
    "src/interior/",
    "src/core/flow/",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_py_paths(repo_root: str):
    src_root = os.path.join(repo_root, "src")
    if not os.path.isdir(src_root):
        return
    for base, _dirs, files in os.walk(src_root):
        for name in files:
            if not str(name).endswith(".py"):
                continue
            abs_path = os.path.join(base, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    for rel_path, tokens in sorted(REQUIRED_FILES.items(), key=lambda item: str(item[0])):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="interior.compartment_flow_duplication_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["required compartment flow substrate file missing"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-INTERIOR-FLOWS-USE-FLOWSYSTEM", "INV-NO-ADHOC-CFD"],
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
                    category="interior.compartment_flow_duplication_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing required compartment flow token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-INTERIOR-FLOWS-USE-FLOWSYSTEM", "INV-NO-ADHOC-CFD"],
                    related_paths=[rel_path],
                )
            )

    for rel_path in sorted(_iter_py_paths(repo_root) or []):
        if rel_path.startswith(SCAN_EXCLUDE_PREFIXES):
            continue
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        suspicious_tokens = (
            "air_mass" in text
            and "water_volume" in text
            and "portal" in text
            and "tick_flow_channels(" not in text
            and "build_compartment_flow_channels(" not in text
            and "from interior" not in text
            and "import interior" not in text
        )
        if not suspicious_tokens:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interior.compartment_flow_duplication_smell",
                severity="RISK",
                confidence=0.85,
                file_path=rel_path,
                line=1,
                evidence=["possible ad-hoc interior compartment flow logic outside substrate", "air_mass", "water_volume"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-INTERIOR-FLOWS-USE-FLOWSYSTEM", "INV-NO-ADHOC-CFD"],
                related_paths=[rel_path],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
