"""E432 nondeterministic repro-bundle ordering smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E432_NONDETERMINISTIC_BUNDLE_ORDERING_SMELL"
REQUIRED_TOKENS = {
    "docs/diag/REPRO_BUNDLE_MODEL.md": (
        "Bundle directory ordering is deterministic",
        "sort by relative path",
        "proof-anchor window hash equivalence",
    ),
    "src/diag/repro_bundle_builder.py": (
        "sorted(bundle_files",
        'canonical_sha256({"files": file_rows})',
        '"proof_window_hash"',
        '"canonical_event_hash"',
        '"log_window_hash"',
    ),
    "tools/diag/tool_replay_bundle.py": (
        "Replay a deterministic DIAG-0 repro bundle.",
        "replay_diag0_bundle(",
    ),
    "tools/xstack/testx/tests/test_bundle_hash_stable.py": (
        "repro bundle hash is stable across repeated captures",
    ),
}
FORBIDDEN_TOKENS = {
    "src/diag/repro_bundle_builder.py": ("random.", "uuid.uuid4(", "os.urandom(", "time.time(", "datetime.utcnow("),
    "tools/diag/tool_replay_bundle.py": ("random.", "uuid.uuid4(", "os.urandom("),
}


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
    related_paths = sorted(set(REQUIRED_TOKENS.keys()) | set(FORBIDDEN_TOKENS.keys()))
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diag.nondeterministic_bundle_ordering_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required DIAG-0 repro bundle surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-REPRO-BUNDLE-DETERMINISTIC",
                    ],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diag.nondeterministic_bundle_ordering_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing DIAG-0 ordering marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-REPRO-BUNDLE-DETERMINISTIC",
                    ],
                    related_paths=related_paths,
                )
            )
    for rel_path, tokens in FORBIDDEN_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        found = [token for token in tokens if token in text]
        if found:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="diag.nondeterministic_bundle_ordering_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden nondeterministic repro-bundle token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-REPRO-BUNDLE-DETERMINISTIC",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
