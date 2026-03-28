"""E430 nondeterministic supervisor smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E430_NONDETERMINISTIC_SUPERVISOR_SMELL"
REQUIRED_TOKENS = {
    "docs/appshell/SUPERVISOR_MODEL.md": (
        "deterministic run manifest",
        "Argument ordering must be stable and canonical.",
        "Supervisor ordering must remain deterministic across platforms and thread counts.",
    ),
    "appshell/supervisor/supervisor_engine.py": (
        "build_supervisor_run_spec(",
        "_build_run_manifest(",
        "canonical_sha256(",
        "self._aggregated_logs = sorted(",
    ),
    "tools/appshell/supervisor_service.py": (
        "SupervisorEngine(",
        "engine.start()",
        "engine.wait_for_shutdown()",
    ),
    "tools/appshell/tool_replay_supervisor.py": (
        "verify_supervisor_replay(",
        "Replay deterministic APPSHELL-6 supervision and verify manifest/log stability.",
    ),
}
FORBIDDEN_TOKENS = {
    "appshell/supervisor/supervisor_engine.py": ("random.", "uuid.uuid4(", "secrets.", "os.urandom("),
    "tools/appshell/supervisor_service.py": ("random.", "uuid.uuid4(", "secrets.", "os.urandom("),
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
    related_paths = sorted(set(REQUIRED_TOKENS.keys()) | set(FORBIDDEN_TOKENS.keys()))
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.supervisor.nondeterministic_supervisor_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required APPSHELL-6 supervisor surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-SUPERVISOR-DETERMINISTIC",
                        "INV-LOG-MERGE-STABLE",
                    ],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.supervisor.nondeterministic_supervisor_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing APPSHELL-6 supervisor marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-SUPERVISOR-DETERMINISTIC",
                        "INV-LOG-MERGE-STABLE",
                    ],
                    related_paths=related_paths,
                )
            )
    for rel_path, tokens in FORBIDDEN_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        found = [token for token in tokens if token in text]
        if found:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.supervisor.nondeterministic_supervisor_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden nondeterministic supervisor token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-SUPERVISOR-DETERMINISTIC",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
