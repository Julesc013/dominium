"""E320 missing-logic-equivalence-proof smell analyzer for LOGIC-6."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E320_MISSING_LOGIC_EQUIVALENCE_PROOF_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e320_missing_logic_equivalence_proof_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/LOGIC_COMPILATION_MODEL.md",
    "logic/compile/logic_compiler.py",
    "logic/compile/logic_proof_engine.py",
    "tools/xstack/sessionx/process_runtime.py",
    "tools/logic/tool_replay_compiled_logic_window.py",
)


class MissingLogicEquivalenceProofSmell:
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

    doctrine_rel = "docs/logic/LOGIC_COMPILATION_MODEL.md"
    doctrine_text = _read_text(repo_root, doctrine_rel).lower()
    for token in ("equivalence proof", "exact proof", "proof exists and verifies"):
        if token in doctrine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.missing_logic_equivalence_proof_smell",
                severity="RISK",
                confidence=0.85,
                file_path=doctrine_rel,
                line=1,
                evidence=["logic compilation doctrine missing proof token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-COMPILED-LOGIC-REQUIRES-PROOF"],
                related_paths=[doctrine_rel],
            )
        )

    compiler_rel = "logic/compile/logic_compiler.py"
    compiler_text = _read_text(repo_root, compiler_rel)
    for token in (
        "build_logic_equivalence_proof_row(",
        "verify_logic_equivalence_proof",
        "REFUSAL_COMPILE_MISSING_PROOF",
        "proof_requirement_enforced",
    ):
        if token in compiler_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.missing_logic_equivalence_proof_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=compiler_rel,
                line=1,
                evidence=["logic compiler missing proof-enforcement token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPILED-LOGIC-REQUIRES-PROOF"],
                related_paths=[compiler_rel, "logic/compile/logic_proof_engine.py"],
            )
        )

    proof_rel = "logic/compile/logic_proof_engine.py"
    proof_text = _read_text(repo_root, proof_rel)
    for token in ("build_logic_equivalence_proof_row(", "logic_equivalence_proof_hash(", "verify_logic_equivalence_proof("):
        if token in proof_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.missing_logic_equivalence_proof_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=proof_rel,
                line=1,
                evidence=["logic proof engine missing deterministic proof token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPILED-LOGIC-REQUIRES-PROOF"],
                related_paths=[proof_rel, compiler_rel],
            )
        )

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    for token in ('"process.logic_compile_request"', "equivalence_proof_rows", "logic_compile_policy_hash_chain"):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.missing_logic_equivalence_proof_smell",
                severity="RISK",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=["runtime missing logic compile proof propagation token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-COMPILED-LOGIC-REQUIRES-PROOF"],
                related_paths=[runtime_rel, compiler_rel],
            )
        )

    replay_rel = "tools/logic/tool_replay_compiled_logic_window.py"
    replay_text = _read_text(repo_root, replay_rel)
    for token in ("equivalence_proof_hash_chain", "compile_result_hash_chain", "logic_compile_policy_hash_chain"):
        if token in replay_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.missing_logic_equivalence_proof_smell",
                severity="RISK",
                confidence=0.88,
                file_path=replay_rel,
                line=1,
                evidence=["compiled replay tool missing proof-surface token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-COMPILED-LOGIC-REQUIRES-PROOF"],
                related_paths=[replay_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
