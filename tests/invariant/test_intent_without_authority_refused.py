import argparse
import os
import sys

from invariant_utils import is_override_active


CLIENT_BRIDGE_REL = os.path.join("client", "core", "client_command_bridge.c")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: intent dispatch without authority context must refuse.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-AUTHORITY-CONTEXT-REQUIRED"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    path = os.path.join(repo_root, CLIENT_BRIDGE_REL)
    if not os.path.isfile(path):
        print("{}: missing {}".format(invariant_id, CLIENT_BRIDGE_REL.replace("\\", "/")))
        return 1

    text = _read(path)
    required = (
        "authority_context_id",
        "ctx.unset",
        "refuse.authority_context_required",
        "client_command_capabilities_allowed(",
    )
    for marker in required:
        if marker not in text:
            print("{}: {} missing marker {}".format(invariant_id, CLIENT_BRIDGE_REL.replace("\\", "/"), marker))
            return 1

    print("intent-without-authority refusal invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
