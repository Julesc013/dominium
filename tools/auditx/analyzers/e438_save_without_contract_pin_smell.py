"""E438 save-without-contract-pin smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E438_SAVE_WITHOUT_CONTRACT_PIN_SMELL"
REQUIRED_TOKENS = {
    "docs/architecture/SAVE_MODEL.md": (
        "INV-SAVE-PINS-CONTRACTS",
        "universe_contract_bundle_hash",
        "pack_lock_hash",
    ),
    "schema/lib/save_manifest.schema": (
        "universe_contract_bundle_hash",
        "pack_lock_hash",
        "allow_read_only_open",
    ),
    "src/lib/save/save_validator.py": (
        "REFUSAL_SAVE_CONTRACT_MISMATCH",
        "load_save_contract_bundle(",
        "save_semantic_contract_registry_hash(",
    ),
    "tools/launcher/launcher_cli.py": (
        "resolve_save_manifest_path(",
        "evaluate_save_open(",
        "save manifest not found",
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
        missing = [token for token in tokens if token not in text]
        if not missing:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="save.save_without_contract_pin_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing save contract-pin marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=[
                    "INV-SAVE-PINS-CONTRACTS",
                    "INV-SAVE-MANIFEST-REQUIRED",
                ],
                related_paths=related_paths,
            )
        )
    return findings
