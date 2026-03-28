"""E304 silent override smell analyzer for unified profile exception logging."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E304_SILENT_OVERRIDE_SMELL"


class SilentOverrideSmell:
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

    profile_engine_rel = "meta/profile/profile_engine.py"
    collapse_rel = "system/system_collapse_engine.py"
    required_profile_tokens = (
        "resolve_profile(",
        "apply_override(",
        "build_profile_exception_event_row(",
        "\"exception_event\"",
    )
    required_collapse_tokens = (
        "_statevec_output_guard_status(",
        "_append_profile_exception_event(",
    )

    profile_engine_text = _read_text(repo_root, profile_engine_rel)
    if not profile_engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="profile.silent_override_smell",
                severity="VIOLATION",
                confidence=0.91,
                file_path=profile_engine_rel,
                line=1,
                evidence=["profile override engine missing; cannot verify exception-ledger emission"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-OVERRIDE-REQUIRES-PROFILE", "INV-EXCEPTION-EVENT-LOGGED"],
                related_paths=[profile_engine_rel],
            )
        )
    else:
        for token in required_profile_tokens:
            if token in profile_engine_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="profile.silent_override_smell",
                    severity="VIOLATION",
                    confidence=0.87,
                    file_path=profile_engine_rel,
                    line=1,
                    evidence=["profile override path missing token '{}'".format(token)],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-EXCEPTION-EVENT-LOGGED"],
                    related_paths=[profile_engine_rel],
                )
            )

    collapse_text = _read_text(repo_root, collapse_rel)
    for token in required_collapse_tokens:
        if token in collapse_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="profile.silent_override_smell",
                severity="RISK",
                confidence=0.82,
                file_path=collapse_rel,
                line=1,
                evidence=["collapse path missing profile override logging token '{}'".format(token)],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-EXCEPTION-EVENT-LOGGED"],
                related_paths=[collapse_rel],
            )
        )

    runtime_roots = ("src", "engine", "game", "client", "server", "launcher", "setup")
    source_exts = {".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp"}
    for root_name in runtime_roots:
        abs_root = os.path.join(repo_root, root_name)
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(name for name in dirs if name not in {".git", "__pycache__", "build", "dist", "out", "legacy"})
            for name in sorted(files):
                if os.path.splitext(name)[1].lower() not in source_exts:
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                text = _read_text(repo_root, rel_path)
                if "debug_profile" not in str(text).lower():
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="profile.silent_override_smell",
                        severity="VIOLATION",
                        confidence=0.92,
                        file_path=rel_path,
                        line=1,
                        evidence=["legacy mode-like override token 'debug_profile' found in runtime path"],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-NO-MODE-FLAGS", "INV-OVERRIDE-REQUIRES-PROFILE"],
                        related_paths=[rel_path],
                    )
                )
                if len(findings) >= 64:
                    return findings

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

