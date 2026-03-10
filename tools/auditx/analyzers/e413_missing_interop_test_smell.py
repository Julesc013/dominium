"""E413 missing interop stress coverage analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E413_MISSING_INTEROP_TEST_SMELL"
REQUIRED_TOKENS = {
    "data/regression/cap_neg_full_baseline.json": (
        '"baseline_id": "cap.neg.full.baseline.v1"',
        '"required_commit_tag": "CAP-NEG-REGRESSION-UPDATE"',
        '"scenario_id": "interop.client_server.contract_mismatch_read_only"',
        '"scenario_id": "real.client_server.current_build"',
    ),
    "tools/compat/cap_neg4_common.py": (
        "def generate_interop_matrix(",
        "def run_interop_stress(",
        '"interop.client_server.rendered_to_tui"',
        '"interop.engine_server.compiled_to_l1"',
        '"real.client_server.current_build"',
    ),
    "tools/compat/tool_run_interop_stress.py": (
        "generate_interop_matrix",
        "run_interop_stress",
        "interoperability stress harness",
    ),
}


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
    related_paths = sorted(REQUIRED_TOKENS.keys())
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.interop.missing_interop_test_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required CAP-NEG-4 interop envelope surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NEGOTIATION-STRESS-BASELINES-PRESENT", "INV-DEGRADE-LADDER-COVERAGE"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.interop.missing_interop_test_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing CAP-NEG-4 interop marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NEGOTIATION-STRESS-BASELINES-PRESENT", "INV-DEGRADE-LADDER-COVERAGE"],
                    related_paths=related_paths,
                )
            )
    return findings
