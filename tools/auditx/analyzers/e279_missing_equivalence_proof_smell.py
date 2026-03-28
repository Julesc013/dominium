"""E279 missing equivalence proof smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E279_MISSING_EQUIVALENCE_PROOF_SMELL"


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

    compile_engine_rel = "meta/compile/compile_engine.py"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_registry_rel = "data/registries/process_registry.json"
    schema_rel = "schema/meta/equivalence_proof.schema"

    for rel in (compile_engine_rel, runtime_rel, process_registry_rel, schema_rel):
        if os.path.isfile(os.path.join(repo_root, rel.replace("/", os.sep))):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_equivalence_proof_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel,
                line=1,
                evidence=["required COMPILE-0 proof artifact missing", rel],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPILED-MODEL-REQUIRES-PROOF"],
                related_paths=[compile_engine_rel, runtime_rel, process_registry_rel, schema_rel],
            )
        )

    compile_engine_text = _read_text(repo_root, compile_engine_rel)
    for token in (
        "build_equivalence_proof_row(",
        "REFUSAL_COMPILE_MISSING_PROOF",
        "equivalence_proof_ref",
    ):
        if token in compile_engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_equivalence_proof_smell",
                severity="RISK",
                confidence=0.92,
                file_path=compile_engine_rel,
                line=1,
                evidence=["compile engine missing proof-enforcement token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPILED-MODEL-REQUIRES-PROOF"],
                related_paths=[compile_engine_rel, runtime_rel],
            )
        )

    runtime_text = _read_text(repo_root, runtime_rel)
    for token in (
        "equivalence_proof_rows",
        "_refresh_compile_hash_chains(state)",
        "proof_requirement_enforced",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_equivalence_proof_smell",
                severity="RISK",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=["runtime missing compile proof propagation token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPILED-MODEL-REQUIRES-PROOF"],
                related_paths=[runtime_rel, compile_engine_rel],
            )
        )

    process_registry_text = _read_text(repo_root, process_registry_rel)
    for token in (
        '"process_id": "process.compile_request_submit"',
        "dominium.schema.meta.equivalence_proof@1.0.0",
    ):
        if token in process_registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_equivalence_proof_smell",
                severity="RISK",
                confidence=0.9,
                file_path=process_registry_rel,
                line=1,
                evidence=["process registry missing compile proof schema linkage", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPILED-MODEL-REQUIRES-PROOF"],
                related_paths=[process_registry_rel, runtime_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
