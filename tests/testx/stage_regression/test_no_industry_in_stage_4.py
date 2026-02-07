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
    allowed, _ = command_surface(commands, "STAGE_4_PRE_INDUSTRY")
    allowed_names = {command["name"] for command in allowed}
    for forbidden in ("network-create", "network-list", "ai"):
        if forbidden in allowed_names:
            add_violation(
                violations,
                "STAGE_REGRESSION_INDUSTRY_LEAK",
                "STAGE_4_PRE_INDUSTRY",
                "industry/future command leaked into stage 4",
                command=forbidden,
                expected="denied",
                actual="allowed",
            )

    if violations:
        emit_violations(violations)
        return 1
    print("Stage regression passed: no industry in stage 4")
    return 0


if __name__ == "__main__":
    sys.exit(main())

