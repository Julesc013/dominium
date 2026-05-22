#!/usr/bin/env python3
"""Validate AIDE WorkUnit schemas and fixtures.

This validator is intentionally small and dependency-free. It validates the
schema/fixture slice added by AIDE-WORKUNIT-SCHEMA-01 without implementing an
AIDE scheduler, repair engine, branch manager, or promotion workflow.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_DIR = Path(".aide/schema")
FIXTURE_DIR = Path(".aide/fixtures/work_unit")

REQUIRED_SCHEMAS = {
    "work_unit": SCHEMA_DIR / "work_unit.schema.json",
    "task_attempt": SCHEMA_DIR / "task_attempt.schema.json",
    "blocker": SCHEMA_DIR / "blocker.schema.json",
    "evidence_packet": SCHEMA_DIR / "evidence_packet.schema.json",
    "repair_task": SCHEMA_DIR / "repair_task.schema.json",
    "resume_task": SCHEMA_DIR / "resume_task.schema.json",
    "checkpoint_candidate": SCHEMA_DIR / "checkpoint_candidate.schema.json",
    "promotion_decision": SCHEMA_DIR / "promotion_decision.schema.json",
    "warning_disposition": SCHEMA_DIR / "warning_disposition.schema.json",
    "capability_reality_record": SCHEMA_DIR / "capability_reality_record.schema.json",
}

FIXTURES = {
    "valid_work_unit_minimal.json": ("work_unit", True),
    "valid_task_attempt_minimal.json": ("task_attempt", True),
    "valid_blocker_repairable.json": ("blocker", True),
    "valid_evidence_packet_validation.json": ("evidence_packet", True),
    "valid_repair_task.json": ("repair_task", True),
    "valid_resume_task.json": ("resume_task", True),
    "valid_checkpoint_candidate.json": ("checkpoint_candidate", True),
    "valid_promotion_decision.json": ("promotion_decision", True),
    "invalid_work_unit_missing_task_id.json": ("work_unit", False),
    "invalid_blocker_unknown_class.json": ("blocker", False),
    "invalid_promotion_missing_evidence.json": ("promotion_decision", False),
}


class ValidationError(Exception):
    """Raised when a JSON document does not match the supported schema slice."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def json_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def matches_json_type(value: Any, expected_type: str) -> bool:
    if expected_type == "null":
        return value is None
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "object":
        return isinstance(value, dict)
    return False


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_value(value: Any, schema: dict[str, Any], path: str) -> None:
    if "const" in schema:
        require(value == schema["const"], f"{path}: expected const {schema['const']!r}")

    if "enum" in schema:
        require(value in schema["enum"], f"{path}: value {value!r} not in enum")

    if "type" in schema:
        expected = schema["type"]
        expected_types = expected if isinstance(expected, list) else [expected]
        require(
            any(matches_json_type(value, item) for item in expected_types),
            f"{path}: expected type {expected_types}, got {json_type_name(value)}",
        )

    if isinstance(value, str) and "minLength" in schema:
        require(len(value) >= int(schema["minLength"]), f"{path}: shorter than minLength")

    if isinstance(value, list):
        if "minItems" in schema:
            require(len(value) >= int(schema["minItems"]), f"{path}: fewer than minItems")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            require(len(encoded) == len(set(encoded)), f"{path}: array items are not unique")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_value(item, schema["items"], f"{path}[{index}]")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            require(key in value, f"{path}: missing required property {key!r}")
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            require(not extra, f"{path}: unexpected properties {extra}")
        for key, subschema in properties.items():
            if key in value:
                validate_value(value[key], subschema, f"{path}.{key}")


