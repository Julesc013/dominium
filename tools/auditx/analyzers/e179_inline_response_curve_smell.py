"""E179 inline response curve smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E179_INLINE_RESPONSE_CURVE_SMELL"


class InlineResponseCurveSmell:
    analyzer_id = ANALYZER_ID


_INLINE_RESPONSE_PATTERNS = (
    re.compile(
        r"\b(?:threshold|multiplier|attenuation|friction|wear|drift|derail|curve|coefficient|ratio)\w*\b\s*=\s*[^#\n]*(?:\*|/|\+|-|min\(|max\(|clamp)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bif\b[^\n]*(?:friction|wear|attenuation|curvature|threshold|ratio|temperature|moisture|wind|radiation)\b[^\n]*(?:>=|<=|>|<)",
        re.IGNORECASE,
    ),
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
        os.path.join(repo_root, "src", "fields"),
        os.path.join(repo_root, "src", "mobility"),
        os.path.join(repo_root, "src", "signals"),
        os.path.join(repo_root, "src", "mechanics"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        "src/meta_model/model_engine.py",
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
                    if not any(pattern.search(snippet) for pattern in _INLINE_RESPONSE_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.inline_response_curve_smell",
                            severity="RISK",
                            confidence=0.86,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["inline response-curve logic detected", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-REALISM-DETAIL-MUST-BE-MODEL"],
                            related_paths=[
                                rel_path,
                                "docs/meta/CONSTITUTIVE_MODEL_CONSTITUTION.md",
                                "docs/meta/CONSTITUTIVE_MODEL_CATALOG.md",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
