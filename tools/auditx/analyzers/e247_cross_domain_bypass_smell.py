"""E247 cross-domain bypass smell analyzer for CHEM degradation couplings."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E247_CROSS_DOMAIN_BYPASS_SMELL"


class CrossDomainBypassSmell:
    analyzer_id = ANALYZER_ID


_PATTERNS_BY_PREFIX = {
    "src/chem/": (
        re.compile(r"\bfluid_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bthermal_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bmech_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\belec_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']fluid_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']thermal_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']mech_", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']elec_", re.IGNORECASE),
    ),
    "src/fluid/": (
        re.compile(r"\bchem_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']chem_", re.IGNORECASE),
    ),
    "src/thermal/": (
        re.compile(r"\bchem_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']chem_", re.IGNORECASE),
    ),
    "src/mechanics/": (
        re.compile(r"\bchem_[a-z0-9_]+\b\s*=", re.IGNORECASE),
        re.compile(r"\bstate\s*\[\s*[\"']chem_", re.IGNORECASE),
    ),
}

_SCAN_PREFIXES = tuple(_PATTERNS_BY_PREFIX.keys())
_SKIP_PREFIXES = (
    "docs/",
    "schema/",
    "schemas/",
    "tools/auditx/analyzers/",
    "tools/xstack/testx/tests/",
)
_ALLOWED_FILES = {
    "src/models/model_engine.py",
    "tools/xstack/sessionx/process_runtime.py",
    "tools/xstack/repox/check.py",
}
_COUPLING_REGISTRY_REL = "data/registries/coupling_contract_registry.json"


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
        os.path.join(repo_root, "src", "chem"),
        os.path.join(repo_root, "src", "fluid"),
        os.path.join(repo_root, "src", "thermal"),
        os.path.join(repo_root, "src", "mechanics"),
    )
    for scan_root in scan_roots:
        if not os.path.isdir(scan_root):
            continue
        for root, _dirs, files in os.walk(scan_root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(root, name), repo_root))
                if not rel_path.startswith(_SCAN_PREFIXES):
                    continue
                if rel_path.startswith(_SKIP_PREFIXES):
                    continue
                if rel_path in _ALLOWED_FILES:
                    continue
                active_patterns = ()
                for prefix, patterns in _PATTERNS_BY_PREFIX.items():
                    if rel_path.startswith(prefix):
                        active_patterns = patterns
                        break
                if not active_patterns:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not any(pattern.search(snippet) for pattern in active_patterns):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.cross_domain_bypass_smell",
                            severity="RISK",
                            confidence=0.82,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "possible direct cross-domain write detected in CHEM degradation path",
                                snippet[:160],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-COUPLING-CONTRACT-DECLARED",
                                "INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL",
                            ],
                            related_paths=[rel_path, _COUPLING_REGISTRY_REL],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
