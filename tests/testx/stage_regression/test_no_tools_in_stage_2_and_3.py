import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stage_matrix_common import add_violation, command_surface, emit_violations, parse_command_entries


def main():
    violations = []
    repo_root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    commands = parse_command_entries(repo_root)
    gated_names = ("institution-create", "institution-list", "network-create", "network-list", "ai")
    for stage_id in ("STAGE_2_INTELLIGENT_PRE_TOOL", "STAGE_3_PRE_TOOL_WORLD"):
        allowed, _ = command_surface(commands, stage_id)
        allowed_names = {command["name"] for command in allowed}
        for forbidden in gated_names:
            if forbidden in allowed_names:
                add_violation(
                    violations,
                    "STAGE_REGRESSION_TOOLS_LEAK",
                    stage_id,
                    "higher-order command leaked into stage 2/3",
                    command=forbidden,
                    expected="denied",
                    actual="allowed",
                )

    if violations:
        emit_violations(violations)
        return 1
    print("Stage regression passed: no tools in stage 2 and 3")
    return 0


if __name__ == "__main__":
    sys.exit(main())

