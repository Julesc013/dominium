"""E111 intent bypass smell analyzer."""

from __future__ import annotations

import fnmatch
import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E111_INTENT_BYPASS_SMELL"
WATCH_PREFIXES = (
    "src/",
    "tools/xstack/sessionx/",
    "data/registries/intent_dispatch_whitelist.json",
)

WHITELIST_REL = "data/registries/intent_dispatch_whitelist.json"
DEFAULT_PATTERNS = (
    "src/net/**",
    "src/control/**",
    "tools/xstack/testx/tests/**",
)

REQUIRED_MARKERS = (
    '"envelope_id"',
    '"payload_schema_id"',
    '"pack_lock_hash"',
    '"authority_summary"',
)
BUILDER_TOKENS = (
    "build_client_intent_envelope(",
    "_build_envelope(",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_patterns(repo_root: str):
    abs_path = os.path.join(repo_root, WHITELIST_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return list(DEFAULT_PATTERNS), "missing or invalid whitelist registry"
    if not isinstance(payload, dict):
        return list(DEFAULT_PATTERNS), "invalid whitelist root object"
    record = payload.get("record")
    if not isinstance(record, dict):
        return list(DEFAULT_PATTERNS), "missing whitelist record"
    rows = record.get("allowed_file_patterns")
    if not isinstance(rows, list):
        return list(DEFAULT_PATTERNS), "missing allowed_file_patterns"
    patterns = sorted(set(_norm(str(item).strip()) for item in rows if str(item).strip()))
    if not patterns:
        return list(DEFAULT_PATTERNS), "empty allowed_file_patterns"
    return patterns, ""


def _path_allowed(rel_path: str, patterns):
    token = _norm(rel_path)
    for pattern in list(patterns or []):
        if fnmatch.fnmatch(token, _norm(pattern)):
            return True
    return False


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    patterns, err = _load_patterns(repo_root)
    if err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.intent_bypass_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=WHITELIST_REL,
                line=1,
                evidence=[err],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-CONTROL-PLANE-ONLY-DISPATCH"],
                related_paths=[WHITELIST_REL],
            )
        )

    roots = (os.path.join(repo_root, "src"),)
    for abs_root in roots:
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(("tools/xstack/testx/tests/", "tools/xstack/out/", "tools/auditx/analyzers/", "tests/")):
                    continue
                try:
                    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                if not text:
                    continue
                has_literal = all(marker in text for marker in REQUIRED_MARKERS)
                has_builder = any(marker in text for marker in BUILDER_TOKENS)
                if (not has_literal) and (not has_builder):
                    continue
                if _path_allowed(rel_path, patterns):
                    continue
                snippet = "intent envelope construction markers"
                if has_builder:
                    snippet = (
                        "build_client_intent_envelope("
                        if "build_client_intent_envelope(" in text
                        else "_build_envelope("
                    )
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="architecture.intent_bypass_smell",
                        severity="VIOLATION",
                        confidence=0.94,
                        file_path=rel_path,
                        line=1,
                        evidence=[snippet, "intent envelope construction outside whitelist"],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-CONTROL-PLANE-ONLY-DISPATCH"],
                        related_paths=[rel_path, WHITELIST_REL],
                    )
                )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
