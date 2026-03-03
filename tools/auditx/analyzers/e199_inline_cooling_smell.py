"""E199 inline cooling smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E199_INLINE_COOLING_SMELL"


class InlineCoolingSmell:
    analyzer_id = ANALYZER_ID


_INLINE_COOLING_PATTERN = re.compile(
    r"\b(?:ambient_coupling_coefficient|forced_cooling_multiplier|radiator_profile_id|radiator_exchange|ambient_exchange)\b[^\n]*(?:=|\.append\(|\.extend\()",
    re.IGNORECASE,
)

_EXEMPT_SNIPPET_TOKENS = (
    "model_type.therm_ambient_exchange",
    "model_type.therm_radiator_exchange",
    "model.therm_ambient_exchange",
    "model.therm_radiator_exchange",
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
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "src/thermal/network/thermal_network_engine.py",
        "src/models/model_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
        "tools/xstack/repox/check.py",
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
                    if not _INLINE_COOLING_PATTERN.search(snippet):
                        continue
                    lower = snippet.lower()
                    if any(token in lower for token in _EXEMPT_SNIPPET_TOKENS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.inline_cooling_smell",
                            severity="RISK",
                            confidence=0.84,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["cooling/ambient expression detected outside thermal model pathway", snippet[:140]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-ADHOC-COOLING", "INV-THERM-AMBIENT-THROUGH-MODEL"],
                            related_paths=[
                                rel_path,
                                "src/thermal/network/thermal_network_engine.py",
                                "src/models/model_engine.py",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

