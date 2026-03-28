"""E296 signing-bypass smell analyzer for PROC-8 signing/deploy discipline."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E296_SIGNING_BYPASS_SMELL"


class SigningBypassSmell:
    analyzer_id = ANALYZER_ID


_SIGNING_PATTERNS = (
    re.compile(r"\bsigning_key_artifact_id\b", re.IGNORECASE),
    re.compile(r"\bsignature_hash\b", re.IGNORECASE),
    re.compile(r"\bdeploy_to_address\b", re.IGNORECASE),
    re.compile(r"\bsig_outbound_rows\b", re.IGNORECASE),
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
    runtime_text = _read_text(repo_root, runtime_rel)
    for token in (
        "REFUSAL_SOFTWARE_PIPELINE_SIGNING_KEY_REQUIRED",
        "REFUSAL_SOFTWARE_PIPELINE_SIGNATURE_REQUIRED_FOR_DEPLOY",
        "sig_outbound_rows",
        "deployment_record_rows",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="governance.signing_bypass_smell",
                severity="RISK",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=[
                    "PROC-8 runtime signing/deploy path is missing required enforcement token",
                    token,
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-SIGN-REQUIRES-KEY",
                    "INV-DEPLOY-THROUGH-SIG",
                ],
                related_paths=[
                    runtime_rel,
                    "process/software/pipeline_engine.py",
                ],
            )
        )

    scan_roots = (
        os.path.join(repo_root, "src", "process"),
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
        "process/software/pipeline_engine.py",
        "process/software/__init__.py",
        runtime_rel,
        "tools/process/tool_replay_pipeline_window.py",
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
                    if not any(pattern.search(snippet) for pattern in _SIGNING_PATTERNS):
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="governance.signing_bypass_smell",
                            severity="RISK",
                            confidence=0.85,
                            file_path=rel_path,
                            line=line_no,
                            evidence=[
                                "software signing/deploy token appears outside canonical PROC-8 pathways",
                                snippet[:140],
                            ],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=[
                                "INV-SIGN-REQUIRES-KEY",
                                "INV-DEPLOY-THROUGH-SIG",
                            ],
                            related_paths=[
                                rel_path,
                                runtime_rel,
                                "process/software/pipeline_engine.py",
                            ],
                        )
                    )
                    break
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
