"""E41 implicit default profile smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E41_IMPLICIT_DEFAULT_PROFILE_SMELL"
TOKEN_REQUIREMENTS = {
    "schemas/universe_identity.schema.json": (
        "physics_profile_id",
        "immutable_after_create",
    ),
    "tools/xstack/sessionx/creator.py": (
        "physics_profile_id",
        "select_physics_profile(",
    ),
    "tools/xstack/sessionx/runner.py": (
        "refusal.physics_profile_missing",
        "select_physics_profile(",
    ),
    "tools/xstack/sessionx/net_handshake.py": (
        "refusal.physics_profile_mismatch",
        "server_physics_profile_id",
    ),
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

    for rel_path, tokens in TOKEN_REQUIREMENTS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="reality.implicit_default_profile_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=rel_path,
                    line=1,
                    evidence=["required file missing for implicit default profile checks"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-PHYSICS-PROFILE-IN-IDENTITY"],
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
                    category="reality.implicit_default_profile_smell",
                    severity="WARN",
                    confidence=0.81,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing required RS-1 profile token '{}'".format(token)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-PHYSICS-PROFILE-IN-IDENTITY"],
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
