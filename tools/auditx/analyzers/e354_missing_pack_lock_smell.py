"""E354 missing pack lock smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E354_MISSING_PACK_LOCK_SMELL"
WATCH_PREFIXES = ("tools/mvp/", "data/session_templates/", "profiles/bundles/", "locks/")
REQUIRED_FILES = {
    "tools/mvp/runtime_entry.py": ("--pack_lock", "pack_lock_path="),
    "tools/mvp/runtime_bundle.py": ("build_pack_lock_payload(", "pack_lock_hash", "MVP_PACK_LOCK_REL"),
    "data/session_templates/session.mvp_default.json": ("pack_lock_hash", "profile.bundle.mvp_default"),
    "profiles/bundles/bundle.mvp_default.json": ("pack_lock.mvp_default", "profile.bundle.mvp_default"),
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_watch_candidates(repo_root: str, changed_files=None):
    if changed_files:
        for rel_path in sorted(set(_norm(path) for path in (changed_files or []))):
            if any(rel_path.startswith(prefix) for prefix in WATCH_PREFIXES):
                yield rel_path
        return

    for prefix in WATCH_PREFIXES:
        abs_root = os.path.join(repo_root, prefix.replace("/", os.sep))
        if os.path.isfile(abs_root):
            yield _norm(os.path.relpath(abs_root, repo_root))
            continue
        if not os.path.isdir(abs_root):
            continue
        for walk_root, _dirs, files in os.walk(abs_root):
            for name in sorted(files):
                yield _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))


def run(graph, repo_root, changed_files=None):
    del graph
    findings = []

    for rel_path, required_tokens in sorted(REQUIRED_FILES.items()):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.missing_pack_lock_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required MVP bootstrap artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-PACK-LOCK-REQUIRED", "INV-PROFILE-BUNDLE-REQUIRED"],
                    related_paths=[rel_path, "locks/pack_lock.mvp_default.json"],
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if not missing:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_pack_lock_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing pack-lock marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-PACK-LOCK-REQUIRED", "INV-PROFILE-BUNDLE-REQUIRED"],
                related_paths=[rel_path, "locks/pack_lock.mvp_default.json", "profiles/bundles/bundle.mvp_default.json"],
            )
        )

    candidate_rows = []
    for rel_path in _iter_watch_candidates(repo_root, changed_files=changed_files):
        rel_norm = _norm(rel_path)
        if rel_norm in REQUIRED_FILES:
            continue
        candidate_rows.append(rel_norm)

    for rel_path in sorted(set(candidate_rows)):
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        normalized = text.replace("\\", "/")
        if "profile_bundle" not in normalized and "session.mvp_default" not in normalized:
            continue
        if "pack_lock" in normalized or "pack_lock_hash" in normalized:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_pack_lock_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                line=1,
                evidence=["bootstrap surface references profile/session bundle without pack lock companion marker"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-PACK-LOCK-REQUIRED"],
                related_paths=[rel_path, "locks/pack_lock.mvp_default.json"],
            )
        )
    return findings
