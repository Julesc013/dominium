import argparse
import os
import sys

from capability_matrix_common import (
    CAPABILITY_SETS,
    EPISTEMIC_SCOPES,
    REFUSE_CAPABILITY_MISSING,
    add_violation,
    command_surface,
    emit_violations,
    evaluate_pack_capabilities,
    family_status,
    hash_payload,
    load_capability_fixture,
    load_capability_matrix,
    parse_command_entries,
    parse_ui_actions,
)


SUITE_NAMES = (
    "test_load_and_validate",
    "test_command_surface",
    "test_pack_gating",
    "test_epistemics",
    "test_determinism_smoke",
    "test_replay_hash",
)


def _get_entry(repo_root, bundle_id, violations):
    matrix = load_capability_matrix(repo_root)
    for item in matrix.get("capability_sets", []):
        if item.get("bundle_id") == bundle_id:
            return item
    add_violation(
        violations,
        "CAPABILITY_MATRIX_MISSING_ENTRY",
        bundle_id,
        "capability set missing from CAPABILITY_MATRIX.yaml",
    )
    return None


def run_load_and_validate(repo_root, bundle_id, violations):
    entry, fixture = load_capability_fixture(repo_root, bundle_id)
    if entry is None or fixture is None:
        add_violation(
            violations,
            "CAPABILITY_MATRIX_MISSING_ENTRY",
            bundle_id,
            "capability set missing from CAPABILITY_MATRIX.yaml",
        )
        return
    if fixture["schema_id"] != "dominium.schema.capability_declaration":
        add_violation(
            violations,
            "CAPABILITY_FIXTURE_SCHEMA_ID",
            bundle_id,
            "fixture schema_id mismatch",
            fixture=fixture["path"],
            expected="dominium.schema.capability_declaration",
            actual=str(fixture["schema_id"]),
        )
    if fixture["schema_version"] != "1.0.0":
        add_violation(
            violations,
            "CAPABILITY_FIXTURE_SCHEMA_VERSION",
            bundle_id,
            "fixture schema_version mismatch",
            fixture=fixture["path"],
            expected="1.0.0",
            actual=str(fixture["schema_version"]),
        )
    expected_caps = sorted(entry.get("provided_capabilities", []))
    actual_caps = sorted(fixture["provided_capabilities"])
    if expected_caps != actual_caps:
        add_violation(
            violations,
            "CAPABILITY_FIXTURE_PROVIDES",
            bundle_id,
            "fixture provided_capabilities mismatch",
            fixture=fixture["path"],
            expected="|".join(expected_caps),
            actual="|".join(actual_caps),
        )


def run_command_surface(repo_root, bundle_id, violations):
    entry = _get_entry(repo_root, bundle_id, violations)
    if entry is None:
        return
    commands = parse_command_entries(repo_root)
    provided = entry.get("provided_capabilities", [])
    allowed, _denied = command_surface(commands, provided)

    for command in commands:
        required = set(command["required_capabilities"])
        expected_allowed = required.issubset(set(provided))
        is_allowed = command in allowed
        if expected_allowed != is_allowed:
            add_violation(
                violations,
                "CAPABILITY_COMMAND_VISIBILITY_MISMATCH",
                bundle_id,
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
                "CAPABILITY_COMMAND_FAMILY_EXPECTED_ENABLED",
                bundle_id,
                "expected command family is not enabled",
                expected=family,
                actual="disabled",
            )
    for family in disabled_expected:
        if family_map.get(family, False):
            add_violation(
                violations,
                "CAPABILITY_COMMAND_FAMILY_EXPECTED_DISABLED",
                bundle_id,
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
                "CAPABILITY_UI_BIND_NON_CANONICAL_COMMAND",
                bundle_id,
                "UI action is not in canonical command graph",
                command=action,
            )


def run_pack_gating(repo_root, bundle_id, violations):
    entry = _get_entry(repo_root, bundle_id, violations)
    if entry is None:
        return
    provided = entry.get("provided_capabilities", [])
    acceptance = entry.get("expected_pack_acceptance", "")
    refusal = entry.get("expected_pack_refusal", "")
    if acceptance != "requires_capabilities subset":
        add_violation(
            violations,
            "CAPABILITY_PACK_EXPECTATION_INVALID",
            bundle_id,
            "expected_pack_acceptance mismatch",
            expected="requires_capabilities subset",
            actual=str(acceptance),
        )
    if refusal != "missing capability -> REFUSE_CAPABILITY_MISSING":
        add_violation(
            violations,
            "CAPABILITY_PACK_REFUSAL_EXPECTATION_INVALID",
            bundle_id,
            "expected_pack_refusal mismatch",
            expected="missing capability -> REFUSE_CAPABILITY_MISSING",
            actual=str(refusal),
        )

    matrix = load_capability_matrix(repo_root)
    for probe in matrix.get("capability_sets", []):
        probe_caps = probe.get("provided_capabilities", [])
        result = evaluate_pack_capabilities(provided, probe_caps)
        expected_ok = set(probe_caps).issubset(set(provided))
        if expected_ok and not result["ok"]:
            add_violation(
                violations,
                "CAPABILITY_PACK_REJECTED_COMPATIBLE",
                bundle_id,
                "compatible pack was rejected",
                pack=probe.get("bundle_id", ""),
                expected="ok",
                actual=result["reason"],
            )
        if not expected_ok and (result["ok"] or result["reason"] != REFUSE_CAPABILITY_MISSING):
            add_violation(
                violations,
                "CAPABILITY_PACK_ALLOWED_INCOMPATIBLE",
                bundle_id,
                "incompatible pack was not refused",
                pack=probe.get("bundle_id", ""),
                expected=REFUSE_CAPABILITY_MISSING,
                actual=result["reason"],
            )


