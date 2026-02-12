import argparse
import os
import sys

from invariant_utils import is_override_active


SCHEMA_REL = os.path.join("schema", "session", "session_spec.schema")
BRIDGE_REL = os.path.join("client", "core", "client_command_bridge.c")
REGISTRY_REL = os.path.join("client", "core", "client_commands_registry.c")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: launches must materialize SessionSpec.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SESSION_SPEC_REQUIRED_FOR_RUN"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    schema_path = os.path.join(repo_root, SCHEMA_REL)
    bridge_path = os.path.join(repo_root, BRIDGE_REL)
    registry_path = os.path.join(repo_root, REGISTRY_REL)
    for rel, path in ((SCHEMA_REL, schema_path), (BRIDGE_REL, bridge_path), (REGISTRY_REL, registry_path)):
        if not os.path.isfile(path):
            print("{}: missing {}".format(invariant_id, rel.replace("\\", "/")))
            return 1

    bridge_text = _read(bridge_path)
    registry_text = _read(registry_path)
    required_markers = (
        "client.session.create_from_selection",
        "session_id=session.selected",
        "authority_context_id=",
        "pack_lock_hash=",
        "budget_policy_id=",
        "fidelity_policy_id=",
        "seed_bundle=",
    )
    for marker in required_markers:
        if marker not in bridge_text and marker not in registry_text:
            print("{}: missing launch marker {}".format(invariant_id, marker))
            return 1

    print("session-spec launch requirement invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
