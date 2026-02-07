import argparse
import os
import sys

from stage_matrix_common import (
    EPISTEMIC_SCOPES,
    STAGES,
    REFUSE_STAGE_TOO_LOW,
    add_violation,
    command_surface,
    emit_violations,
    evaluate_pack_stage,
    family_status,
    hash_payload,
    load_stage_fixture,
    load_stage_matrix,
    parse_command_entries,
    parse_ui_actions,
    stage_rank,
)


SUITE_NAMES = (
    "test_load_and_validate",
    "test_command_surface",
    "test_pack_gating",
    "test_epistemics",
    "test_determinism_smoke",
    "test_replay_hash",
)


def run_load_and_validate(repo_root, stage_id, violations):
    entry, fixture = load_stage_fixture(repo_root, stage_id)
    if entry is None or fixture is None:
        add_violation(violations, "STAGE_MATRIX_MISSING_ENTRY", stage_id, "stage missing from STAGE_MATRIX.yaml")
        return
    if fixture["schema_id"] != "dominium.schema.stage_declaration":
        add_violation(
            violations,
            "STAGE_FIXTURE_SCHEMA_ID",
            stage_id,
            "fixture schema_id mismatch",
            fixture=fixture["path"],
            expected="dominium.schema.stage_declaration",
            actual=str(fixture["schema_id"]),
        )
    if fixture["schema_version"] != "1.0.0":
        add_violation(
            violations,
            "STAGE_FIXTURE_SCHEMA_VERSION",
            stage_id,
            "fixture schema_version mismatch",
            fixture=fixture["path"],
            expected="1.0.0",
            actual=str(fixture["schema_version"]),
        )
    if fixture["requires_stage"] != stage_id:
        add_violation(
            violations,
            "STAGE_FIXTURE_REQUIRES",
            stage_id,
            "fixture requires_stage mismatch",
            fixture=fixture["path"],
            expected=stage_id,
            actual=str(fixture["requires_stage"]),
        )
    if fixture["provides_stage"] != stage_id:
        add_violation(
            violations,
            "STAGE_FIXTURE_PROVIDES",
            stage_id,
            "fixture provides_stage mismatch",
            fixture=fixture["path"],
            expected=stage_id,
            actual=str(fixture["provides_stage"]),
        )
    if not isinstance(fixture["stage_features"], list):
        add_violation(
            violations,
            "STAGE_FIXTURE_FEATURES",
            stage_id,
            "fixture stage_features must be list",
            fixture=fixture["path"],
        )


def run_command_surface(repo_root, stage_id, violations):
    matrix = load_stage_matrix(repo_root)
    entry = None
    for item in matrix.get("stages", []):
        if item.get("stage_id") == stage_id:
            entry = item
            break
    if entry is None:
        add_violation(violations, "STAGE_MATRIX_MISSING_ENTRY", stage_id, "stage missing from STAGE_MATRIX.yaml")
        return
    commands = parse_command_entries(repo_root)
    allowed, denied = command_surface(commands, stage_id)
    if stage_rank(stage_id) < len(STAGES) - 1 and not denied:
        add_violation(violations, "STAGE_COMMAND_SURFACE_EMPTY_DENIED", stage_id, "higher-stage commands were not denied")

    for command in commands:
        cmd_rank = stage_rank(command["required_stage"])
        world_rank = stage_rank(stage_id)
        if cmd_rank < 0:
            add_violation(
                violations,
                "STAGE_COMMAND_INVALID_REQUIRED_STAGE",
                stage_id,
                "command has invalid required_stage",
                command=command["name"],
                actual=command["required_stage"],
            )
            continue
        expected_allowed = world_rank >= cmd_rank
        is_allowed = command in allowed
        if expected_allowed != is_allowed:
            add_violation(
                violations,
                "STAGE_COMMAND_VISIBILITY_MISMATCH",
                stage_id,
                "command availability mismatch",
                command=command["name"],
                expected="allowed" if expected_allowed else "denied",
                actual="allowed" if is_allowed else "denied",
            )

    family_map = family_status(allowed)
    enabled_expected = set(entry.get("expected_enabled_command_families", []))
    disabled_expected = set(entry.get("expected_disabled_command_families", []))
    for family in enabled_expected:
        if not family_map.get(family, False):
            add_violation(
                violations,
                "STAGE_COMMAND_FAMILY_EXPECTED_ENABLED",
                stage_id,
                "expected command family is not enabled",
                expected=family,
                actual="disabled",
            )
    for family in disabled_expected:
        if family_map.get(family, False):
            add_violation(
                violations,
                "STAGE_COMMAND_FAMILY_EXPECTED_DISABLED",
                stage_id,
                "expected command family is not disabled",
                expected=family,
                actual="enabled",
            )

    ui_actions = parse_ui_actions(repo_root)
    command_names = {command["name"] for command in commands}
    for action in ui_actions:
        if action not in command_names:
            add_violation(
                violations,
                "STAGE_UI_BIND_NON_CANONICAL_COMMAND",
                stage_id,
                "UI action is not in canonical command graph",
                command=action,
            )


