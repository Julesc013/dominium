"""E350 silent identity change smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E350_SILENT_IDENTITY_CHANGE_SMELL"
WATCH_PREFIXES = ("src/geo/", "tools/geo/", "tools/xstack/sessionx/")
REQUIRED_FILES = {
    "geo/overlay/overlay_merge_engine.py": (
        "_IMMUTABLE_PROPERTY_PATHS",
        '"object_id"',
        '"identity_hash"',
        '"generator_version_id"',
        "build_property_patch(",
    ),
    "tools/xstack/sessionx/process_runtime.py": (
        '"process.overlay_save_patch"',
        "normalize_property_patch(",
        "_append_save_property_patch(",
    ),
}
_BANNED_PATTERNS = (
    re.compile(
        r"property_path\s*=\s*[\"'](?:object_id|identity_hash|generator_version_id|topology_profile_id|metric_profile_id|partition_profile_id|projection_profile_id)[\"']",
        re.IGNORECASE,
    ),
    re.compile(
        r"[\"']property_path[\"']\s*:\s*[\"'](?:object_id|identity_hash|generator_version_id|topology_profile_id|metric_profile_id|partition_profile_id|projection_profile_id)[\"']",
        re.IGNORECASE,
    ),
)
_SKIP_PREFIXES = ("tools/xstack/testx/tests/", "tools/auditx/analyzers/", "docs/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_candidate_files(repo_root: str):
    for prefix in WATCH_PREFIXES:
        abs_prefix = os.path.join(repo_root, prefix.replace("/", os.sep))
        if not os.path.isdir(abs_prefix):
            continue
        for root, _dirs, files in os.walk(abs_prefix):
            for name in sorted(files):
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(root, name)
                rel_path = os.path.relpath(abs_path, repo_root).replace(os.sep, "/")
                if any(rel_path.startswith(skip) for skip in _SKIP_PREFIXES):
                    continue
                yield rel_path


def run(graph, repo_root, changed_files=None):
    del graph
    findings = []
    for rel_path, required_tokens in sorted(REQUIRED_FILES.items()):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="overlay.silent_identity_change_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required GEO-9 overlay identity guard file is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NO-IDENTITY-OVERRIDE-WITHOUT-MIGRATION"],
                    related_paths=[rel_path],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if not missing:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="overlay.silent_identity_change_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing GEO-9 identity guard token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-IDENTITY-OVERRIDE-WITHOUT-MIGRATION"],
                related_paths=[rel_path, "geo/overlay/overlay_merge_engine.py"],
            )
        )

    candidates = []
    if changed_files:
        for rel_path in list(changed_files or []):
            rel_norm = str(rel_path).replace(os.sep, "/")
            if not rel_norm.endswith(".py"):
                continue
            if any(rel_norm.startswith(prefix) for prefix in WATCH_PREFIXES) and not any(
                rel_norm.startswith(skip) for skip in _SKIP_PREFIXES
            ):
                candidates.append(rel_norm)
    else:
        candidates = list(_iter_candidate_files(repo_root))

    for rel_path in sorted(set(candidates)):
        if rel_path in REQUIRED_FILES:
            continue
        text = _read_text(repo_root, rel_path)
        if not text or ("property_path" not in text and "object_id" not in text):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(pattern.search(snippet) for pattern in _BANNED_PATTERNS):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="overlay.silent_identity_change_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "property patch appears to target immutable identity or universe-lineage fields",
                        snippet[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-IDENTITY-OVERRIDE-WITHOUT-MIGRATION"],
                    related_paths=[rel_path, "geo/overlay/overlay_merge_engine.py"],
                )
            )
            break
    return findings
