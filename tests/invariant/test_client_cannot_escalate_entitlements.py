import argparse
import os
import sys

from invariant_utils import is_override_active


SERVER_CPP_REL = os.path.join("server", "authority", "dom_server_authority.cpp")
CLIENT_BRIDGE_REL = os.path.join("client", "core", "client_command_bridge.c")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: client entitlement escalation must be rejected.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    server_cpp = os.path.join(repo_root, SERVER_CPP_REL)
    client_bridge = os.path.join(repo_root, CLIENT_BRIDGE_REL)
    if not os.path.isfile(server_cpp):
        print("{}: missing {}".format(invariant_id, SERVER_CPP_REL.replace("\\", "/")))
        return 1
    if not os.path.isfile(client_bridge):
        print("{}: missing {}".format(invariant_id, CLIENT_BRIDGE_REL.replace("\\", "/")))
        return 1

    server_text = _read(server_cpp)
    client_text = _read(client_bridge)
    required_server = (
        "dom_server_authority_check_with_context",
        "server_authoritative",
        "DOM_AUTH_REFUSE_PROFILE_INSUFFICIENT",
        "DOM_AUTH_PROFILE_FULL_PLAYER",
    )
    required_client = (
        "refuse.entitlement_required",
        "authority_context_id",
    )
    for marker in required_server:
        if marker not in server_text:
            print("{}: {} missing {}".format(invariant_id, SERVER_CPP_REL.replace("\\", "/"), marker))
            return 1
    for marker in required_client:
        if marker not in client_text:
            print("{}: {} missing {}".format(invariant_id, CLIENT_BRIDGE_REL.replace("\\", "/"), marker))
            return 1

    print("client-escalation rejection invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
