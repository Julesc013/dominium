#!/usr/bin/env python3
"""Validate the AIDE-CHECKPOINT-LOOP-01 policy packet and fixtures.

This check is intentionally lightweight. It validates required policy files and
tiny checkpoint fixtures without implementing branch automation, merging,
promotion, or repair execution.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_POLICY_FILES = [
    ".aide/policy/checkpoint_loop_law.md",
    ".aide/policy/checkpoint_validation_tiers.md",
    ".aide/policy/checkpoint_repair_policy.md",
    ".aide/policy/checkpoint_promotion_policy.md",
]

CHECKPOINT_FIXTURES = {
    "valid_checkpoint_candidate_minimal.json": ("checkpoint", True),
    "valid_checkpoint_candidate_with_repair.json": ("checkpoint", True),
    "invalid_checkpoint_missing_validation_plan.json": ("checkpoint", False),
}

PROMOTION_FIXTURES = {
    "valid_promotion_decision_promote.json": ("promotion", True),
    "valid_promotion_decision_defer.json": ("promotion", True),
    "invalid_promotion_missing_evidence.json": ("promotion", False),
    "invalid_promotion_unclassified_warning.json": ("promotion", False),
}

CHECKPOINT_REQUIRED = [
    "checkpoint_id",
    "wave_id",
    "source_branches",
    "included_work_units",
    "excluded_work_units",
    "base_commit",
    "merge_commit",
    "validation_plan",
    "validation_results",
    "warning_disposition_refs",
    "blockers",
    "promotion_recommendation",
    "status",
]

PROMOTION_REQUIRED = [
    "promotion_id",
    "checkpoint_id",
    "source_branch",
    "target_branch",
    "decision",
    "required_evidence_refs",
    "validation_summary",
    "warnings_accepted",
    "warnings_rejected",
    "human_approver",
    "rationale",
    "resulting_commit",
]

POLICY_SNIPPETS = {
    ".aide/policy/checkpoint_loop_law.md": [
        "development is non-blocking",
        "promotion is evidence-blocked",
        "CHECKPOINT_PASS",
        "CHECKPOINT_REPAIR_REQUIRED",
        "CHECKPOINT_QUARANTINE_REQUIRED",
        "Coordinator File Update Policy",
        "Evidence Bundle Requirements",
    ],
    ".aide/policy/checkpoint_validation_tiers.md": [
        "T0 - Coordinator Consistency",
        "T1 - Policy And Schema Consistency",
        "T2 - Foundation Fast Gate",
        "T3 - Product-Spine Affected Gate",
        "T4 - Full Or Release Gate",
        "T4 is not required for ordinary dev checkpoints",
        "Full CTest remains T4/full-gate debt",
    ],
    ".aide/policy/checkpoint_repair_policy.md": [
        "Create Repair WorkUnits",
        "Create Prerequisite Tasks",
        "Create Resume Tasks",
        "Quarantine Work",
        "Targeted Validation After Repair",
        "Repeated Failures",
    ],
    ".aide/policy/checkpoint_promotion_policy.md": [
        "Promotion Decision Requirements",
        "Minimum Evidence For Main Promotion",
        "Warning Acceptance Rules",
        "Human Approval Rules",
        "Automatic promotion is not authorized",
        "Rollback, Defer, And Quarantine Outcomes",
    ],
}


class ValidationError(Exception):
    """Raised when a fixture violates the supported checkpoint slice."""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_object(data: Any, path: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return data


def require_fields(data: dict[str, Any], fields: list[str], path: Path) -> None:
    for field in fields:
        if field not in data:
            raise ValidationError(f"{path} missing required field: {field}")


def require_string(data: dict[str, Any], field: str, path: Path) -> None:
    if not isinstance(data.get(field), str) or not data[field]:
        raise ValidationError(f"{path} field must be non-empty string: {field}")


def require_array(data: dict[str, Any], field: str, path: Path) -> None:
    if not isinstance(data.get(field), list):
        raise ValidationError(f"{path} field must be array: {field}")


def validate_checkpoint(data: dict[str, Any], path: Path) -> None:
    require_fields(data, CHECKPOINT_REQUIRED, path)
    for field in [
        "checkpoint_id",
        "wave_id",
        "base_commit",
        "promotion_recommendation",
        "status",
    ]:
        require_string(data, field, path)
    for field in [
        "source_branches",
        "included_work_units",
        "excluded_work_units",
        "validation_plan",
        "validation_results",
        "warning_disposition_refs",
        "blockers",
    ]:
        require_array(data, field, path)
    if not data["source_branches"]:
        raise ValidationError(f"{path} source_branches must not be empty")
    if not data["included_work_units"]:
        raise ValidationError(f"{path} included_work_units must not be empty")
    if not data["validation_plan"]:
        raise ValidationError(f"{path} validation_plan must not be empty")
    if data["promotion_recommendation"] not in {
        "promote",
        "reject",
        "repair_required",
        "quarantine",
        "defer",
    }:
        raise ValidationError(f"{path} invalid promotion_recommendation")


def validate_promotion(data: dict[str, Any], path: Path) -> None:
    require_fields(data, PROMOTION_REQUIRED, path)
    for field in [
        "promotion_id",
        "checkpoint_id",
        "source_branch",
        "target_branch",
        "decision",
        "validation_summary",
        "rationale",
    ]:
        require_string(data, field, path)
    for field in ["required_evidence_refs", "warnings_accepted", "warnings_rejected"]:
        require_array(data, field, path)
    if data["decision"] not in {"promote", "reject", "repair_required", "quarantine", "defer"}:
        raise ValidationError(f"{path} invalid decision")
    if data["decision"] == "promote":
        if data["target_branch"] != "origin/main":
            raise ValidationError(f"{path} promote decision must target origin/main")
        if not data["required_evidence_refs"]:
            raise ValidationError(f"{path} promote decision requires evidence refs")
        if not data.get("human_approver"):
            raise ValidationError(f"{path} promote decision requires approval")
        summary = data["validation_summary"].lower()
        rationale = data["rationale"].lower()
        if "unclassified_warning" in summary or "unclassified" in rationale:
            raise ValidationError(f"{path} promote decision contains unclassified warning")


def validate_fixture(path: Path, fixture_type: str) -> None:
    data = require_object(load_json(path), path)
    if fixture_type == "checkpoint":
        validate_checkpoint(data, path)
    elif fixture_type == "promotion":
        validate_promotion(data, path)
    else:
        raise ValidationError(f"{path} unknown fixture type: {fixture_type}")


def validate_policy_files(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_POLICY_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required policy file: {rel}")
            continue
        text = read_text(path)
        for snippet in POLICY_SNIPPETS[rel]:
            if snippet not in text:
                errors.append(f"{rel} missing required text: {snippet}")


def validate_fixtures(root: Path, errors: list[str]) -> None:
    fixture_root = root / ".aide/fixtures/checkpoint"
    all_fixtures = {**CHECKPOINT_FIXTURES, **PROMOTION_FIXTURES}
    for name, (fixture_type, should_pass) in all_fixtures.items():
        path = fixture_root / name
        if not path.is_file():
            errors.append(f"missing checkpoint fixture: {name}")
            continue
        try:
            validate_fixture(path, fixture_type)
            actual_pass = True
        except Exception as exc:  # pragma: no cover - command-line validator
            actual_pass = False
            failure = str(exc)
        if actual_pass != should_pass:
            expectation = "pass" if should_pass else "fail"
            actual = "pass" if actual_pass else f"fail ({failure})"
            errors.append(f"{name} expected {expectation}, got {actual}")


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    errors: list[str] = []

    validate_policy_files(root, errors)
    validate_fixtures(root, errors)

    if errors:
        print("AIDE checkpoint loop check: FAIL")
        for error in errors:
            print(f"- FAIL {error}")
        return 1

    print("AIDE checkpoint loop check: PASS")
    print(f"- policy files: {len(REQUIRED_POLICY_FILES)}")
    print(f"- checkpoint fixtures: {len(CHECKPOINT_FIXTURES)}")
    print(f"- promotion fixtures: {len(PROMOTION_FIXTURES)}")
    print("- main promotion evidence gate: present")
    print("- unclassified promotion warning rejection: present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