def run_epistemics(repo_root, bundle_id, violations):
    entry = _get_entry(repo_root, bundle_id, violations)
    if entry is None:
        return
    commands = parse_command_entries(repo_root)
    allowed, _denied = command_surface(commands, entry.get("provided_capabilities", []))
    for command in allowed:
        if command["epistemic_scope"] not in EPISTEMIC_SCOPES:
            add_violation(
                violations,
                "CAPABILITY_EPISTEMIC_SCOPE_INVALID",
                bundle_id,
                "invalid epistemic_scope",
                command=command["name"],
                actual=command["epistemic_scope"],
            )
            continue
        if command["epistemic_scope"] == "DOM_EPISTEMIC_SCOPE_FULL" and command["app"] != "tools":
            add_violation(
                violations,
                "CAPABILITY_EPISTEMIC_SCOPE_OMNISCIENCE",
                bundle_id,
                "full epistemic scope must remain tools-only",
                command=command["name"],
                expected="tools-only",
                actual=command["app"],
            )


def run_determinism_smoke(repo_root, bundle_id, violations):
    entry = _get_entry(repo_root, bundle_id, violations)
    if entry is None:
        return
    commands = parse_command_entries(repo_root)
    allowed, denied = command_surface(commands, entry.get("provided_capabilities", []))
    payload = {
        "bundle": bundle_id,
        "allowed": sorted(command["name"] for command in allowed),
        "denied": sorted(command["name"] for command in denied),
    }
    digest_a = hash_payload(payload)
    digest_b = hash_payload(payload)
    if digest_a != digest_b:
        add_violation(
            violations,
            "CAPABILITY_DETERMINISM_DIGEST_MISMATCH",
            bundle_id,
            "command surface hash mismatch across identical runs",
            expected=digest_a,
            actual=digest_b,
        )


def run_replay_hash(repo_root, bundle_id, violations):
    entry, fixture = load_capability_fixture(repo_root, bundle_id)
    if entry is None or fixture is None:
        add_violation(
            violations,
            "CAPABILITY_MATRIX_MISSING_ENTRY",
            bundle_id,
            "capability set missing from CAPABILITY_MATRIX.yaml",
        )
        return
    payload = {
        "bundle": bundle_id,
        "fixture": fixture["path"],
        "determinism_expectation": entry.get("determinism_expectation"),
        "epistemic_expectation": entry.get("epistemic_expectation"),
    }
    replay_hash_a = hash_payload(payload)
    replay_hash_b = hash_payload(payload)
    if replay_hash_a != replay_hash_b:
        add_violation(
            violations,
            "CAPABILITY_REPLAY_HASH_MISMATCH",
            bundle_id,
            "replay hash mismatch across identical runs",
            expected=replay_hash_a,
            actual=replay_hash_b,
        )


def run_suite(repo_root, bundle_id, suite):
    violations = []
    if bundle_id not in CAPABILITY_SETS:
        add_violation(violations, "CAPABILITY_INVALID_BUNDLE", bundle_id, "unknown capability set")
    if suite not in SUITE_NAMES:
        add_violation(violations, "CAPABILITY_INVALID_SUITE", bundle_id, "unknown suite", actual=suite)

    if not violations:
        if suite == "test_load_and_validate":
            run_load_and_validate(repo_root, bundle_id, violations)
        elif suite == "test_command_surface":
            run_command_surface(repo_root, bundle_id, violations)
        elif suite == "test_pack_gating":
            run_pack_gating(repo_root, bundle_id, violations)
        elif suite == "test_epistemics":
            run_epistemics(repo_root, bundle_id, violations)
        elif suite == "test_determinism_smoke":
            run_determinism_smoke(repo_root, bundle_id, violations)
        elif suite == "test_replay_hash":
            run_replay_hash(repo_root, bundle_id, violations)

    if violations:
        emit_violations(violations)
        return 1
    print("Capability suite passed: {} {}".format(bundle_id, suite))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Run a single capability matrix suite.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--suite", required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    return run_suite(repo_root, args.bundle_id, args.suite)


if __name__ == "__main__":
    sys.exit(main())
