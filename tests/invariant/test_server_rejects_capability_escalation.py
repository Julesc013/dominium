import argparse
import os
import sys

from invariant_utils import is_override_active


SERVER_CPP_REL = os.path.join("server", "authority", "dom_server_authority.cpp")
SERVER_H_REL = os.path.join("server", "authority", "dom_server_authority.h")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: server rejects client capability escalation.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    header = os.path.join(repo_root, SERVER_H_REL)
    impl = os.path.join(repo_root, SERVER_CPP_REL)
    if not os.path.isfile(header) or not os.path.isfile(impl):
        print("{}: missing server authority sources".format(invariant_id))
        return 1

    header_text = _read(header)
    impl_text = _read(impl)
    required = (
        "dom_server_authority_check_with_context",
        "DOM_AUTH_REFUSE_PROFILE_INSUFFICIENT",
        "DOM_AUTH_REFUSE_ENTITLEMENT_MISSING",
        "server_authoritative",
    )
    for marker in required:
        if marker not in header_text and marker not in impl_text:
            print("{}: missing server escalation marker {}".format(invariant_id, marker))
            return 1

    print("server-capability-escalation invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
