"""E417 nondeterministic pack ordering smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E417_NONDETERMINISTIC_PACK_ORDER_SMELL"
REQUIRED_TOKENS = {
    "docs/packs/PACK_VERIFICATION_PIPELINE.md": (
        "Pack order is canonicalized by `(pack_id, pack_version)`.",
        "All report and lock artifacts use canonical JSON serialization.",
    ),
    "src/packs/compat/pack_verification_pipeline.py": (
        "sorted(out, key=lambda item: (item[\"pack_id\"], item[\"pack_version\"]))",
        "compute_pack_lock_hash(",
        "canonical_json_text(",
    ),
    "tools/xstack/pack_loader/loader.py": (
        "sorted(",
        "pack_id",
        "version",
    ),
    "tools/xstack/testx/tests/test_deterministic_pack_lock_hash.py": (
        "verify_fixture_pack_set(",
        "pack_lock_hash",
    ),
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
    related_paths = list(REQUIRED_TOKENS.keys())
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="packs.nondeterministic_pack_order_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required pack-ordering surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-PACK-LOCK-DETERMINISTIC",
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
                    category="packs.nondeterministic_pack_order_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing deterministic pack-order marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-PACK-LOCK-DETERMINISTIC",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
