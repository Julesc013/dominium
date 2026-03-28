"""E269 direct spec bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E269_DIRECT_SPEC_BYPASS_SMELL"


class DirectSpecBypassSmell:
    analyzer_id = ANALYZER_ID


_DIRECT_SPEC_PATTERN = re.compile(
    r"\b(?:latest_spec_binding_for_target|spec_compliance_results|evaluate_compliance)\b",
    re.IGNORECASE,
)


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
    engine_rel = "system/certification/system_cert_engine.py"
    process_registry_rel = "data/registries/process_registry.json"

    runtime_text = _read_text(repo_root, runtime_rel)
    for token in (
        'elif process_id == "process.system_evaluate_certification":',
        "evaluate_system_certification(",
        "process.spec_check_compliance",
        "event.system.certificate_revocation.spec_violation",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.direct_spec_bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["missing SYS-5 runtime token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SPEC-CHECK-THROUGH-CERT-ENGINE"],
                related_paths=[runtime_rel, engine_rel, process_registry_rel],
            )
        )

    process_registry_text = _read_text(repo_root, process_registry_rel)
    if '"process_id": "process.system_evaluate_certification"' not in process_registry_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.direct_spec_bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=process_registry_rel,
                line=1,
                evidence=["process.system_evaluate_certification declaration missing from process registry"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SPEC-CHECK-THROUGH-CERT-ENGINE"],
                related_paths=[process_registry_rel],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src", "system"),
        os.path.join(repo_root, "tools", "xstack", "sessionx"),
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
        engine_rel,
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
                    if not _DIRECT_SPEC_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.direct_spec_bypass_smell",
                            severity="RISK",
                            confidence=0.9,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "potential direct SPEC/compliance pathway detected outside certification runtime/engine",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-SPEC-CHECK-THROUGH-CERT-ENGINE"],
                            related_paths=[rel_path, runtime_rel, engine_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

