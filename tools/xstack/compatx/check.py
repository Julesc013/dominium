#!/usr/bin/env python3
"""CompatX profile checks integrated with the ControlX runner."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.schema_registry import (  # noqa: E402
    discover_schema_files,
    load_schema,
    load_version_registry,
)
from tools.xstack.compatx.validator import (  # noqa: E402
    validate_instance,
    validate_schema_example,
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _finding_key(row: Dict[str, object]) -> Tuple[str, str, int, str]:
    severity_rank = {
        "warn": 0,
        "fail": 1,
        "refusal": 2,
    }
    return (
        str(severity_rank.get(str(row.get("severity", "")), 9)),
        str(row.get("schema_name", "")),
        int(row.get("line_number", 0) or 0),
        str(row.get("message", "")),
    )


def _finding(
    schema_name: str,
    severity: str,
    message: str,
    code: str,
    line_number: int = 0,
) -> Dict[str, object]:
    return {
        "schema_name": str(schema_name),
        "severity": str(severity),
        "line_number": int(line_number),
        "code": str(code),
        "message": str(message),
    }


def _status_from_findings(findings: List[Dict[str, object]]) -> str:
    severities = set(str(row.get("severity", "")) for row in findings)
    if "refusal" in severities:
        return "refusal"
    if "fail" in severities:
        return "fail"
    return "pass"


def run_compatx_check(repo_root: str, profile: str) -> Dict[str, object]:
    token = str(profile or "").strip().upper() or "FAST"
    strict_mode = token in ("STRICT", "FULL")
    findings: List[Dict[str, object]] = []

    schema_files = discover_schema_files(repo_root)
    if not schema_files:
        findings.append(
            _finding(
                schema_name="<all>",
                severity="refusal",
                code="refuse.compatx.missing_schemas",
                message="no schema files discovered under schemas/*.schema.json",
            )
        )
    version_registry, version_error = load_version_registry(repo_root)
    if version_error:
        findings.append(
            _finding(
                schema_name="<registry>",
                severity="refusal",
                code="refuse.compatx.version_registry_load_failed",
                message=version_error,
            )
        )
    registry_entries = {}
    if isinstance(version_registry, dict):
        raw_entries = version_registry.get("schemas")
        if isinstance(raw_entries, dict):
            registry_entries = raw_entries

    for schema_name in sorted(schema_files.keys()):
        schema, schema_path, schema_error = load_schema(repo_root, schema_name)
        if schema_error:
            findings.append(
                _finding(
                    schema_name=schema_name,
                    severity="refusal",
                    code="refuse.compatx.schema_load_failed",
                    message=schema_error,
                )
            )
            continue

        example_result = validate_schema_example(repo_root=repo_root, schema_name=schema_name)
        if not bool(example_result.get("valid", False)):
            for err in example_result.get("errors", []):
                findings.append(
                    _finding(
                        schema_name=schema_name,
                        severity="refusal",
                        code=str(err.get("code", "refuse.compatx.schema_example_invalid")),
                        message=str(err.get("message", "")),
                    )
                )

        entry = registry_entries.get(schema_name)
        if not isinstance(entry, dict):
            findings.append(
                _finding(
                    schema_name=schema_name,
                    severity="refusal",
                    code="refuse.compatx.missing_registry_entry",
                    message="schema '{}' missing entry in tools/xstack/compatx/version_registry.json".format(schema_name),
                )
            )
        else:
            schema_version = str(schema.get("version", "")).strip()
            current_version = str(entry.get("current_version", "")).strip()
            if schema_version and current_version and schema_version != current_version:
                findings.append(
                    _finding(
                        schema_name=schema_name,
                        severity="refusal",
                        code="refuse.compatx.schema_registry_mismatch",
                        message="schema '{}' version '{}' does not match registry '{}'".format(
                            schema_name,
                            schema_version,
                            current_version,
                        ),
                    )
                )

        if strict_mode:
            examples = schema.get("examples")
            if isinstance(examples, list) and examples and isinstance(examples[0], dict):
                sample = copy.deepcopy(examples[0])
                sample["__xstack_unknown_top__"] = True
                strict_check = validate_instance(
                    repo_root=repo_root,
                    schema_name=schema_name,
                    payload=sample,
                    strict_top_level=True,
                )
                errs = strict_check.get("errors") or []
                has_unknown = any(
                    str(err.get("code", "")) in ("unknown_top_level_field", "unknown_field")
                    for err in errs
                    if isinstance(err, dict)
                )
                if bool(strict_check.get("valid", True)) or not has_unknown:
                    findings.append(
                        _finding(
                            schema_name=schema_name,
                            severity="refusal",
                            code="refuse.compatx.strict_unknown_field_guard_missing",
                            message="strict unknown-field refusal guard failed for schema '{}'".format(schema_name),
                        )
                    )
            else:
                findings.append(
                    _finding(
                        schema_name=schema_name,
                        severity="refusal",
                        code="refuse.compatx.strict_missing_example",
                        message="schema '{}' missing example object for strict checks".format(schema_name),
                    )
                )

        if not _norm(os.path.relpath(schema_path, repo_root)).startswith("schemas/"):
            findings.append(
                _finding(
                    schema_name=schema_name,
                    severity="fail",
                    code="fail.compatx.schema_path_mismatch",
                    message="schema '{}' path must remain under schemas/".format(schema_name),
                )
            )

    ordered = sorted(findings, key=_finding_key)
    status = _status_from_findings(ordered)
    message = "compatx checks {} (schemas={}, findings={})".format(
        "passed" if status == "pass" else "completed_with_findings",
        len(schema_files),
        len(ordered),
    )
    return {
        "status": status,
        "message": message,
        "findings": ordered,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CompatX schema/version checks.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_compatx_check(repo_root=repo_root, profile=str(args.profile))
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

