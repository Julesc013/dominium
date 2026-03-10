"""E405 ungated authority spawn smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E405_UNGATED_AUTHORITY_SPAWN_SMELL"
REQUIRED_TOKENS = {
    "src/client/local_server/local_server_controller.py": (
        "REFUSAL_LOCAL_AUTHORITY_FORBIDDEN",
        "LOCAL_SERVER_PROFILE_ALLOWLIST",
        "server.profile.private_relaxed",
        "_local_authority_gate(",
        "start_local_singleplayer(",
    ),
    "tools/mvp/runtime_entry.py": (
        "--local-singleplayer",
        "start_local_singleplayer(",
    ),
    "docs/server/LOCAL_SINGLEPLAYER_MODEL.md": (
        "Local authority spawning is profile-driven.",
        "`server.profile.private_relaxed`",
        "`refusal.client.local_authority_forbidden`",
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
                    category="server.local_singleplayer.ungated_authority_spawn_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required local-authority gating surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-LOCAL-SPAWN-PROFILED"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="server.local_singleplayer.ungated_authority_spawn_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing local-authority gate marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-LOCAL-SPAWN-PROFILED"],
                    related_paths=related_paths,
                )
            )
    return findings
