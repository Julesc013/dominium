import argparse
import os
import sys

from invariant_utils import is_override_active


REGISTRY_REL = os.path.join("client", "core", "client_commands_registry.c")
BRIDGE_REL = os.path.join("client", "core", "client_command_bridge.c")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: UI surfaces are entitlement-gated.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-UI-ENTITLEMENT-GATING"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    registry_path = os.path.join(repo_root, REGISTRY_REL)
    bridge_path = os.path.join(repo_root, BRIDGE_REL)
    if not os.path.isfile(registry_path):
        print("{}: missing {}".format(invariant_id, REGISTRY_REL.replace("\\", "/")))
        return 1
    if not os.path.isfile(bridge_path):
        print("{}: missing {}".format(invariant_id, BRIDGE_REL.replace("\\", "/")))
        return 1

    registry_text = _read(registry_path)
    bridge_text = _read(bridge_path)
    if not registry_text or not bridge_text:
        print("{}: unable to read required source files".format(invariant_id))
        return 1

    required_pairs = (
        ("client.ui.hud.show", "ui.hud.basic"),
        ("client.ui.overlay.world_layers.show", "ui.overlay.world_layers"),
        ("client.console.open", "ui.console.command.read_only"),
        ("client.console.open.readwrite", "ui.console.command.read_write"),
        ("client.camera.freecam.enable", "camera.mode.observer_truth"),
    )
    violations = []
    for command_id, entitlement in required_pairs:
        if command_id not in registry_text:
            violations.append("missing command {}".format(command_id))
        if entitlement not in registry_text:
            violations.append("missing entitlement {}".format(entitlement))

    for marker in ("entitlement_allowed(", "refuse.entitlement_required", "refuse.profile_not_selected"):
        if marker not in bridge_text:
            violations.append("missing bridge marker {}".format(marker))

    if violations:
        print("{}: entitlement gating failures".format(invariant_id))
        for item in violations[:32]:
            print("- {}".format(item))
        return 1

    print("ui-entitlement-gating invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
