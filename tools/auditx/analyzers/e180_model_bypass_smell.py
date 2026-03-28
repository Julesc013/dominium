"""E180 model bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E180_MODEL_BYPASS_SMELL"


class ModelBypassSmell:
    analyzer_id = ANALYZER_ID


_BYPASS_PATTERNS = (
    re.compile(
        r"\bmodel_(?:bindings|evaluation_results|cache_rows|runtime_state|hazard_rows|flow_adjustment_rows)\b[^\n]*(?:=|\.append\(|\.extend\(|\.pop\(|\.update\()",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bprocess\.(?:hazard_increment|flow_adjust)\b[^\n]*(?:TODO|bypass|direct)",
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
        "models/model_engine.py",
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
                    if not any(pattern.search(snippet) for pattern in _BYPASS_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.model_bypass_smell",
                            severity="RISK",
                            confidence=0.82,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["constitutive model output/state mutation pattern detected", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-MODEL-OUTPUTS-PROCESS-ONLY"],
                            related_paths=[
                                rel_path,
                                "models/model_engine.py",
                                "tools/xstack/sessionx/process_runtime.py",
                            ],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

