import argparse
import os
import sys

from invariant_utils import is_override_active


LAW_REL = os.path.join("data", "registries", "law_profiles.json")
BRIDGE_REL = os.path.join("client", "core", "client_command_bridge.c")
REGISTRY_REL = os.path.join("client", "core", "client_commands_registry.c")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: survival profile has no freecam entitlement.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SURVIVAL-DIEGETIC-CONTRACT"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    law_path = os.path.join(repo_root, LAW_REL)
    bridge_path = os.path.join(repo_root, BRIDGE_REL)
    registry_path = os.path.join(repo_root, REGISTRY_REL)
    for rel, path in ((LAW_REL, law_path), (BRIDGE_REL, bridge_path), (REGISTRY_REL, registry_path)):
        if not os.path.isfile(path):
            print("{}: missing {}".format(invariant_id, rel.replace("\\", "/")))
            return 1

    law_text = _read(law_path)
    bridge_text = _read(bridge_path)
    registry_text = _read(registry_path)

    if "law.survival.default" not in law_text or "camera.mode.observer_truth" not in law_text:
        print("{}: survival law must revoke camera.mode.observer_truth".format(invariant_id))
        return 1
    if "{ \"exp.survival\", \"law.survival.default\", 1, 0, 0, 0, 0, 0 }" not in bridge_text:
        print("{}: survival bridge binding must keep freecam disabled".format(invariant_id))
        return 1
    if "client.camera.freecam.enable" not in registry_text:
        print("{}: missing canonical freecam command metadata".format(invariant_id))
        return 1
    if "camera.mode.observer_truth" not in registry_text:
        print("{}: freecam command must require observer entitlement".format(invariant_id))
        return 1

    print("survival-no-freecam invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
