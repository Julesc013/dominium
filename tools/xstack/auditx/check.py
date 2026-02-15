#!/usr/bin/env python3
"""Minimal deterministic AuditX checks for pack/registry/doc drift."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.validator import validate_instance  # noqa: E402
from tools.xstack.pack_contrib.parser import parse_contributions  # noqa: E402
from tools.xstack.pack_loader.loader import load_pack_set  # noqa: E402


REGISTRY_SCHEMA_MAP = (
    ("build/registries/domain.registry.json", "domain_registry"),
    ("build/registries/law.registry.json", "law_registry"),
    ("build/registries/experience.registry.json", "experience_registry"),
    ("build/registries/lens.registry.json", "lens_registry"),
    ("build/registries/astronomy.catalog.index.json", "astronomy_catalog_index"),
    ("build/registries/site.registry.index.json", "site_registry_index"),
    ("build/registries/ui.registry.json", "ui_registry"),
)

DOC_SCHEMA_LINKS = {
    "docs/architecture/pack_system.md": ["pack_manifest.schema.json", "bundle_profile.schema.json"],
    "docs/architecture/registry_compile.md": ["bundle_lockfile.schema.json", "site_registry_index.schema.json", "bundle.base.lab"],
    "docs/architecture/astronomy_catalogs.md": ["astronomy_catalog_entry.schema.json", "reference_frame.schema.json", "astronomy.catalog.index.json"],
    "docs/architecture/site_registry.md": ["site_entry.schema.json", "site.registry.index.json", "TARGET_NOT_FOUND"],
    "docs/architecture/session_lifecycle.md": ["session_spec.schema.json", "bundle_profile.schema.json", "session_boot"],
    "docs/architecture/srz_contract.md": ["srz_shard.schema.json", "intent_envelope.schema.json", "SHARD_TARGET_INVALID"],
    "docs/architecture/deterministic_parallelism.md": ["read", "propose", "resolve", "commit"],
    "docs/architecture/hash_anchors.md": ["PerTickHash", "CheckpointHash", "CompositeHash"],
    "docs/architecture/deterministic_packaging.md": ["tools/setup/build", "manifest.json", "canonical_content_hash"],
    "docs/architecture/setup_and_launcher.md": ["tools/launcher/launch", "LOCKFILE_MISMATCH", "lockfile_enforcement"],
    "docs/architecture/truth_model.md": ["truth_model_v1.h", "truth_perceived_render.md"],
    "docs/architecture/observation_kernel.md": ["observe(", "LENS_FORBIDDEN", "ENTITLEMENT_MISSING"],
    "docs/architecture/truth_perceived_render.md": ["DOMINIUM_RENDERER_BOUNDARY", "repox.renderer_truth_import"],
    "docs/architecture/lens_system.md": ["lens.registry.json", "law.registry.json", "LENS_FORBIDDEN"],
    "docs/contracts/session_spec.md": ["session_spec.schema.json"],
    "docs/contracts/authority_context.md": ["authority_context.schema.json"],
    "docs/contracts/law_profile.md": ["law_profile.schema.json"],
    "docs/contracts/lens_contract.md": ["lens.schema.json"],
    "docs/contracts/refusal_contract.md": ["reason_code", "remediation_hint", "relevant_ids"],
    "docs/contracts/versioning_and_migration.md": ["version_registry.json"],
    "docs/testing/xstack_profiles.md": ["tools/xstack/run.py"],
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _severity_rank(token: str) -> int:
    value = str(token or "").strip().lower()
    if value == "warn":
        return 0
    if value == "fail":
        return 1
    if value == "refusal":
        return 2
    return 9


def _finding(scope: str, severity: str, code: str, message: str, file_path: str = "", line_number: int = 0) -> Dict[str, object]:
    return {
        "scope": str(scope),
        "severity": str(severity),
        "code": str(code),
        "message": str(message),
        "file_path": _norm(file_path),
        "line_number": int(line_number),
    }


def _status_from_findings(findings: List[Dict[str, object]]) -> str:
    severities = set(str(row.get("severity", "")) for row in findings)
    if "refusal" in severities:
        return "refusal"
    if "fail" in severities:
        return "fail"
    return "pass"


def _pack_checks(repo_root: str) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    loaded = load_pack_set(repo_root=repo_root)
    if loaded.get("result") != "complete":
        for row in loaded.get("errors", []):
            findings.append(
                _finding(
                    scope="pack",
                    severity="refusal",
                    code=str(row.get("code", "refuse.auditx.pack_load_failed")),
                    message=str(row.get("message", "")),
                    file_path=str(row.get("path", "")),
                )
            )
        return findings

    contrib = parse_contributions(repo_root=repo_root, packs=loaded.get("packs") or [])
    if contrib.get("result") != "complete":
        for row in contrib.get("errors", []):
            findings.append(
                _finding(
                    scope="pack",
                    severity="refusal",
                    code=str(row.get("code", "refuse.auditx.pack_contrib_failed")),
                    message=str(row.get("message", "")),
                    file_path=str(row.get("path", "")),
                )
            )
    return findings


def _registry_checks(repo_root: str) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    for rel_path, schema_name in REGISTRY_SCHEMA_MAP:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    scope="registry",
                    severity="fail",
                    code="fail.auditx.registry_missing",
                    message="missing compiled registry '{}'".format(rel_path),
                    file_path=rel_path,
                )
            )
            continue
        try:
            payload = json.load(open(abs_path, "r", encoding="utf-8"))
        except (OSError, ValueError):
            findings.append(
                _finding(
                    scope="registry",
                    severity="refusal",
                    code="refuse.auditx.registry_invalid_json",
                    message="invalid JSON in '{}'".format(rel_path),
                    file_path=rel_path,
                )
            )
            continue

        result = validate_instance(
            repo_root=repo_root,
            schema_name=schema_name,
            payload=payload,
            strict_top_level=True,
        )
        if not bool(result.get("valid", False)):
            for err in result.get("errors", []):
                findings.append(
                    _finding(
                        scope="registry",
                        severity="refusal",
                        code=str(err.get("code", "refuse.auditx.registry_schema_invalid")),
                        message="{}: {}".format(rel_path, str(err.get("message", ""))),
                        file_path=rel_path,
                    )
                )
    return findings


def _docs_checks(repo_root: str, profile: str) -> List[Dict[str, object]]:
    token = str(profile or "").strip().upper() or "FAST"
    strict = token in ("STRICT", "FULL")
    findings: List[Dict[str, object]] = []

    for rel_path in sorted(DOC_SCHEMA_LINKS.keys()):
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                _finding(
                    scope="docs",
                    severity="fail" if not strict else "refusal",
                    code="fail.auditx.required_doc_missing",
                    message="required doc '{}' is missing".format(rel_path),
                    file_path=rel_path,
                )
            )
            continue
        try:
            text = open(abs_path, "r", encoding="utf-8").read()
        except OSError:
            text = ""
        for token_ref in DOC_SCHEMA_LINKS[rel_path]:
            if token_ref not in text:
                findings.append(
                    _finding(
                        scope="docs",
                        severity="warn" if not strict else "fail",
                        code="warn.auditx.doc_schema_ref_missing",
                        message="doc '{}' missing reference '{}'".format(rel_path, token_ref),
                        file_path=rel_path,
                    )
                )
        if "1.0.0" not in text:
            findings.append(
                _finding(
                    scope="docs",
                    severity="warn" if not strict else "fail",
                    code="warn.auditx.doc_version_missing",
                    message="doc '{}' missing version marker '1.0.0'".format(rel_path),
                    file_path=rel_path,
                )
            )

        if strict:
            schema_mentions = sorted(set(re.findall(r"[a-z0-9_]+\.schema\.json", text)))
            for mention in schema_mentions:
                schema_path = os.path.join(repo_root, "schemas", mention)
                if not os.path.isfile(schema_path):
                    findings.append(
                        _finding(
                            scope="docs",
                            severity="fail",
                            code="fail.auditx.doc_schema_missing",
                            message="doc '{}' references missing schema '{}'".format(rel_path, mention),
                            file_path=rel_path,
                        )
                    )
    return findings


def run_auditx_check(repo_root: str, profile: str) -> Dict[str, object]:
    findings: List[Dict[str, object]] = []
    findings.extend(_pack_checks(repo_root))
    findings.extend(_registry_checks(repo_root))
    findings.extend(_docs_checks(repo_root, profile))
    ordered = sorted(
        findings,
        key=lambda row: (
            _severity_rank(str(row.get("severity", ""))),
            str(row.get("scope", "")),
            str(row.get("file_path", "")),
            int(row.get("line_number", 0) or 0),
            str(row.get("code", "")),
            str(row.get("message", "")),
        ),
    )
    status = _status_from_findings(ordered)
    message = "auditx checks {} (findings={})".format(
        "passed" if status == "pass" else "completed_with_findings",
        len(ordered),
    )
    return {
        "status": status,
        "message": message,
        "findings": ordered,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run minimal deterministic AuditX checks.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_auditx_check(repo_root=repo_root, profile=str(args.profile))
    print(json.dumps(result, indent=2, sort_keys=True))
    status = str(result.get("status", "error"))
    if status == "pass":
        return 0
    if status == "refusal":
        return 2
    if status == "fail":
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
