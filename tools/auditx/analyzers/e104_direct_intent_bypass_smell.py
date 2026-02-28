"""E104 direct intent bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E104_DIRECT_INTENT_BYPASS_SMELL"

ALLOWED_PATHS = {
    "src/control/control_plane_engine.py",
    "src/client/interaction/interaction_dispatch.py",
    "src/net/srz/shard_coordinator.py",
    "src/net/policies/policy_server_authoritative.py",
}


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

    for root, _dirs, files in os.walk(repo_root):
        for name in files:
            if not name.endswith(".py"):
                continue
            abs_path = os.path.join(root, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            if not rel_path.startswith("src/"):
                continue
            if rel_path.startswith(
                (
                    "tools/xstack/testx/tests/",
                    "tests/",
                    "tools/xstack/out/",
                    "tools/auditx/analyzers/",
                )
            ):
                continue
            text = _read_text(repo_root, rel_path)
            if not text:
                continue
            if rel_path in ALLOWED_PATHS:
                continue
            has_execute_call = ("execute_intent(" in text) and ("def execute_intent(" not in text)
            has_envelope_builder = ("build_client_intent_envelope(" in text) or ("_build_envelope(" in text)
            if (not has_execute_call) and (not has_envelope_builder):
                continue
            evidence = []
            if has_execute_call:
                evidence.append("execute_intent(")
            if "build_client_intent_envelope(" in text:
                evidence.append("build_client_intent_envelope(")
            elif "_build_envelope(" in text:
                evidence.append("_build_envelope(")
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.direct_intent_bypass_smell",
                    severity="RISK",
                    confidence=0.89,
                    file_path=rel_path,
                    line=1,
                    evidence=evidence + ["direct intent dispatch detected outside canonical pipeline"],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-CONTROL-PLANE-ONLY-DISPATCH"],
                    related_paths=[rel_path],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
