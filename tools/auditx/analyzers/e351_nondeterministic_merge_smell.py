"""E351 nondeterministic merge smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E351_NONDETERMINISTIC_MERGE_SMELL"
REQUIRED_FILES = {
    "src/geo/overlay/overlay_merge_engine.py": (
        "_ordered_patches_for_manifest(",
        "sorted(",
        "canonical_sha256(",
        "_merge_cache_store(",
        "overlay_effective_object_hash_chain",
    ),
    "tools/geo/tool_replay_overlay_merge.py": (
        "verify_overlay_merge_replay(",
        "overlay_manifest_hash",
        "property_patch_hash_chain",
        "overlay_merge_result_hash_chain",
        "stable_across_repeated_runs",
    ),
}
WATCH_PREFIXES = ("src/geo/overlay/", "tools/geo/")
_BANNED_TOKENS = ("random.", "uuid", "secrets.", "time.time(", "datetime.now(", "os.urandom(")


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
                yield os.path.relpath(abs_path, repo_root).replace(os.sep, "/")


def run(graph, repo_root, changed_files=None):
    del graph
    findings = []
    for rel_path, required_tokens in sorted(REQUIRED_FILES.items()):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="overlay.nondeterministic_merge_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required GEO-9 overlay merge file is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-OVERLAY-MERGE-DETERMINISTIC"],
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
                category="overlay.nondeterministic_merge_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing GEO-9 merge determinism token(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-OVERLAY-MERGE-DETERMINISTIC"],
                related_paths=[rel_path, "src/geo/overlay/overlay_merge_engine.py"],
            )
        )

    candidates = []
    if changed_files:
        for rel_path in list(changed_files or []):
            rel_norm = str(rel_path).replace(os.sep, "/")
            if rel_norm.endswith(".py") and any(rel_norm.startswith(prefix) for prefix in WATCH_PREFIXES):
                candidates.append(rel_norm)
    else:
        candidates = list(_iter_candidate_files(repo_root))

    for rel_path in sorted(set(candidates)):
        text = _read_text(repo_root, rel_path)
        if not text or "overlay" not in text.lower():
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            if not any(token in snippet for token in _BANNED_TOKENS):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="overlay.nondeterministic_merge_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=[
                        "nondeterministic source detected in GEO-9 overlay merge surface",
                        snippet[:160],
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-OVERLAY-MERGE-DETERMINISTIC"],
                    related_paths=[rel_path, "src/geo/overlay/overlay_merge_engine.py"],
                )
            )
            break
    return findings
