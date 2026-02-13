import argparse
import os
import sys

from invariant_utils import is_override_active


LAW_REL = os.path.join("data", "registries", "law_profiles.json")
BRIDGE_REL = os.path.join("client", "core", "client_command_bridge.c")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: survival profile has no console entitlement.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SURVIVAL-DIEGETIC-CONTRACT"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    law_path = os.path.join(repo_root, LAW_REL)
    bridge_path = os.path.join(repo_root, BRIDGE_REL)
    if not os.path.isfile(law_path):
        print("{}: missing {}".format(invariant_id, LAW_REL.replace("\\", "/")))
        return 1
    if not os.path.isfile(bridge_path):
        print("{}: missing {}".format(invariant_id, BRIDGE_REL.replace("\\", "/")))
        return 1

    law_text = _read(law_path)
    bridge_text = _read(bridge_path)

    if "law.survival.default" not in law_text:
        print("{}: missing law.survival.default".format(invariant_id))
        return 1
    if "\"forbidden_lenses\": [" not in law_text or "lens.nondiegetic.*" not in law_text:
        print("{}: law.survival.default must forbid nondiegetic lenses".format(invariant_id))
        return 1

    required_bridge = (
        "{ \"exp.survival\", \"law.survival.default\", 1, 0, 0, 0, 0, 0 }",
        "client.console.open",
        "refuse.entitlement_required",
    )
    for marker in required_bridge:
        if marker not in bridge_text:
            print("{}: {} missing marker {}".format(invariant_id, BRIDGE_REL.replace("\\", "/"), marker))
            return 1

    print("survival-no-console invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
