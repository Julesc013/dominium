"""E260 missing interface descriptor smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E260_MISSING_INTERFACE_DESCRIPTOR_SMELL"


class MissingInterfaceDescriptorSmell:
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

    schema_rel = "schema/system/interface_signature.schema"
    validation_rel = "src/system/system_validation_engine.py"
    collapse_rel = "src/system/system_collapse_engine.py"
    expand_rel = "src/system/system_expand_engine.py"

    schema_text = _read_text(repo_root, schema_rel)
    for token in (
        "port_id:",
        "port_type_id:",
        "direction:",
        "allowed_bundle_ids:",
        "spec_limit_refs:",
        "signal_descriptors:",
        "channel_type_id:",
        "capacity:",
        "delay:",
        "access_policy_id:",
    ):
        if token in schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_interface_descriptor_smell",
                severity="RISK",
                confidence=0.95,
                file_path=schema_rel,
                line=1,
                evidence=["missing required interface descriptor token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYSTEM-INTERFACE-SIGNATURE-REQUIRED"],
                related_paths=[schema_rel, validation_rel, collapse_rel, expand_rel],
            )
        )

    validation_text = _read_text(repo_root, validation_rel)
    for token in (
        "def validate_interface_signature(",
        "interface.port_type.present",
        "interface.allowed_bundle_ids.present",
        "interface.spec_limit_refs.present",
        "interface.signal.channel_type.registered",
    ):
        if token in validation_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_interface_descriptor_smell",
                severity="RISK",
                confidence=0.9,
                file_path=validation_rel,
                line=1,
                evidence=["interface validation token missing", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYSTEM-INTERFACE-SIGNATURE-REQUIRED"],
                related_paths=[validation_rel, schema_rel],
            )
        )

    for rel_path, token in (
        (collapse_rel, "validate_interface_signature("),
        (expand_rel, "validate_interface_signature("),
    ):
        if token in _read_text(repo_root, rel_path):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_interface_descriptor_smell",
                severity="RISK",
                confidence=0.88,
                file_path=rel_path,
                line=1,
                evidence=["system transition path missing interface validation call", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYSTEM-INTERFACE-SIGNATURE-REQUIRED"],
                related_paths=[rel_path, validation_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
