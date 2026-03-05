"""E267 template bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E267_TEMPLATE_BYPASS_SMELL"


class TemplateBypassSmell:
    analyzer_id = ANALYZER_ID


_DIRECT_TEMPLATE_WRITE_PATTERN = re.compile(
    r"\b(?:system_template_instance_record_rows|template_instance_record_hash_chain|compiled_template_fingerprint_hash_chain)\b.*=",
    re.IGNORECASE,
)

_DIRECT_COMPILE_CALL_PATTERN = re.compile(r"\bcompile_system_template\s*\(", re.IGNORECASE)


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

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    compiler_rel = "src/system/templates/template_compiler.py"
    process_registry_rel = "data/registries/process_registry.json"
    runtime_text = _read_text(repo_root, runtime_rel)

    for token in (
        'elif process_id == "process.template_instantiate":',
        "compile_system_template(",
        "create_plan_artifact(",
        "create_commitment_row(",
        "system_template_instance_record_rows",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.template_bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["missing SYS-4 runtime token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-PREFAB-BYPASS"],
                related_paths=[runtime_rel, compiler_rel, process_registry_rel],
            )
        )

    process_registry_text = _read_text(repo_root, process_registry_rel)
    if '"process_id": "process.template_instantiate"' not in process_registry_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.template_bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=process_registry_rel,
                line=1,
                evidence=["process.template_instantiate declaration missing from process registry"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-PREFAB-BYPASS"],
                related_paths=[process_registry_rel],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
        os.path.join(repo_root, "tools"),
    )
    skip_prefixes = (
        "docs/",
        "schema/",
        "schemas/",
        "tools/auditx/analyzers/",
        "tools/xstack/testx/tests/",
    )
    allowed_files = {
        runtime_rel,
        compiler_rel,
        "tools/system/tool_verify_template_reproducible.py",
        "tools/system/tool_template_browser.py",
        "tools/xstack/repox/check.py",
    }
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
                    if _DIRECT_TEMPLATE_WRITE_PATTERN.search(snippet):
                        findings.append(
                            make_finding(
                                analyzer_id=ANALYZER_ID,
                                category="architecture.template_bypass_smell",
                                severity="RISK",
                                confidence=0.9,
                                file_path=rel_path,
                                line=line_no,
                                evidence=[
                                    "potential direct template instance state mutation outside canonical runtime path",
                                    snippet[:140],
                                ],
                                suggested_classification="NEEDS_REVIEW",
                                recommended_action="REWRITE",
                                related_invariants=["INV-NO-PREFAB-BYPASS"],
                                related_paths=[rel_path, runtime_rel],
                            )
                        )
                        break
                    if _DIRECT_COMPILE_CALL_PATTERN.search(snippet):
                        findings.append(
                            make_finding(
                                analyzer_id=ANALYZER_ID,
                                category="architecture.template_bypass_smell",
                                severity="RISK",
                                confidence=0.86,
                                file_path=rel_path,
                                line=line_no,
                                evidence=[
                                    "template compiler call detected outside approved runtime/tools",
                                    snippet[:140],
                                ],
                                suggested_classification="NEEDS_REVIEW",
                                recommended_action="REWRITE",
                                related_invariants=["INV-NO-PREFAB-BYPASS"],
                                related_paths=[rel_path, compiler_rel],
                            )
                        )
                        break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

