#!/usr/bin/env python3
"""Validate AIDE capability reality schema, fixtures, and seed ledger.

This validator is intentionally dependency-free. It validates the record shape
and a few AIDE-specific overclaim rules without implementing runtime
capability inspection.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_PATH = Path(".aide/schema/capability_reality_record.schema.json")
LEDGER_PATH = Path(".aide/ledgers/capability_reality.jsonl")
FIXTURE_DIR = Path(".aide/fixtures/capability_reality")

STATUSES = {
    "planned",
    "specified",
    "fixture_only",
    "stubbed",
    "implemented",
    "tested",
    "exposed",
    "release_supported",
    "retired",
}

CATEGORIES = {
    "command",
    "service",
    "provider",
    "module",
    "app",
    "product_mode",
    "package",
    "pack",
    "document",
    "patch",
    "view",
    "projection",
    "replay",
    "renderer",
    "platform",
    "Workbench",
    "AIDE",
    "release",
    "domain",
}

SUPPORT_CLAIMS = {"none", "internal", "dev", "experimental", "release"}

REQUIRED_FIELDS = [
    "schema_version",
    "capability_id",
    "surface_id",
    "title",
    "owner",
    "category",
    "status",
    "status_rationale",
    "evidence_refs",
    "blocking_gaps",
    "known_warnings",
    "related_tasks",
    "related_files",
    "last_verified_commit",
    "verification_method",
    "support_claim",
    "exposed_surfaces",
    "non_goals",
    "next_actions",
]

STRING_FIELDS = [
    "schema_version",
    "capability_id",
    "surface_id",
    "title",
    "owner",
    "category",
    "status",
    "status_rationale",
    "last_verified_commit",
    "verification_method",
    "support_claim",
]

ARRAY_FIELDS = [
    "evidence_refs",
    "blocking_gaps",
    "known_warnings",
    "related_tasks",
    "related_files",
    "exposed_surfaces",
    "non_goals",
    "next_actions",
]

FIXTURES = {
    "valid_planned_capability.json": True,
    "valid_fixture_only_capability.json": True,
    "valid_tested_capability.json": True,
    "invalid_release_supported_without_evidence.json": False,
    "invalid_unknown_status.json": False,
}

BLOCKED_RUNTIME_CAPABILITIES = {
    "capability.package.runtime_mount",
    "capability.workbench.shell",
    "capability.provider.runtime",
    "capability.module.runtime_loader",
    "capability.native_gui",
    "capability.gameplay.domain_runtime",
}

BLOCKED_RUNTIME_FORBIDDEN_STATUSES = {
    "implemented",
    "tested",
    "exposed",
    "release_supported",
}


class ValidationError(Exception):
    """Raised when a capability reality record violates local policy."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_object(data: Any, label: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return data


def require_string(data: dict[str, Any], field: str, label: str) -> None:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} field must be non-empty string: {field}")


def require_array(data: dict[str, Any], field: str, label: str) -> None:
    value = data.get(field)
    if not isinstance(value, list):
        raise ValidationError(f"{label} field must be array: {field}")
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValidationError(f"{label} field {field} must contain non-empty strings")


def validate_record(data: dict[str, Any], label: str, seed_ledger: bool = False) -> None:
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValidationError(f"{label} missing required field: {field}")
    for field in STRING_FIELDS:
        require_string(data, field, label)
    for field in ARRAY_FIELDS:
        require_array(data, field, label)

    if data["schema_version"] != "dominium.aide.capability_reality_record.v1":
        raise ValidationError(f"{label} has wrong schema_version")
    if data["status"] not in STATUSES:
        raise ValidationError(f"{label} has unknown status: {data['status']}")
    if data["category"] not in CATEGORIES:
        raise ValidationError(f"{label} has unknown category: {data['category']}")
    if data["support_claim"] not in SUPPORT_CLAIMS:
        raise ValidationError(f"{label} has unknown support_claim: {data['support_claim']}")

    previous = data.get("previous_status")
    if previous is not None and previous not in STATUSES:
        raise ValidationError(f"{label} has unknown previous_status: {previous}")

    if data["status"] == "release_supported":
        if not data["evidence_refs"]:
            raise ValidationError(f"{label} release_supported requires evidence_refs")
        if data["support_claim"] != "release":
            raise ValidationError(f"{label} release_supported requires support_claim release")

    if data["status"] in {"planned", "specified", "fixture_only", "stubbed"}:
        if data["support_claim"] == "release":
            raise ValidationError(f"{label} {data['status']} must not claim release support")

    if data["status"] in {"fixture_only", "stubbed"} and data["support_claim"] == "release":
        raise ValidationError(f"{label} fixture/stubbed capability cannot be release-supported")

    if data["capability_id"] in BLOCKED_RUNTIME_CAPABILITIES:
        if data["status"] in BLOCKED_RUNTIME_FORBIDDEN_STATUSES:
            raise ValidationError(f"{label} blocked runtime capability overclaims status")
        if data["support_claim"] == "release":
            raise ValidationError(f"{label} blocked runtime capability cannot claim release support")

    if data["status"] == "exposed" and not data["exposed_surfaces"]:
        raise ValidationError(f"{label} exposed status requires exposed_surfaces")

    if seed_ledger and not data["evidence_refs"]:
        raise ValidationError(f"{label} seed ledger record requires evidence_refs")