def extract_policy_table_ids(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    ids: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
        if match:
            ids.add(match.group(1))
    return ids


def extract_lifecycle_states(path: Path) -> set[str]:
    candidates = extract_policy_table_ids(path)
    return {item for item in candidates if item.upper() == item}


def enum_at(schema: dict[str, Any], *path: str) -> set[str]:
    current: Any = schema
    for key in path:
        current = current[key]
    return set(current["enum"])


def validate_policy_alignment(root: Path, schemas: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    blocker_policy = root / ".aide/policy/blocker_taxonomy.md"
    lifecycle_policy = root / ".aide/policy/task_lifecycle.md"

    if not blocker_policy.is_file():
        errors.append(f"missing blocker taxonomy policy: {blocker_policy}")
    else:
        policy_blockers = extract_policy_table_ids(blocker_policy)
        schema_blockers = enum_at(schemas["blocker"], "properties", "blocker_class")
        if policy_blockers != schema_blockers:
            errors.append(
                "blocker schema enum does not match policy taxonomy: "
                f"missing={sorted(policy_blockers - schema_blockers)} "
                f"extra={sorted(schema_blockers - policy_blockers)}"
            )

    if not lifecycle_policy.is_file():
        errors.append(f"missing task lifecycle policy: {lifecycle_policy}")
    else:
        policy_states = extract_lifecycle_states(lifecycle_policy)
        schema_states = enum_at(schemas["work_unit"], "properties", "status")
        if policy_states != schema_states:
            errors.append(
                "WorkUnit status enum does not match lifecycle policy: "
                f"missing={sorted(policy_states - schema_states)} "
                f"extra={sorted(schema_states - policy_states)}"
            )

    return errors


def run(root: Path) -> tuple[int, dict[str, Any]]:
    errors: list[str] = []
    fixture_results: list[dict[str, Any]] = []
    schemas: dict[str, dict[str, Any]] = {}

    for schema_name, rel_path in REQUIRED_SCHEMAS.items():
        path = root / rel_path
        if not path.is_file():
            errors.append(f"missing schema: {rel_path}")
            continue
        try:
            schemas[schema_name] = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"schema JSON parse failed: {rel_path}: {exc}")

    if not errors:
        errors.extend(validate_policy_alignment(root, schemas))

    for filename, (schema_name, should_pass) in FIXTURES.items():
        fixture_path = root / FIXTURE_DIR / filename
        result = {
            "fixture": str(FIXTURE_DIR / filename).replace("\\", "/"),
            "schema": schema_name,
            "expected": "pass" if should_pass else "fail",
            "actual": "not_run",
            "message": "",
        }
        if not fixture_path.is_file():
            result["actual"] = "fail"
            result["message"] = "missing fixture"
            errors.append(f"missing fixture: {fixture_path}")
            fixture_results.append(result)
            continue
        if schema_name not in schemas:
            result["actual"] = "fail"
            result["message"] = "schema unavailable"
            errors.append(f"schema unavailable for fixture: {fixture_path}")
            fixture_results.append(result)
            continue
        try:
            instance = load_json(fixture_path)
            validate_value(instance, schemas[schema_name], "$")
            passed = True
            message = "valid"
        except (json.JSONDecodeError, ValidationError) as exc:
            passed = False
            message = str(exc)
        result["actual"] = "pass" if passed else "fail"
        result["message"] = message
        fixture_results.append(result)
        if passed != should_pass:
            errors.append(
                f"fixture expectation mismatch: {fixture_path} expected "
                f"{'pass' if should_pass else 'fail'} got {'pass' if passed else 'fail'}: {message}"
            )

    report = {
        "status": "PASS" if not errors else "FAIL",
        "schema_count": len(REQUIRED_SCHEMAS),
        "fixture_count": len(FIXTURES),
        "fixtures": fixture_results,
        "errors": errors,
    }
    return (0 if not errors else 1), report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--json-out", help="Optional report path.")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    code, report = run(root)

    if args.json_out:
        out_path = root / args.json_out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"AIDE WorkUnit schema validation: {report['status']}")
    print(f"- schemas: {report['schema_count']}")
    print(f"- fixtures: {report['fixture_count']}")
    for result in report["fixtures"]:
        print(
            f"- {result['fixture']}: expected {result['expected']}, "
            f"actual {result['actual']}"
        )
    for error in report["errors"]:
        print(f"- FAIL {error}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
