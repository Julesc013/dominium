"""E270 unlogged certificate issue smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E270_UNLOGGED_CERTIFICATE_ISSUE_SMELL"


class UnloggedCertificateIssueSmell:
    analyzer_id = ANALYZER_ID


_CERT_ROW_MUTATION_PATTERN = re.compile(
    r"\bsystem_certificate_artifact_rows\b.*=",
    re.IGNORECASE,
)

_REVOCATION_ROW_MUTATION_PATTERN = re.compile(
    r"\bsystem_certificate_revocation_rows\b.*=",
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
    explain_registry_rel = "data/registries/explain_contract_registry.json"
    provenance_registry_rel = "data/registries/provenance_classification_registry.json"
    runtime_text = _read_text(repo_root, runtime_rel)

    for token in (
        "_refresh_system_certification_hash_chains(state)",
        "artifact.record.system_certification_result",
        "artifact.report.system_certification_result",
        "artifact.credential.system_certificate",
        "_append_system_certification_revocation_artifacts(",
        "event.system.certificate_revocation.collapse",
        "event.system.certificate_revocation.expand",
        "event.system.certificate_revocation.degradation_threshold",
        "event.system.certificate_revocation.spec_violation",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unlogged_certificate_issue_smell",
                severity="RISK",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["missing SYS-5 certificate issuance/revocation logging token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-NO-SILENT-CERT-ISSUE",
                    "INV-CERT-INVALIDATED-ON-MODIFICATION",
                ],
                related_paths=[runtime_rel, explain_registry_rel, provenance_registry_rel],
            )
        )

    explain_registry_text = _read_text(repo_root, explain_registry_rel)
    for token in (
        '"contract_id": "explain.system.certification_failure"',
        '"contract_id": "explain.system.certificate_revocation"',
    ):
        if token in explain_registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unlogged_certificate_issue_smell",
                severity="RISK",
                confidence=0.9,
                file_path=explain_registry_rel,
                line=1,
                evidence=["missing SYS-5 explain contract declaration", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-CERT-ISSUE"],
                related_paths=[explain_registry_rel],
            )
        )

    provenance_registry_text = _read_text(repo_root, provenance_registry_rel)
    for token in (
        "artifact.record.system_certification_result",
        "artifact.report.system_certification_result",
        "artifact.credential.system_certificate",
        "artifact.record.system_certificate_revocation",
    ):
        if token in provenance_registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unlogged_certificate_issue_smell",
                severity="RISK",
                confidence=0.9,
                file_path=provenance_registry_rel,
                line=1,
                evidence=["missing SYS-5 provenance classification", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-CERT-ISSUE"],
                related_paths=[provenance_registry_rel],
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
        runtime_rel,
        "tools/xstack/repox/check.py",
        "system/forensics/system_forensics_engine.py",
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
                    if _CERT_ROW_MUTATION_PATTERN.search(snippet) or _REVOCATION_ROW_MUTATION_PATTERN.search(snippet):
                        findings.append(
                            make_finding(
                                analyzer_id=ANALYZER_ID,
                                category="architecture.unlogged_certificate_issue_smell",
                                severity="RISK",
                                confidence=0.9,
                                file_path=rel_path,
                                line=line_no,
                                evidence=[
                                    "direct certificate/revocation row mutation detected outside canonical runtime pathway",
                                    snippet[:140],
                                ],
                                suggested_classification="NEEDS_REVIEW",
                                recommended_action="REWRITE",
                                related_invariants=["INV-NO-SILENT-CERT-ISSUE"],
                                related_paths=[rel_path, runtime_rel],
                            )
                        )
                        break

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
