"""AuditX security boundary and secret hygiene analyzer."""

from __future__ import annotations

import os
import re
from typing import List

from analyzers.base import make_finding


ANALYZER_ID = "C1"
WATCH_PREFIXES = ("engine/", "game/", "client/", "server/", "launcher/", "setup/", "tools/", "docs/security/")

SOURCE_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".py", ".json", ".md"}
SECRET_RE = re.compile(r"(AKIA[0-9A-Z]{16}|BEGIN[ ]+PRIVATE[ ]+KEY|password\\s*=\\s*['\\\"])", re.IGNORECASE)


def _iter_files(repo_root: str) -> List[str]:
    out: List[str] = []
    for root_name in ("engine", "game", "client", "server", "launcher", "setup", "tools"):
        root = os.path.join(repo_root, root_name)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in {".git", ".vs", "out", "dist", "__pycache__"}]
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() not in SOURCE_EXTS:
                    continue
                out.append(os.path.join(dirpath, filename))
    out.sort()
    return out


def run(_graph, repo_root, changed_files=None):
    findings = []
    changed_set = set((changed_files or []))
    for path in _iter_files(repo_root):
        rel = os.path.relpath(path, repo_root).replace("\\", "/")
        if changed_files and rel not in changed_set:
            continue
        try:
            text = open(path, "r", encoding="utf-8").read()
        except OSError:
            continue
        lowered = text.lower()

        if SECRET_RE.search(text):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="security.secret_hygiene",
                    severity="RISK",
                    confidence=0.8,
                    file_path=rel,
                    evidence=["secret-like token detected"],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-UNLOCKED-DEPENDENCY"],
                    related_paths=[rel],
                )
            )

        for token in ("bypass_law_profile", "disable_epistemic_guard", "override_authority_state"):
            if token in lowered:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="security.privilege_bypass",
                        severity="VIOLATION",
                        confidence=0.9,
                        file_path=rel,
                        evidence=[token],
                        suggested_classification="INVALID",
                        recommended_action="ADD_TEST",
                        related_invariants=["INV-SECUREX-PRIVILEGE-MODEL"],
                        related_paths=[rel],
                    )
                )
        if rel.startswith(("client/", "launcher/", "setup/")) and "open(" in lowered and "scripts/dev" not in rel:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="security.boundary_io",
                    severity="WARN",
                    confidence=0.6,
                    file_path=rel,
                    evidence=["direct file I/O token in client boundary"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-SECUREX-TRUST-POLICY-VALID"],
                    related_paths=[rel],
                )
            )
    return findings

