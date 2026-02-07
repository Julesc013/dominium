import argparse
import os
import sys

from stage_matrix_common import STAGES, add_violation, emit_violations, load_stage_matrix


SUITE_NAMES = (
    "test_load_and_validate",
    "test_command_surface",
    "test_pack_gating",
    "test_epistemics",
    "test_determinism_smoke",
    "test_replay_hash",
)

STAGE_DIRS = {
    "STAGE_0_NONBIO_WORLD": "stage_0_nonbio",
    "STAGE_1_NONINTELLIGENT_LIFE": "stage_1_nonintelligent_life",
    "STAGE_2_INTELLIGENT_PRE_TOOL": "stage_2_intelligent_pre_tool",
    "STAGE_3_PRE_TOOL_WORLD": "stage_3_pre_tool_world",
    "STAGE_4_PRE_INDUSTRY": "stage_4_pre_industry",
    "STAGE_5_PRE_PRESENT": "stage_5_pre_present",
    "STAGE_6_FUTURE": "stage_6_future",
}


def main():
    parser = argparse.ArgumentParser(description="Stage matrix structural contracts.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = []
    matrix = load_stage_matrix(repo_root)
    entries = matrix.get("stages", [])
    seen = set()

    if matrix.get("schema_id") != "dominium.testx.stage_matrix":
        add_violation(violations, "STAGE_MATRIX_SCHEMA_ID", "", "matrix schema_id mismatch", expected="dominium.testx.stage_matrix", actual=str(matrix.get("schema_id")))
    if matrix.get("schema_version") != "1.0.0":
        add_violation(violations, "STAGE_MATRIX_SCHEMA_VERSION", "", "matrix schema_version mismatch", expected="1.0.0", actual=str(matrix.get("schema_version")))
    if not isinstance(entries, list):
        add_violation(violations, "STAGE_MATRIX_STAGES_MISSING", "", "matrix stages must be a list")
        entries = []

    for entry in entries:
        stage_id = entry.get("stage_id")
        if stage_id not in STAGES:
            add_violation(violations, "STAGE_MATRIX_STAGE_INVALID", str(stage_id), "invalid stage id")
            continue
        if stage_id in seen:
            add_violation(violations, "STAGE_MATRIX_STAGE_DUPLICATE", stage_id, "duplicate stage entry")
            continue
        seen.add(stage_id)

        fixture = entry.get("fixture", "")
        expected_fixture = "tests/fixtures/worlds/{}/world_stage.json".format(STAGE_DIRS[stage_id])
        if fixture != expected_fixture:
            add_violation(
                violations,
                "STAGE_MATRIX_FIXTURE_PATH",
                stage_id,
                "fixture path mismatch",
                expected=expected_fixture,
                actual=str(fixture),
            )
        if not os.path.isfile(os.path.join(repo_root, fixture)):
            add_violation(violations, "STAGE_MATRIX_FIXTURE_MISSING", stage_id, "fixture file missing", fixture=fixture)

        suites = entry.get("required_test_suites")
        if suites != list(SUITE_NAMES):
            add_violation(
                violations,
                "STAGE_MATRIX_REQUIRED_SUITES",
                stage_id,
                "required_test_suites must match canonical suite list",
                expected="|".join(SUITE_NAMES),
                actual="|".join(suites or []),
            )

        tests = entry.get("tests")
        if not isinstance(tests, list):
            add_violation(violations, "STAGE_MATRIX_TESTS_MISSING", stage_id, "tests must be a list")
            tests = []
        expected_tests = [
            "tests/testx/stages/{}/{}.py".format(STAGE_DIRS[stage_id], suite_name)
            for suite_name in SUITE_NAMES
        ]
        if tests != expected_tests:
            add_violation(
                violations,
                "STAGE_MATRIX_TESTS_PATHS",
                stage_id,
                "tests paths must match canonical per-stage suite paths",
                expected="|".join(expected_tests),
                actual="|".join(tests),
            )
        for test_path in tests:
            if not os.path.isfile(os.path.join(repo_root, test_path)):
                add_violation(violations, "STAGE_MATRIX_TEST_FILE_MISSING", stage_id, "test file missing", actual=test_path)

    for stage_id in STAGES:
        if stage_id not in seen:
            add_violation(violations, "STAGE_MATRIX_STAGE_MISSING", stage_id, "missing stage entry")

    regression_tests = matrix.get("regression_tests")
    if not isinstance(regression_tests, list):
        add_violation(violations, "STAGE_MATRIX_REGRESSION_MISSING", "", "regression_tests must be a list")
        regression_tests = []
    for test_path in regression_tests:
        if not os.path.isfile(os.path.join(repo_root, test_path)):
            add_violation(violations, "STAGE_MATRIX_REGRESSION_FILE_MISSING", "", "regression test file missing", actual=test_path)

    if violations:
        emit_violations(violations)
        return 1

    print("Stage matrix contracts OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

