"""E185 inline power loss smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E185_INLINE_POWER_LOSS_SMELL"


class InlinePowerLossSmell:
    analyzer_id = ANALYZER_ID


_POWER_LOSS_PATTERN = re.compile(
    r"\b(?:loss_p|heat_loss|line_loss|resistance_proxy)\b\s*=\s*[^#\n]*(?:\*|/|\+|-|//)",
    re.IGNORECASE,
)
_PF_INLINE_PATTERN = re.compile(
    r"\b(?:pf|power_factor|pf_permille)\b[^\n]*[=*\/+-]",
    re.IGNORECASE,
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
    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    skip_prefixes = (
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
        "docs/",
        "schema/",
        "schemas/",
    )
    allowed_files = {
        "src/electric/power_network_engine.py",
        "src/models/model_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
    }
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not (_POWER_LOSS_PATTERN.search(snippet) or _PF_INLINE_PATTERN.search(snippet)):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.inline_power_loss_smell",
                            severity="RISK",
                            confidence=0.82,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["inline electrical loss/PF expression detected outside canonical power model", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-POWER-FLOW-THROUGH-BUNDLE"],
                            related_paths=[
                                rel_path,
                                "src/electric/power_network_engine.py",
                                "docs/electric/ELECTRICAL_CONSTITUTION.md",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

