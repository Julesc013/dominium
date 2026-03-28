"""E278 custom compilation smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E278_CUSTOM_COMPILATION_SMELL"


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

    for rel in (compile_engine_rel, runtime_rel, process_registry_rel):
        if os.path.isfile(os.path.join(repo_root, rel.replace("/", os.sep))):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.custom_compilation_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel,
                line=1,
                evidence=["COMPILE-0 required artifact missing", rel],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-BESPOKE-COMPILER"],
                related_paths=[compile_engine_rel, runtime_rel, process_registry_rel],
            )
        )

    runtime_text = _read_text(repo_root, runtime_rel)
    for token in (
        'elif process_id == "process.compile_request_submit":',
        "evaluate_compile_request(",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.custom_compilation_smell",
                severity="RISK",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=["runtime missing COMPILE-0 dispatch token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-BESPOKE-COMPILER"],
                related_paths=[runtime_rel, compile_engine_rel],
            )
        )

    call_pattern = re.compile(r"\bevaluate_compile_request\s*\(", re.IGNORECASE)
    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools"),
    )
    allowed_files = {
        _norm(compile_engine_rel),
        _norm(runtime_rel),
        _norm("process/capsules/capsule_builder.py"),
        _norm("tools/meta/tool_verify_compiled_model.py"),
        _norm("tools/xstack/repox/check.py"),
        _norm("tools/xstack/testx/tests/test_compile_engine_deterministic.py"),
        _norm("tools/xstack/testx/tests/test_recompile_matches_hash.py"),
    }
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
    )
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for walk_root, _dirs, files in os.walk(root):
            for name in files:
                if not name.endswith(".py"):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path.startswith(skip_prefixes):
                    continue
                if rel_path in allowed_files:
                    continue
                text = _read_text(repo_root, rel_path)
                if not text:
                    continue
                for line_no, line in enumerate(text.splitlines(), start=1):
                    snippet = str(line).strip()
                    if (not snippet) or snippet.startswith("#"):
                        continue
                    if not call_pattern.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.custom_compilation_smell",
                            severity="RISK",
                            confidence=0.9,
                            file_path=rel_path,
                            line=line_no,
                            evidence=["compile framework call from non-canonical location", snippet[:140]],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-BESPOKE-COMPILER"],
                            related_paths=[rel_path, compile_engine_rel, runtime_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
