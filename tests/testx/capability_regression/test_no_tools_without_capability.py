import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from capability_matrix_common import add_violation, command_surface, emit_violations, parse_command_entries


def main():
    violations = []
    commands = parse_command_entries(os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    allowed, _ = command_surface(commands, ["dominium.capability.world.life.nonintelligent"])
    allowed_names = {command["name"] for command in allowed}
    if "agent-add" in allowed_names:
        add_violation(
            violations,
            "CAPABILITY_REGRESSION_TOOL_LEAK",
            "CAPSET_WORLD_LIFE_NONINTELLIGENT",
            "tooling command leaked without capability",
            command="agent-add",
            expected="denied",
            actual="allowed",
        )

    if violations:
        emit_violations(violations)
        return 1
    print("Capability regression passed: no tooling without capability")
    return 0


if __name__ == "__main__":
    sys.exit(main())
