"""E415 pack loaded without compatibility validation smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E415_PACK_LOADED_WITHOUT_COMPAT_VALIDATION_SMELL"
REQUIRED_TOKENS = {
    "src/packs/compat/pack_compat_validator.py": (
        "validate_pack_compat_manifest(",
        "REFUSAL_PACK_CONTRACT_MISMATCH",
        "REFUSAL_PACK_MISSING_REGISTRY",
    ),
    "tools/xstack/pack_loader/loader.py": (
        "attach_pack_compat_manifest(",
        "\"compat_manifest_path\"",
        "compat_errors",
        "compat_warnings",
    ),
    "tools/xstack/registry_compile/compiler.py": (
        "\"compat_manifest_hash\"",
        "\"pack_degrade_mode_id\"",
        "load_pack_set(",
    ),
    "tools/xstack/registry_compile/lockfile.py": (
        "\"compat_manifest_hash\"",
        "\"pack_degrade_mode_id\"",
        "compute_pack_lock_hash(",
    ),
    "tools/mvp/runtime_bundle.py": (
        "attach_pack_compat_manifest(",
        "\"compat_manifest_hash\"",
        "\"pack_degrade_mode_id\"",
        "source_pack_lock_hash",
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
                    category="packs.pack_loaded_without_compat_validation_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required pack compatibility validation surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-PACK-COMPAT-VALIDATED-BEFORE-LOAD",
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
                    category="packs.pack_loaded_without_compat_validation_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing pack-compat validation marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-PACK-COMPAT-VALIDATED-BEFORE-LOAD",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
