"""E263 capsule bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E263_CAPSULE_BYPASS_SMELL"


class CapsuleBypassSmell:
    analyzer_id = ANALYZER_ID


_DIRECT_WRITE_PATTERN = re.compile(
    r"\b(?:system_macro_runtime_state_rows|system_macro_output_record_rows|system_forced_expand_event_rows)\b.*=",
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

    macro_engine_rel = "src/system/macro/macro_capsule_engine.py"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"

    macro_text = _read_text(repo_root, macro_engine_rel)
    runtime_text = _read_text(repo_root, runtime_rel)
    for rel_path, token, message in (
        (macro_engine_rel, "def evaluate_macro_capsules_tick(", "macro capsule engine entrypoint missing"),
        (macro_engine_rel, "evaluate_model_bindings(", "macro capsule engine must use constitutive model evaluation"),
        (runtime_rel, "elif process_id == \"process.system_macro_tick\":", "runtime missing process.system_macro_tick branch"),
        (runtime_rel, "evaluate_macro_capsules_tick(", "runtime missing macro capsule engine invocation"),
    ):
        text = macro_text if rel_path == macro_engine_rel else runtime_text
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.capsule_bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=[message, token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-CAPSULE-BEHAVIOR-MODEL-ONLY"],
                related_paths=[macro_engine_rel, runtime_rel],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src"),
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
        macro_engine_rel,
        runtime_rel,
        "src/system/forensics/system_forensics_engine.py",
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
                    if not _DIRECT_WRITE_PATTERN.search(snippet):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.capsule_bypass_smell",
                            severity="RISK",
                            confidence=0.92,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "Potential direct SYS-2 capsule state mutation outside canonical runtime/engine path",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-CAPSULE-OUTPUTS-THROUGH-PROCESSES"],
                            related_paths=[rel_path, runtime_rel, macro_engine_rel],
                        )
                    )
                    break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
