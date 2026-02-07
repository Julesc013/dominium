import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stage_matrix_common import STAGES, add_violation, command_surface, emit_violations, parse_command_entries


def main():
    violations = []
    repo_root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    commands = parse_command_entries(repo_root)
    for stage_id in STAGES[:-1]:
        allowed, _ = command_surface(commands, stage_id)
        allowed_names = {command["name"] for command in allowed}
        if "ai" in allowed_names:
            add_violation(
                violations,
                "STAGE_REGRESSION_FUTURE_LEAK",
                stage_id,
                "future affordance leaked before stage 6",
                command="ai",
                expected="denied",
                actual="allowed",
            )

    if violations:
        emit_violations(violations)
        return 1
    print("Stage regression passed: no future affordances before stage 6")
    return 0


if __name__ == "__main__":
    sys.exit(main())

