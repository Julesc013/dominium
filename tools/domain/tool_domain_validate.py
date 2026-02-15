#!/usr/bin/env python3
"""Deterministic validation for domain/contract/solver structural registries."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.validator import validate_instance  # noqa: E402


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _err(code: str, message: str, path: str) -> dict:
    return {
        "code": str(code),
        "message": str(message),
        "path": str(path),
    }


def _sorted_errors(rows: List[dict]) -> List[dict]:
    return sorted(
        [dict(row) for row in rows if isinstance(row, dict)],
        key=lambda row: (
            str(row.get("code", "")),
            str(row.get("path", "")),
            str(row.get("message", "")),
        ),
    )


def _id_duplicates(rows: List[dict], field: str, code: str, path_prefix: str) -> List[dict]:
    seen: Dict[str, int] = {}
    dup: List[dict] = []
    for idx, row in enumerate(rows):
        token = str((row or {}).get(field, "")).strip()
        if not token:
            continue
        if token in seen:
            dup.append(
                _err(
                    code,
                    "duplicate id '{}' at records[{}] and records[{}]".format(token, seen[token], idx),
                    "{}.records[{}].{}".format(path_prefix, idx, field),
                )
            )
        else:
            seen[token] = idx
    return dup


def _domain_id_set(domain_registry: dict) -> List[str]:
    rows = domain_registry.get("records")
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("domain_id", "")).strip()
        if token:
            out.append(token)
    return sorted(set(out))


def _contract_id_set(contract_registry: dict) -> List[str]:
    rows = contract_registry.get("records")
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("contract_id", "")).strip()
        if token:
            out.append(token)
    return sorted(set(out))


def _schema_errors(repo_root: str, schema_name: str, payload: dict, path_prefix: str) -> List[dict]:
    checked = validate_instance(
        repo_root=repo_root,
        schema_name=schema_name,
        payload=payload,
        strict_top_level=True,
    )
    if bool(checked.get("valid", False)):
        return []
    rows: List[dict] = []
    for row in checked.get("errors") or []:
        if not isinstance(row, dict):
            continue
        rows.append(
            _err(
                "refusal.schema_invalid",
                "{}: {}".format(path_prefix, str(row.get("message", ""))),
                str(row.get("path", "$")),
            )
        )
    return rows


def validate_domain_foundation(
    repo_root: str,
    domain_registry_rel: str = "data/registries/domain_registry.json",
    domain_contract_registry_rel: str = "data/registries/domain_contract_registry.json",
    solver_registry_rel: str = "data/registries/solver_registry.json",
) -> Dict[str, object]:
    domain_registry_path = os.path.join(repo_root, domain_registry_rel.replace("/", os.sep))
    contract_registry_path = os.path.join(repo_root, domain_contract_registry_rel.replace("/", os.sep))
    solver_registry_path = os.path.join(repo_root, solver_registry_rel.replace("/", os.sep))

    errors: List[dict] = []

    domain_registry, domain_err = _read_json(domain_registry_path)
    if domain_err:
        errors.append(_err("refusal.domain_missing", "domain registry JSON unavailable", _norm(domain_registry_rel)))
        domain_registry = {}
    contract_registry, contract_err = _read_json(contract_registry_path)
    if contract_err:
        errors.append(_err("refusal.contract_missing", "contract registry JSON unavailable", _norm(domain_contract_registry_rel)))
        contract_registry = {}
    solver_registry, solver_err = _read_json(solver_registry_path)
    if solver_err:
        errors.append(_err("refusal.solver_unbound", "solver registry JSON unavailable", _norm(solver_registry_rel)))
        solver_registry = {}

    if not errors:
        errors.extend(_schema_errors(repo_root, "domain_foundation_registry", domain_registry, domain_registry_rel))
        errors.extend(_schema_errors(repo_root, "domain_contract_registry", contract_registry, domain_contract_registry_rel))
        errors.extend(_schema_errors(repo_root, "solver_registry", solver_registry, solver_registry_rel))

    domain_rows = list(domain_registry.get("records") or []) if isinstance(domain_registry.get("records"), list) else []
    contract_rows = list(contract_registry.get("records") or []) if isinstance(contract_registry.get("records"), list) else []
    solver_rows = list(solver_registry.get("records") or []) if isinstance(solver_registry.get("records"), list) else []

    errors.extend(_id_duplicates(domain_rows, "domain_id", "refusal.duplicate_id", _norm(domain_registry_rel)))
    errors.extend(_id_duplicates(contract_rows, "contract_id", "refusal.duplicate_id", _norm(domain_contract_registry_rel)))
    errors.extend(_id_duplicates(solver_rows, "solver_id", "refusal.duplicate_id", _norm(solver_registry_rel)))

    domain_ids = set(_domain_id_set(domain_registry))
    contract_ids = set(_contract_id_set(contract_registry))

    for idx, row in enumerate(domain_rows):
        if not isinstance(row, dict):
            continue
        for contract_id in sorted(set(str(item).strip() for item in (row.get("contract_ids") or []) if str(item).strip())):
            if contract_id not in contract_ids:
                errors.append(
                    _err(
                        "refusal.contract_missing",
                        "domain '{}' references missing contract '{}'".format(str(row.get("domain_id", "")), contract_id),
                        "{}.records[{}].contract_ids".format(_norm(domain_registry_rel), idx),
                    )
                )

    for idx, row in enumerate(solver_rows):
        if not isinstance(row, dict):
            continue
        solver_id = str(row.get("solver_id", "")).strip()
        bound_domain_ids = sorted(set(str(item).strip() for item in (row.get("domain_ids") or []) if str(item).strip()))
        bound_contract_ids = sorted(set(str(item).strip() for item in (row.get("contract_ids") or []) if str(item).strip()))
        if not bound_domain_ids or not bound_contract_ids:
            errors.append(
                _err(
                    "refusal.solver_unbound",
                    "solver '{}' must declare non-empty domain_ids and contract_ids".format(solver_id),
                    "{}.records[{}]".format(_norm(solver_registry_rel), idx),
                )
            )
        for domain_id in bound_domain_ids:
            if domain_id not in domain_ids:
                errors.append(
                    _err(
                        "refusal.domain_missing",
                        "solver '{}' references missing domain '{}'".format(solver_id, domain_id),
                        "{}.records[{}].domain_ids".format(_norm(solver_registry_rel), idx),
                    )
                )
        for contract_id in bound_contract_ids:
            if contract_id not in contract_ids:
                errors.append(
                    _err(
                        "refusal.contract_missing",
                        "solver '{}' references missing contract '{}'".format(solver_id, contract_id),
                        "{}.records[{}].contract_ids".format(_norm(solver_registry_rel), idx),
                    )
                )

    ordered_errors = _sorted_errors(errors)
    status = "complete" if not ordered_errors else "refused"
    return {
        "result": status,
        "domain_registry_path": _norm(domain_registry_rel),
        "domain_contract_registry_path": _norm(domain_contract_registry_rel),
        "solver_registry_path": _norm(solver_registry_rel),
        "summary": {
            "domain_count": len(domain_ids),
            "contract_count": len(contract_ids),
            "solver_count": len(
                sorted(
                    set(
                        str(row.get("solver_id", "")).strip()
                        for row in solver_rows
                        if isinstance(row, dict) and str(row.get("solver_id", "")).strip()
                    )
                )
            ),
        },
        "errors": ordered_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate domain/contract/solver foundation registries.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--domain-registry", default="data/registries/domain_registry.json")
    parser.add_argument("--contract-registry", default="data/registries/domain_contract_registry.json")
    parser.add_argument("--solver-registry", default="data/registries/solver_registry.json")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = validate_domain_foundation(
        repo_root=repo_root,
        domain_registry_rel=str(args.domain_registry),
        domain_contract_registry_rel=str(args.contract_registry),
        solver_registry_rel=str(args.solver_registry),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
