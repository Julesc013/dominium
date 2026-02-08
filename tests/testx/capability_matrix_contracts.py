import argparse
import os
import sys

from capability_matrix_common import (
    CAPABILITY_SETS,
    add_violation,
    emit_violations,
    load_capability_matrix,
)


SUITE_NAMES = (
    "test_load_and_validate",
    "test_command_surface",
    "test_pack_gating",
    "test_epistemics",
    "test_determinism_smoke",
    "test_replay_hash",
)

CAPABILITY_SET_DIRS = {
    "CAPSET_WORLD_NONBIO": "stage_0_nonbio",
    "CAPSET_WORLD_LIFE_NONINTELLIGENT": "stage_1_nonintelligent_life",
    "CAPSET_WORLD_LIFE_INTELLIGENT": "stage_2_intelligent_pre_tool",
    "CAPSET_WORLD_PRETOOL": "stage_3_pre_tool_world",
    "CAPSET_SOCIETY_INSTITUTIONS": "stage_4_pre_industry",
    "CAPSET_INFRASTRUCTURE_INDUSTRY": "stage_5_pre_present",
    "CAPSET_FUTURE_AFFORDANCES": "stage_6_future",
}


def main():
    parser = argparse.ArgumentParser(description="Capability matrix structural contracts.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = []
    matrix = load_capability_matrix(repo_root)
    entries = matrix.get("capability_sets", [])
    seen = set()

    if matrix.get("schema_id") != "dominium.testx.capability_matrix":
        add_violation(
            violations,
            "CAPABILITY_MATRIX_SCHEMA_ID",
            "",
            "matrix schema_id mismatch",
            expected="dominium.testx.capability_matrix",
            actual=str(matrix.get("schema_id")),
        )
    if matrix.get("schema_version") != "1.0.0":
        add_violation(
            violations,
            "CAPABILITY_MATRIX_SCHEMA_VERSION",
            "",
            "matrix schema_version mismatch",
            expected="1.0.0",
            actual=str(matrix.get("schema_version")),
        )
    if not isinstance(entries, list):
        add_violation(
            violations,
            "CAPABILITY_MATRIX_SETS_MISSING",
            "",
            "matrix capability_sets must be a list",
        )
        entries = []

    for entry in entries:
        bundle_id = entry.get("bundle_id")
        if bundle_id not in CAPABILITY_SETS:
            add_violation(
                violations,
                "CAPABILITY_MATRIX_SET_INVALID",
                str(bundle_id),
                "invalid capability set id",
            )
            continue
        if bundle_id in seen:
            add_violation(
                violations,
                "CAPABILITY_MATRIX_SET_DUPLICATE",
                bundle_id,
                "duplicate capability set entry",
            )
            continue
        seen.add(bundle_id)

        set_dir = CAPABILITY_SET_DIRS[bundle_id]
        fixture = entry.get("fixture", "")
        expected_fixture = "tests/fixtures/worlds/{}/world_stage.json".format(set_dir)
        if fixture != expected_fixture:
            add_violation(
                violations,
                "CAPABILITY_MATRIX_FIXTURE_PATH",
                bundle_id,
                "fixture path mismatch",
                expected=expected_fixture,
                actual=str(fixture),
            )
        if not os.path.isfile(os.path.join(repo_root, fixture)):
            add_violation(
                violations,
                "CAPABILITY_MATRIX_FIXTURE_MISSING",
                bundle_id,
                "fixture file missing",
                fixture=fixture,
            )

        suites = entry.get("required_test_suites")
        if suites != list(SUITE_NAMES):
            add_violation(
                violations,
                "CAPABILITY_MATRIX_REQUIRED_SUITES",
                bundle_id,
                "required_test_suites must match canonical suite list",
                expected="|".join(SUITE_NAMES),
                actual="|".join(suites or []),
            )

        tests = entry.get("tests")
        if not isinstance(tests, list):
            add_violation(
                violations,
                "CAPABILITY_MATRIX_TESTS_MISSING",
                bundle_id,
                "tests must be a list",
            )
            tests = []
        expected_tests = [
            "tests/testx/stages/{}/{}.py".format(set_dir, suite_name)
            for suite_name in SUITE_NAMES
        ]
        if tests != expected_tests:
            add_violation(
                violations,
                "CAPABILITY_MATRIX_TESTS_PATHS",
                bundle_id,
                "tests paths must match canonical per-capability suite paths",
                expected="|".join(expected_tests),
                actual="|".join(tests),
            )
        for test_path in tests:
            if not os.path.isfile(os.path.join(repo_root, test_path)):
                add_violation(
                    violations,
                    "CAPABILITY_MATRIX_TEST_FILE_MISSING",
                    bundle_id,
                    "test file missing",
                    actual=test_path,
                )

    for bundle_id in CAPABILITY_SETS:
        if bundle_id not in seen:
            add_violation(
                violations,
                "CAPABILITY_MATRIX_SET_MISSING",
                bundle_id,
                "missing capability set entry",
            )

    regression_tests = matrix.get("regression_tests")
    if not isinstance(regression_tests, list):
        add_violation(
            violations,
            "CAPABILITY_MATRIX_REGRESSION_MISSING",
            "",
            "regression_tests must be a list",
        )
        regression_tests = []
    for test_path in regression_tests:
        if not os.path.isfile(os.path.join(repo_root, test_path)):
            add_violation(
                violations,
                "CAPABILITY_MATRIX_REGRESSION_FILE_MISSING",
                "",
                "regression test file missing",
                actual=test_path,
            )

    if violations:
        emit_violations(violations)
        return 1

    print("Capability matrix contracts OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
