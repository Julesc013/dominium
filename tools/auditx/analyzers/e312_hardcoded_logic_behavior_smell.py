"""E312 hardcoded-logic-behavior smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E312_HARDCODED_LOGIC_BEHAVIOR_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e312_hardcoded_logic_behavior_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "src/logic/",
    "packs/core/pack.core.logic_base/",
)

_HARDCODED_PATTERNS = (
    re.compile(r"\blogic\.(?:and|or|not|xor|relay|flip_flop|comparator_scalar|counter_small|timer_delay)\b", re.IGNORECASE),
)


class HardcodedLogicBehaviorSmell:
    analyzer_id = ANALYZER_ID


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

    for root_rel in ("src/logic",):
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for pattern in _HARDCODED_PATTERNS:
                    match = pattern.search(text)
                    if not match:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="logic.hardcoded_logic_behavior_smell",
                            severity="VIOLATION",
                            confidence=0.96,
                            file_path=rel_path,
                            line=1,
                            evidence=["logic runtime references a starter gate id directly", match.group(0)],
                            suggested_classification="INVALID",
                            recommended_action="MOVE_TO_REGISTRY",
                            related_invariants=["INV-NO-HARDCODED-GATES"],
                            related_paths=[rel_path, "packs/core/pack.core.logic_base/data/logic_element_registry.json"],
                        )
                    )
                    break

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
