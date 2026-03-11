"""E444 nondeterministic LIB-7 bundle/regression smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E444_NONDETERMINISTIC_BUNDLE_SMELL"
REQUIRED_TOKENS = {
    "docs/lib/EXPORT_IMPORT_FORMAT.md": (
        "bundle.instance.portable",
        "`bundle_hash` is computed from the canonical ordered item-hash projection only.",
        "No OS-specific metadata is permitted in archive entries.",
    ),
    "docs/audit/LIB_FINAL_BASELINE.md": (
        "repeated runs keep identical projection hashes",
        "forward- and backslash-shaped scenarios keep identical bundle hashes",
        "`tool_verify_bundle` returns `result=complete`",
    ),
    "tools/lib/lib_stress_common.py": (
        "\"bundle_hash_stable\"",
        "\"projection_hashes\"",
        "\"bundle_verifications\"",
        "\"tool_verify_bundle.py\"",
    ),
    "tools/lib/tool_run_lib_stress.py": (
        "Run the LIB-7 deterministic library stress harness.",
        "--slash-mode",
        "--baseline-out",
    ),
    "data/regression/lib_full_baseline.json": (
        "\"bundle_hashes\"",
        "\"decision_log_fingerprints\"",
        "\"required_commit_tag\": \"LIB-REGRESSION-UPDATE\"",
    ),
}
FORBIDDEN_TOKENS = {
    "tools/lib/lib_stress_common.py": ("time.time(", "datetime.utcnow(", "uuid.uuid4(", "random.", "os.path.getmtime("),
    "tools/lib/tool_run_lib_stress.py": ("time.time(", "datetime.utcnow(", "uuid.uuid4(", "random."),
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
                    category="bundle.nondeterministic_bundle_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required LIB-7 bundle/regression surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-LIB-DETERMINISTIC",
                        "INV-EXPORT-IMPORT-VERIFIED",
                        "INV-BUNDLES-DETERMINISTIC",
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
                    category="bundle.nondeterministic_bundle_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing LIB-7 bundle determinism marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-LIB-DETERMINISTIC",
                        "INV-EXPORT-IMPORT-VERIFIED",
                        "INV-BUNDLES-DETERMINISTIC",
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
                    category="bundle.nondeterministic_bundle_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden nondeterministic bundle token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-LIB-DETERMINISTIC",
                        "INV-EXPORT-IMPORT-VERIFIED",
                        "INV-BUNDLES-DETERMINISTIC",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
