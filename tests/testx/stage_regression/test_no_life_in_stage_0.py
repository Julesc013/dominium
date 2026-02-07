import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stage_matrix_common import add_violation, command_surface, emit_violations, parse_command_entries


def main():
    violations = []
    commands = parse_command_entries(os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    allowed, _ = command_surface(commands, "STAGE_0_NONBIO_WORLD")
    allowed_names = {command["name"] for command in allowed}
    for forbidden in ("agents", "agent-add"):
        if forbidden in allowed_names:
            add_violation(
                violations,
                "STAGE_REGRESSION_LIFE_LEAK",
                "STAGE_0_NONBIO_WORLD",
                "life command leaked into stage 0",
                command=forbidden,
                expected="denied",
                actual="allowed",
            )

    if violations:
        emit_violations(violations)
        return 1
    print("Stage regression passed: no life in stage 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())