def read_ledger(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            data = require_object(json.loads(stripped), f"{path}:{line_no}")
            validate_record(data, f"{path}:{line_no}", seed_ledger=True)
            records.append(data)
    return records


def validate_schema(root: Path, errors: list[str]) -> None:
    path = root / SCHEMA_PATH
    if not path.is_file():
        errors.append(f"missing schema: {SCHEMA_PATH}")
        return
    try:
        schema = require_object(load_json(path), str(SCHEMA_PATH))
        status_enum = set(schema["properties"]["status"]["enum"])
        category_enum = set(schema["properties"]["category"]["enum"])
        support_enum = set(schema["properties"]["support_claim"]["enum"])
    except Exception as exc:
        errors.append(f"schema parse/shape failure: {exc}")
        return
    if status_enum != STATUSES:
        errors.append("schema status enum does not match policy vocabulary")
    if category_enum != CATEGORIES:
        errors.append("schema category enum does not match policy vocabulary")
    if support_enum != SUPPORT_CLAIMS:
        errors.append("schema support_claim enum does not match policy vocabulary")


def validate_ledger(root: Path, errors: list[str]) -> list[dict[str, Any]]:
    path = root / LEDGER_PATH
    if not path.is_file():
        errors.append(f"missing ledger: {LEDGER_PATH}")
        return []
    try:
        records = read_ledger(path)
    except Exception as exc:
        errors.append(f"ledger validation failure: {exc}")
        return []
    ids = [record["capability_id"] for record in records]
    duplicates = sorted({capability_id for capability_id in ids if ids.count(capability_id) > 1})
    for capability_id in duplicates:
        errors.append(f"duplicate capability_id in ledger: {capability_id}")
    minimum_ids = {
        "capability.aide.workflow_law",
        "capability.aide.workunit_schema",
        "capability.aide.dev_main_policy",
        "capability.aide.checkpoint_loop",
        "capability.package.mount_planning",
        "capability.package.runtime_mount",
        "capability.replay.command_proof",
        "capability.client.barebones_shell",
        "capability.workbench.validation_projection",
        "capability.workbench.shell",
        "capability.provider.runtime",
        "capability.module.runtime_loader",
        "capability.renderer.software",
        "capability.native_gui",
        "capability.gameplay.domain_runtime",
    }
    missing = sorted(minimum_ids - set(ids))
    for capability_id in missing:
        errors.append(f"missing minimum seed capability: {capability_id}")
    return records


def validate_fixtures(root: Path, errors: list[str]) -> None:
    for name, should_pass in FIXTURES.items():
        path = root / FIXTURE_DIR / name
        if not path.is_file():
            errors.append(f"missing fixture: {name}")
            continue
        try:
            data = require_object(load_json(path), name)
            validate_record(data, name)
            actual_pass = True
        except Exception as exc:  # pragma: no cover - command-line validator
            actual_pass = False
            failure = str(exc)
        if actual_pass != should_pass:
            expected = "pass" if should_pass else "fail"
            actual = "pass" if actual_pass else f"fail ({failure})"
            errors.append(f"{name} expected {expected}, got {actual}")


def write_summary(path: Path, records: list[dict[str, Any]]) -> None:
    lines = [
        "# Capability Reality Summary",
        "",
        "Generated by `tools/aide/validate_capability_reality.py --summary-out`.",
        "",
        "| capability_id | category | status | support claim | blocking gaps | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in sorted(records, key=lambda item: item["capability_id"]):
        gaps = "; ".join(record["blocking_gaps"]) if record["blocking_gaps"] else "none"
        next_action = "; ".join(record["next_actions"]) if record["next_actions"] else "none"
        lines.append(
            "| {capability_id} | {category} | {status} | {support_claim} | {gaps} | {next_action} |".format(
                capability_id=record["capability_id"],
                category=record["category"],
                status=record["status"],
                support_claim=record["support_claim"],
                gaps=gaps.replace("|", "/"),
                next_action=next_action.replace("|", "/"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--summary-out", default=None)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    errors: list[str] = []
    validate_schema(root, errors)
    records = validate_ledger(root, errors)
    validate_fixtures(root, errors)

    if errors:
        print("AIDE capability reality validation: FAIL")
        for error in errors:
            print(f"- FAIL {error}")
        return 1

    if args.summary_out:
        write_summary(root / args.summary_out, records)

    print("AIDE capability reality validation: PASS")
    print(f"- schema: {SCHEMA_PATH}")
    print(f"- ledger records: {len(records)}")
    print(f"- fixtures: {len(FIXTURES)}")
    print("- blocked runtime overclaim guard: present")
    print("- release support evidence guard: present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
