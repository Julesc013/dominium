#!/usr/bin/env python3
"""Validate Dominium build contract registries."""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Any, Dict, List, Mapping

from build_contract_common import (
    FORBIDDEN_ID_WORDS,
    PROOF_VALUES,
    STATUS_VALUES,
    entry_map,
    load_build_contracts,
    norm,
)


REQUIRED_FILES = (
    "floors.toml",
    "toolchains.toml",
    "tuples.toml",
    "artifacts.toml",
    "build_contract.schema.json",
)


def _has_forbidden_word(identifier: str) -> str:
    lowered = identifier.lower()
    for word in sorted(FORBIDDEN_ID_WORDS):
        if word in lowered:
            return word
    return ""


def _require_fields(rows: Mapping[str, Dict[str, Any]], fields: List[str], label: str, errors: List[str]) -> None:
    for row_id, row in rows.items():
        for field in fields:
            if field not in row:
                errors.append("{} {} missing required field {}".format(label, row_id, field))


def build_report(repo_root: str) -> Dict[str, Any]:
    repo_root_abs = os.path.abspath(repo_root)
    contract_root = os.path.join(repo_root_abs, "contracts", "build")
    errors: List[str] = []
    warnings: List[str] = []
    files = {}
    for filename in REQUIRED_FILES:
        path = os.path.join(contract_root, filename)
        files[filename] = os.path.isfile(path)
        if not os.path.isfile(path):
            errors.append("missing build contract file: {}".format(norm(os.path.join("contracts", "build", filename))))
    contracts: Dict[str, Dict[str, Any]] = {}
    if all(files.values()):
        try:
            contracts = load_build_contracts(repo_root_abs)
        except Exception as exc:  # pragma: no cover - surfaced in CLI output
            errors.append("failed to parse build contracts: {}".format(exc))
            contracts = {}
    floors = entry_map(contracts.get("floors", {}), "floors")
    toolchains = entry_map(contracts.get("toolchains", {}), "toolchains")
    tuples = entry_map(contracts.get("tuples", {}), "tuples")
    artifacts = entry_map(contracts.get("artifacts", {}), "artifacts")

    _require_fields(floors, ["name", "family", "status", "minimum_os", "notes"], "floor", errors)
    _require_fields(
        toolchains,
        ["name", "family", "status", "cmake_generator", "cmake_toolset", "requires_probe", "notes"],
        "toolchain",
        errors,
    )
    _require_fields(
        tuples,
        ["intent", "floor", "arch", "toolchain", "runtime", "config", "products", "platform", "renderer", "status", "proof", "notes"],
        "tuple",
        errors,
    )
    _require_fields(artifacts, ["notes"], "artifact", errors)

    for label, rows in (("floor", floors), ("toolchain", toolchains), ("tuple", tuples)):
        for row_id, row in rows.items():
            forbidden = _has_forbidden_word(row_id)
            if forbidden:
                errors.append("{} id {} contains forbidden vague word {}".format(label, row_id, forbidden))
            if re.search(r"\b(jules|desktop|laptop|workstation|homepc)\b", row_id, flags=re.IGNORECASE):
                warnings.append("{} id {} may encode a personal machine name".format(label, row_id))
            status = str(row.get("status") or "")
            if status not in STATUS_VALUES:
                errors.append("{} {} has invalid status {}".format(label, row_id, status))
    for tuple_id, row in tuples.items():
        floor = str(row.get("floor") or "")
        toolchain = str(row.get("toolchain") or "")
        proof = str(row.get("proof") or "")
        products = row.get("products")
        if floor not in floors:
            errors.append("tuple {} references missing floor {}".format(tuple_id, floor))
        if toolchain not in toolchains:
            errors.append("tuple {} references missing toolchain {}".format(tuple_id, toolchain))
        if proof not in PROOF_VALUES:
            errors.append("tuple {} has invalid proof {}".format(tuple_id, proof))
        if not isinstance(products, list) or not products:
            errors.append("tuple {} must list products".format(tuple_id))
    schema_path = os.path.join(contract_root, "build_contract.schema.json")
    if os.path.isfile(schema_path):
        try:
            with open(schema_path, "r", encoding="utf-8") as handle:
                json.load(handle)
        except json.JSONDecodeError as exc:
            errors.append("build contract schema is not valid JSON: {}".format(exc))
    return {
        "result": "pass" if not errors else "fail",
        "contract_root": norm(os.path.relpath(contract_root, repo_root_abs)),
        "files": files,
        "counts": {
            "floors": len(floors),
            "toolchains": len(toolchains),
            "tuples": len(tuples),
            "artifacts": len(artifacts),
        },
        "errors": errors,
        "warnings": warnings,
    }


def _print_text(report: Mapping[str, Any]) -> None:
    print("Build contract validation")
    print("result: {}".format(report.get("result")))
    counts = dict(report.get("counts") or {})
    print("floors: {floors}; toolchains: {toolchains}; tuples: {tuples}; artifacts: {artifacts}".format(**counts))
    errors = list(report.get("errors") or [])
    warnings = list(report.get("warnings") or [])
    if errors:
        print("")
        print("Errors:")
        for error in errors:
            print("- {}".format(error))
    if warnings:
        print("")
        print("Warnings:")
        for warning in warnings:
            print("- {}".format(warning))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Dominium build contracts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = build_report(args.repo_root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    if args.strict and report.get("result") != "pass":
        return 2
    return 0 if report.get("result") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
