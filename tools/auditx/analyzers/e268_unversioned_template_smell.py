"""E268 unversioned template smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E268_UNVERSIONED_TEMPLATE_SMELL"


class UnversionedTemplateSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _rows(payload: dict, key: str) -> list[dict]:
    rows = payload.get(key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, dict)]
    record_rows = dict(payload.get("record") or {}).get(key)
    if isinstance(record_rows, list):
        return [dict(item) for item in record_rows if isinstance(item, dict)]
    return []


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    schema_rel = "schema/system/system_template.schema"
    pack_registry_rel = "packs/system_templates/base/data/system_template_registry.json"
    core_registry_rel = "data/registries/system_template_registry.json"
    docs_rel = "docs/system/SYSTEM_TEMPLATES.md"

    for rel in (schema_rel, pack_registry_rel, core_registry_rel, docs_rel):
        if os.path.isfile(os.path.join(repo_root, rel.replace("/", os.sep))):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unversioned_template_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel,
                line=1,
                evidence=["required SYS-4 template artifact missing", rel],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-TEMPLATE-HAS-SIGNATURE-INVARIANTS"],
                related_paths=[schema_rel, pack_registry_rel, core_registry_rel],
            )
        )

    schema_text = ""
    try:
        schema_text = open(os.path.join(repo_root, schema_rel.replace("/", os.sep)), "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        schema_text = ""
    for token in (
        "template_id",
        "version",
        "interface_signature_template_id",
        "boundary_invariant_template_ids",
        "macro_model_set_id",
    ):
        if token in schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unversioned_template_smell",
                severity="RISK",
                confidence=0.9,
                file_path=schema_rel,
                line=1,
                evidence=["system_template schema missing required declaration token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-TEMPLATE-HAS-SIGNATURE-INVARIANTS"],
                related_paths=[schema_rel],
            )
        )

    pack_payload = _read_json(repo_root, pack_registry_rel)
    for row in _rows(pack_payload, "system_templates"):
        template_id = str(row.get("template_id", "")).strip()
        if not template_id:
            continue
        if str(row.get("version", "")).strip():
            version_ok = True
        else:
            version_ok = False
        signature_ok = bool(str(row.get("interface_signature_template_id", "")).strip())
        invariants_ok = bool(list(row.get("boundary_invariant_template_ids") or []))
        macro_ok = bool(str(row.get("macro_model_set_id", "")).strip())
        tier_ok = bool(str(row.get("tier_contract_id", "")).strip())
        if version_ok and signature_ok and invariants_ok and macro_ok and tier_ok:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unversioned_template_smell",
                severity="RISK",
                confidence=0.93,
                file_path=pack_registry_rel,
                line=1,
                evidence=[
                    "template declaration missing required version/signature/invariant/macro/tier references",
                    template_id,
                ],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-TEMPLATE-HAS-SIGNATURE-INVARIANTS"],
                related_paths=[pack_registry_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

