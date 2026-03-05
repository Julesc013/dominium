#!/usr/bin/env python3
"""Verify SYS-4 template compilation is deterministic and reproducible."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.system import compile_system_template  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be object"
    return dict(payload), ""


def _registry_payload(repo_root: str, rel_path: str, entry_key: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload, err = _read_json(abs_path)
    if err:
        return {entry_key: []}
    return payload


def _registry_rows(payload: Mapping[str, object], entry_key: str) -> list[dict]:
    body = _as_map(payload)
    rows = body.get(entry_key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, Mapping)]
    record_rows = _as_map(body.get("record")).get(entry_key)
    if isinstance(record_rows, list):
        return [dict(item) for item in record_rows if isinstance(item, Mapping)]
    return []


def _combined_template_registry(repo_root: str) -> dict:
    core = _registry_payload(repo_root, "data/registries/system_template_registry.json", "system_templates")
    core_rows = _registry_rows(core, "system_templates")
    optional_paths = _sorted_tokens(list(_as_map(_as_map(core.get("record")).get("extensions")).get("optional_pack_paths") or []))
    out_rows = [dict(row) for row in core_rows]
    for rel in optional_paths:
        pack_rel = "{}/data/system_template_registry.json".format(str(rel).strip("/"))
        pack = _registry_payload(repo_root, pack_rel, "system_templates")
        out_rows.extend(_registry_rows(pack, "system_templates"))
    return {"system_templates": out_rows}


def verify_template_reproducible(
    *,
    repo_root: str,
    template_id: str,
    instantiation_mode: str,
) -> dict:
    template_registry = _combined_template_registry(repo_root)
    interface_registry = _registry_payload(
        repo_root, "data/registries/interface_signature_template_registry.json", "interface_signature_templates"
    )
    invariant_registry = _registry_payload(
        repo_root, "data/registries/boundary_invariant_template_registry.json", "boundary_invariant_templates"
    )
    macro_registry = _registry_payload(repo_root, "data/registries/macro_model_set_registry.json", "macro_model_sets")
    tier_registry = _registry_payload(repo_root, "data/registries/tier_contract_registry.json", "tier_contracts")
    domain_registry = _registry_payload(repo_root, "data/registries/domain_registry.json", "records")

    compiled_a = compile_system_template(
        template_id=template_id,
        instantiation_mode=instantiation_mode,
        system_template_registry_payload=template_registry,
        interface_signature_template_registry_payload=interface_registry,
        boundary_invariant_template_registry_payload=invariant_registry,
        macro_model_set_registry_payload=macro_registry,
        tier_contract_registry_payload=tier_registry,
        domain_registry_payload=domain_registry,
    )
    compiled_b = compile_system_template(
        template_id=template_id,
        instantiation_mode=instantiation_mode,
        system_template_registry_payload=template_registry,
        interface_signature_template_registry_payload=interface_registry,
        boundary_invariant_template_registry_payload=invariant_registry,
        macro_model_set_registry_payload=macro_registry,
        tier_contract_registry_payload=tier_registry,
        domain_registry_payload=domain_registry,
    )

    fingerprint_a = str(compiled_a.get("compiled_template_fingerprint", "")).strip()
    fingerprint_b = str(compiled_b.get("compiled_template_fingerprint", "")).strip()
    deterministic_a = str(compiled_a.get("deterministic_fingerprint", "")).strip()
    deterministic_b = str(compiled_b.get("deterministic_fingerprint", "")).strip()
    resolved_order_a = [str(token).strip() for token in list(compiled_a.get("resolved_template_order") or []) if str(token).strip()]
    resolved_order_b = [str(token).strip() for token in list(compiled_b.get("resolved_template_order") or []) if str(token).strip()]
    violations = []
    if fingerprint_a != fingerprint_b:
        violations.append("compiled_template_fingerprint mismatch")
    if deterministic_a != deterministic_b:
        violations.append("deterministic_fingerprint mismatch")
    if resolved_order_a != resolved_order_b:
        violations.append("resolved_template_order mismatch")

    report = {
        "result": "complete" if not violations else "violation",
        "template_id": str(template_id or "").strip(),
        "instantiation_mode": str(instantiation_mode or "").strip(),
        "compiled_template_fingerprint": fingerprint_a,
        "deterministic_fingerprint": deterministic_a,
        "resolved_template_order": resolved_order_a,
        "violations": violations,
        "deterministic_report_fingerprint": "",
    }
    report["deterministic_report_fingerprint"] = canonical_sha256(
        dict(report, deterministic_report_fingerprint="")
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify SYS-4 template compilation reproducibility.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--template-id", required=True)
    parser.add_argument("--instantiation-mode", default="micro", choices=("micro", "macro", "hybrid"))
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    report = verify_template_reproducible(
        repo_root=repo_root,
        template_id=str(args.template_id),
        instantiation_mode=str(args.instantiation_mode),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())