def run_pack_gating(repo_root, stage_id, violations):
    matrix = load_stage_matrix(repo_root)
    entry = None
    for item in matrix.get("stages", []):
        if item.get("stage_id") == stage_id:
            entry = item
            break
    if entry is None:
        add_violation(violations, "STAGE_MATRIX_MISSING_ENTRY", stage_id, "stage missing from STAGE_MATRIX.yaml")
        return
    world_rank = stage_rank(stage_id)
    acceptance = entry.get("expected_pack_acceptance", "")
    refusal = entry.get("expected_pack_refusal", "")
    if acceptance != "<= stage":
        add_violation(
            violations,
            "STAGE_PACK_EXPECTATION_INVALID",
            stage_id,
            "expected_pack_acceptance must be '<= stage'",
            expected="<= stage",
            actual=str(acceptance),
        )
    if refusal != "> stage -> REFUSE_CAPABILITY_STAGE_TOO_LOW":
        add_violation(
            violations,
            "STAGE_PACK_REFUSAL_EXPECTATION_INVALID",
            stage_id,
            "expected_pack_refusal mismatch",
            expected="> stage -> REFUSE_CAPABILITY_STAGE_TOO_LOW",
            actual=str(refusal),
        )

    for pack_stage in STAGES:
        result = evaluate_pack_stage(stage_id, pack_stage)
        pack_rank = stage_rank(pack_stage)
        if pack_rank <= world_rank:
            if not result["ok"]:
                add_violation(
                    violations,
                    "STAGE_PACK_REJECTED_COMPATIBLE",
                    stage_id,
                    "compatible pack was rejected",
                    pack=pack_stage,
                    expected="ok",
                    actual=result["reason"],
                )
        else:
            if result["ok"] or result["reason"] != REFUSE_STAGE_TOO_LOW:
                add_violation(
                    violations,
                    "STAGE_PACK_ALLOWED_INCOMPATIBLE",
                    stage_id,
                    "incompatible pack was not refused",
                    pack=pack_stage,
                    expected=REFUSE_STAGE_TOO_LOW,
                    actual=result["reason"],
                )


def run_epistemics(repo_root, stage_id, violations):
    commands = parse_command_entries(repo_root)
    allowed, _ = command_surface(commands, stage_id)
    for command in allowed:
        if command["epistemic_scope"] not in EPISTEMIC_SCOPES:
            add_violation(
                violations,
                "STAGE_EPISTEMIC_SCOPE_INVALID",
                stage_id,
                "invalid epistemic_scope",
                command=command["name"],
                actual=command["epistemic_scope"],
            )
            continue
        if command["epistemic_scope"] == "DOM_EPISTEMIC_SCOPE_FULL" and command["app"] != "tools":
            add_violation(
                violations,
                "STAGE_EPISTEMIC_SCOPE_OMNISCIENCE",
                stage_id,
                "full epistemic scope must remain tools-only",
                command=command["name"],
                expected="tools-only",
                actual=command["app"],
            )


def run_determinism_smoke(repo_root, stage_id, violations):
    commands = parse_command_entries(repo_root)
    allowed, denied = command_surface(commands, stage_id)
    payload = {
        "stage": stage_id,
        "allowed": sorted(command["name"] for command in allowed),
        "denied": sorted(command["name"] for command in denied),
    }
    digest_a = hash_payload(payload)
    digest_b = hash_payload(payload)
    if digest_a != digest_b:
        add_violation(
            violations,
            "STAGE_DETERMINISM_DIGEST_MISMATCH",
            stage_id,
            "command surface hash mismatch across identical runs",
            expected=digest_a,
            actual=digest_b,
        )


def run_replay_hash(repo_root, stage_id, violations):
    entry, fixture = load_stage_fixture(repo_root, stage_id)
    if entry is None or fixture is None:
        add_violation(violations, "STAGE_MATRIX_MISSING_ENTRY", stage_id, "stage missing from STAGE_MATRIX.yaml")
        return
    payload = {
        "stage": stage_id,
        "fixture": fixture["path"],
        "determinism_expectation": entry.get("determinism_expectation"),
        "epistemic_expectation": entry.get("epistemic_expectation"),
    }
    replay_hash_a = hash_payload(payload)
    replay_hash_b = hash_payload(payload)
    if replay_hash_a != replay_hash_b:
        add_violation(
            violations,
            "STAGE_REPLAY_HASH_MISMATCH",
            stage_id,
            "replay hash mismatch across identical runs",
            expected=replay_hash_a,
            actual=replay_hash_b,
        )


def run_suite(repo_root, stage_id, suite):
    violations = []
    if stage_id not in STAGES:
        add_violation(violations, "STAGE_INVALID_ID", stage_id, "unknown stage")
    if suite not in SUITE_NAMES:
        add_violation(violations, "STAGE_INVALID_SUITE", stage_id, "unknown suite", actual=suite)

    if not violations:
        if suite == "test_load_and_validate":
            run_load_and_validate(repo_root, stage_id, violations)
        elif suite == "test_command_surface":
            run_command_surface(repo_root, stage_id, violations)
        elif suite == "test_pack_gating":
            run_pack_gating(repo_root, stage_id, violations)
        elif suite == "test_epistemics":
            run_epistemics(repo_root, stage_id, violations)
        elif suite == "test_determinism_smoke":
            run_determinism_smoke(repo_root, stage_id, violations)
        elif suite == "test_replay_hash":
            run_replay_hash(repo_root, stage_id, violations)

    if violations:
        emit_violations(violations)
        return 1
    print("Stage suite passed: {} {}".format(stage_id, suite))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Run a single stage matrix suite.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--suite", required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    return run_suite(repo_root, args.stage_id, args.suite)


if __name__ == "__main__":
    sys.exit(main())

