"""E311 carrier-bias smell analyzer for LOGIC runtime."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E311_CARRIER_BIAS_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e311_carrier_bias_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "src/logic/",
    "docs/logic/",
)

_FORBIDDEN_PATTERNS = (
    re.compile(r"\bcarrier\.electrical\b", re.IGNORECASE),
    re.compile(r"\bcarrier\.pneumatic\b", re.IGNORECASE),
    re.compile(r"\bcarrier\.hydraulic\b", re.IGNORECASE),
    re.compile(r"\bcarrier\.mechanical\b", re.IGNORECASE),
    re.compile(r"\bcarrier\.optical\b", re.IGNORECASE),
    re.compile(r"\bvoltage\b", re.IGNORECASE),
    re.compile(r"\bcurrent\b", re.IGNORECASE),
    re.compile(r"\bpressure(?:_head)?\b", re.IGNORECASE),
)


class CarrierBiasSmell:
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

    for root_rel in ("src/logic", "tools/logic"):
        abs_root = os.path.join(repo_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                rel_lower = rel_path.lower()
                if "carrier_adapters.py" in rel_lower or rel_path.startswith("tools/xstack/testx/tests/"):
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for pattern in _FORBIDDEN_PATTERNS:
                    match = pattern.search(text)
                    if not match:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="logic.carrier_bias_smell",
                            severity="RISK",
                            confidence=0.9,
                            file_path=rel_path,
                            line=1,
                            evidence=["logic runtime references carrier-specific semantic token outside adapter seam", match.group(0)],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-CARRIER-SEMANTIC-BIAS"],
                            related_paths=[rel_path, "src/logic/signal/carrier_adapters.py"],
                        )
                    )
                    break

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
