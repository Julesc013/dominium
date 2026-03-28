"""E182 bundle bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E182_BUNDLE_BYPASS_SMELL"


class BundleBypassSmell:
    analyzer_id = ANALYZER_ID


_BYPASS_PATTERNS = (
    re.compile(r"\bif\b[^\n]*quantity_bundle_id[^\n]*\bquantity_id\b", re.IGNORECASE),
    re.compile(r"\bquantity_bundle_id\b[^\n]*(?:fallback|legacy|scalar)", re.IGNORECASE),
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
        os.path.join(repo_root, "src", "core", "flow"),
        os.path.join(repo_root, "src", "models"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
    )
    allowed_files = {
        "core/flow/flow_engine.py",
        "tools/xstack/sessionx/process_runtime.py",
        "models/model_engine.py",
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
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                has_bundle = "quantity_bundle_id" in text
                has_component = "component_quantity_id" in text
                if has_bundle and (not has_component) and ("flow_adjust" in text or "transferred_amount" in text or "lost_amount" in text):
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.bundle_bypass_smell",
                            severity="RISK",
                            confidence=0.78,
                            file_path=rel_path,
                            line=1,
                            evidence=["bundle-aware flow handling appears to bypass component selectors"],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-COUPLED-QUANTITY-HACKS"],
                            related_paths=[rel_path, "core/flow/flow_engine.py", "docs/architecture/QUANTITY_BUNDLES.md"],
                        )
                    )
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
                            category="architecture.bundle_bypass_smell",
                            severity="RISK",
                            confidence=0.76,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["possible bundle bypass pattern detected", snippet[:140]],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-COUPLED-QUANTITY-HACKS"],
                            related_paths=[rel_path, "docs/architecture/QUANTITY_BUNDLES.md"],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
