#!/usr/bin/env python3
"""CompatX compatibility and migration enforcement CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(THIS_DIR, "core")
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

DEV_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "scripts", "dev"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from compatibility_matrix import (  # noqa: E402
    build_matrix_index,
    load_json,
    transition_entry,
    validate_matrix_payload,
    validate_schema_policy_links,
)
from migration_runner import (  # noqa: E402
    load_and_validate,
    migration_index,
    migration_tool_exists,
    run_migration,
    validate_matrix_coverage,
)
from pack_compatibility import (  # noqa: E402
    validate_optional_bundle_removal,
    validate_pack_entries,
)
from save_replay_validator import validate_save_replay_entries  # noqa: E402
from schema_diff import diff_schema_files  # noqa: E402
from env_tools_lib import canonical_workspace_id, canonicalize_env_for_workspace, detect_repo_root  # noqa: E402


COMPAT_MATRIX_REL = os.path.join("data", "registries", "compat_matrix.json")
MIGRATIONS_REL = os.path.join("data", "registries", "migrations.json")
SCHEMA_POLICY_REL = os.path.join("data", "registries", "schema_version_policy.json")
BUNDLE_PROFILES_REL = os.path.join("data", "registries", "bundle_profiles.json")

OUTPUT_ROOT_REL = os.path.join("docs", "audit", "compat")
BASELINE_JSON_REL = "COMPAT_BASELINE.json"
BASELINE_MD_REL = "COMPAT_BASELINE.md"


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return detect_repo_root(os.getcwd(), __file__)


def _relpath(path: str, repo_root: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_baseline_md(path: str, summary: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: {}\n".format(datetime.utcnow().strftime("%Y-%m-%d")))
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# CompatX Baseline\n\n")
        handle.write("- matrix_entries: `{}`\n".format(summary.get("matrix_entries", 0)))
        handle.write("- migration_entries: `{}`\n".format(summary.get("migration_entries", 0)))
        handle.write("- policy_entries: `{}`\n".format(summary.get("policy_entries", 0)))
        warnings = summary.get("warnings", [])
        if warnings:
            handle.write("- warnings:\n")
            for item in sorted(set(str(value) for value in warnings)):
                handle.write("  - `{}`\n".format(item))


def _load_policy_entries(path: str) -> tuple[List[Dict[str, Any]], List[str]]:
    payload = load_json(path)
    if payload is None:
        return [], ["refuse.schema_policy_registry_missing"]
    if str(payload.get("schema_id", "")).strip() != "dominium.schema.governance.schema_version_policy":
        return [], ["refuse.schema_policy_schema_id"]
    record = payload.get("record")
    if not isinstance(record, dict):
        return [], ["refuse.schema_policy_record"]
    rows = record.get("policies")
    if not isinstance(rows, list):
        return [], ["refuse.schema_policy_rows"]
    out: List[Dict[str, Any]] = []
    errors: List[str] = []
    for row in rows:
        if not isinstance(row, dict):
            errors.append("refuse.schema_policy_row_type")
            continue
        schema_id = str(row.get("schema_id", "")).strip()
        current_version = str(row.get("current_version", "")).strip()
        allowed_backward = row.get("allowed_backward")
        allowed_forward = row.get("allowed_forward")
        breaking = row.get("breaking_change_requires_migration")
        deprecation_policy = str(row.get("deprecation_policy", "")).strip()
        if not schema_id:
            errors.append("refuse.schema_policy_schema_id_missing")
        if not current_version:
            errors.append("refuse.schema_policy_current_version_missing")
        if not isinstance(allowed_backward, list):
            errors.append("refuse.schema_policy_allowed_backward")
        if not isinstance(allowed_forward, list):
            errors.append("refuse.schema_policy_allowed_forward")
        if not isinstance(breaking, bool):
            errors.append("refuse.schema_policy_breaking_flag")
        if not deprecation_policy:
            errors.append("refuse.schema_policy_deprecation_policy")
        out.append(row)
    out.sort(key=lambda row: str(row.get("schema_id", "")))
    return out, sorted(set(errors))


def _build_baseline_payload(
    matrix_entries: List[Dict[str, Any]],
    migration_entries: List[Dict[str, Any]],
    policy_entries: List[Dict[str, Any]],
    warnings: List[str],
) -> Dict[str, Any]:
    components = []
    for row in matrix_entries:
        components.append(
            {
                "component_type": row["component_type"],
                "component_id": row["component_id"],
                "from_version": row["version_from"],
                "to_version": row["version_to"],
                "compatibility_type": row["compatibility_type"],
                "migration_required": bool(row["migration_required"]),
                "migration_id": row["migration_id"],
            }
        )
    components.sort(
        key=lambda row: (
            row["component_type"],
            row["component_id"],
            row["from_version"],
            row["to_version"],
        )
    )
    return {
        "artifact_class": "CANONICAL",
        "schema_id": "dominium.schema.governance.compat_matrix",
        "schema_version": "1.0.0",
        "record": {
            "baseline_id": "compatx.baseline",
            "matrix_entries": components,
            "migration_ids": sorted(str(row.get("migration_id", "")) for row in migration_entries),
            "schema_policies": sorted(str(row.get("schema_id", "")) for row in policy_entries),
            "summary": {
                "matrix_entries": len(matrix_entries),
                "migration_entries": len(migration_entries),
                "policy_entries": len(policy_entries),
                "warnings": sorted(set(warnings)),
            },
            "extensions": {},
        },
    }


def _run_verify(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    ws_id = canonical_workspace_id(repo_root, env=os.environ)
    _env, ws_dirs = canonicalize_env_for_workspace(dict(os.environ), repo_root, ws_id=ws_id)

    matrix_path = os.path.join(repo_root, COMPAT_MATRIX_REL)
    migrations_path = os.path.join(repo_root, MIGRATIONS_REL)
    policy_path = os.path.join(repo_root, SCHEMA_POLICY_REL)
    bundles_path = os.path.join(repo_root, BUNDLE_PROFILES_REL)

    matrix_payload = load_json(matrix_path)
    if matrix_payload is None:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.compat_matrix_missing"}, indent=2, sort_keys=True))
        return 2
    matrix_entries, matrix_errors = validate_matrix_payload(matrix_payload)

    migration_entries, migration_errors = load_and_validate(migrations_path)
    migration_ids = [row.get("migration_id", "") for row in migration_entries]
    coverage_errors = validate_matrix_coverage(matrix_entries, migration_ids)
    migration_by_id = migration_index(migration_entries)
    missing_tools = [
        "refuse.migration_tool_missing_file"
        for row in migration_entries
        if not migration_tool_exists(repo_root, str(row.get("migration_tool", "")))
    ]

    policy_entries, policy_errors = _load_policy_entries(policy_path)
    policy_link_errors = validate_schema_policy_links(policy_entries, matrix_entries)

    save_replay_errors = validate_save_replay_entries(matrix_entries, migration_by_id)
    pack_errors = validate_pack_entries(matrix_entries, migration_by_id)
    bundle_payload = load_json(bundles_path) if os.path.isfile(bundles_path) else None
    bundle_errors = validate_optional_bundle_removal(bundle_payload)

    errors = sorted(
        set(
            matrix_errors
            + migration_errors
            + coverage_errors
            + policy_errors
            + policy_link_errors
            + save_replay_errors
            + pack_errors
            + bundle_errors
            + missing_tools
        )
    )
    if errors:
        print(json.dumps({"result": "refused", "refusal_codes": errors}, indent=2, sort_keys=True))
        return 2

    output_root = os.path.join(repo_root, OUTPUT_ROOT_REL)
    baseline_json_path = os.path.join(output_root, BASELINE_JSON_REL)
    baseline_md_path = os.path.join(output_root, BASELINE_MD_REL)

    warnings = []
    baseline_payload = _build_baseline_payload(matrix_entries, migration_entries, policy_entries, warnings)
    _write_json(baseline_json_path, baseline_payload)
    _write_baseline_md(
        baseline_md_path,
        {
            "matrix_entries": len(matrix_entries),
            "migration_entries": len(migration_entries),
            "policy_entries": len(policy_entries),
            "warnings": warnings,
        },
    )

    print(
        json.dumps(
            {
                "result": "complete",
                "workspace_id": str(ws_dirs.get("workspace_id", "")),
                "baseline_json": _relpath(baseline_json_path, repo_root),
                "baseline_md": _relpath(baseline_md_path, repo_root),
                "matrix_entries": len(matrix_entries),
                "migration_entries": len(migration_entries),
                "policy_entries": len(policy_entries),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _run_schema_diff(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    old_path = os.path.normpath(os.path.abspath(args.old_schema))
    new_path = os.path.normpath(os.path.abspath(args.new_schema))
    diff = diff_schema_files(old_path, new_path)
    diff["repo_root"] = repo_root.replace("\\", "/")
    print(json.dumps(diff, indent=2, sort_keys=True))
    return 0 if diff.get("compatibility") != "breaking" else 2


def _run_migrate(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    migration_entries, errors = load_and_validate(os.path.join(repo_root, MIGRATIONS_REL))
    if errors:
        print(json.dumps({"result": "refused", "refusal_codes": errors}, indent=2, sort_keys=True))
        return 2
    migration_by_id = migration_index(migration_entries)
    migration_id = str(args.migration_id).strip()
    migration = migration_by_id.get(migration_id)
    if migration is None:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.unknown_migration_id"}, indent=2, sort_keys=True))
        return 2

    try:
        with open(args.input_json, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        print(json.dumps({"result": "refused", "refusal_code": "refuse.invalid_migration_input"}, indent=2, sort_keys=True))
        return 2
    if not isinstance(payload, dict):
        print(json.dumps({"result": "refused", "refusal_code": "refuse.invalid_migration_input_shape"}, indent=2, sort_keys=True))
        return 2

    result = run_migration(payload, migration)
    if args.output_json:
        _write_json(os.path.normpath(os.path.abspath(args.output_json)), result["result"])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def _run_save_replay_validate(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    matrix_payload = load_json(os.path.join(repo_root, COMPAT_MATRIX_REL))
    if matrix_payload is None:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.compat_matrix_missing"}, indent=2, sort_keys=True))
        return 2
    matrix_entries, matrix_errors = validate_matrix_payload(matrix_payload)
    migration_entries, migration_errors = load_and_validate(os.path.join(repo_root, MIGRATIONS_REL))
    migration_by_id = migration_index(migration_entries)
    errors = sorted(set(matrix_errors + migration_errors + validate_save_replay_entries(matrix_entries, migration_by_id)))
    if errors:
        print(json.dumps({"result": "refused", "refusal_codes": errors}, indent=2, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "result": "complete",
                "validated_entries": len(
                    [row for row in matrix_entries if str(row.get("component_type", "")) in ("save", "replay")]
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _run_pack_validate(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    matrix_payload = load_json(os.path.join(repo_root, COMPAT_MATRIX_REL))
    if matrix_payload is None:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.compat_matrix_missing"}, indent=2, sort_keys=True))
        return 2
    matrix_entries, matrix_errors = validate_matrix_payload(matrix_payload)
    migration_entries, migration_errors = load_and_validate(os.path.join(repo_root, MIGRATIONS_REL))
    migration_by_id = migration_index(migration_entries)
    bundle_payload = load_json(os.path.join(repo_root, BUNDLE_PROFILES_REL))
    errors = sorted(
        set(
            matrix_errors
            + migration_errors
            + validate_pack_entries(matrix_entries, migration_by_id)
            + validate_optional_bundle_removal(bundle_payload)
        )
    )
    if errors:
        print(json.dumps({"result": "refused", "refusal_codes": errors}, indent=2, sort_keys=True))
        return 2
    index = build_matrix_index(matrix_entries)
    sample_entry = transition_entry(index, "pack", "pack.core.runtime", "1.0.0", "1.1.0")
    print(
        json.dumps(
            {
                "result": "complete",
                "pack_entries": len([row for row in matrix_entries if str(row.get("component_type", "")) == "pack"]),
                "sample_transition_found": bool(sample_entry),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CompatX compatibility and migration validator.")
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="Run full CompatX validation and baseline generation.")
    verify.add_argument("--repo-root", default="")
    verify.set_defaults(func=_run_verify)

    schema_diff = sub.add_parser("schema-diff", help="Classify schema change compatibility.")
    schema_diff.add_argument("--repo-root", default="")
    schema_diff.add_argument("--old-schema", required=True)
    schema_diff.add_argument("--new-schema", required=True)
    schema_diff.set_defaults(func=_run_schema_diff)

    migrate = sub.add_parser("migrate", help="Apply a deterministic migration spec to JSON payload.")
    migrate.add_argument("--repo-root", default="")
    migrate.add_argument("--migration-id", required=True)
    migrate.add_argument("--input-json", required=True)
    migrate.add_argument("--output-json", default="")
    migrate.set_defaults(func=_run_migrate)

    save_replay = sub.add_parser("save-replay-validate", help="Validate save/replay compatibility entries.")
    save_replay.add_argument("--repo-root", default="")
    save_replay.set_defaults(func=_run_save_replay_validate)

    pack_validate = sub.add_parser("pack-validate", help="Validate pack/protocol/api/abi compatibility entries.")
    pack_validate.add_argument("--repo-root", default="")
    pack_validate.set_defaults(func=_run_pack_validate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

