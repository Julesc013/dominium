import argparse
import os
import sys

from invariant_utils import is_override_active


SCHEMA_REL = os.path.join("schema", "authority", "authority_context.schema")
CLIENT_REL = os.path.join("client", "core", "client_command_bridge.c")
SERVER_H_REL = os.path.join("server", "authority", "dom_server_authority.h")
SERVER_CPP_REL = os.path.join("server", "authority", "dom_server_authority.cpp")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: AuthorityContext required for intent paths.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    schema_path = os.path.join(repo_root, SCHEMA_REL)
    client_path = os.path.join(repo_root, CLIENT_REL)
    server_h_path = os.path.join(repo_root, SERVER_H_REL)
    server_cpp_path = os.path.join(repo_root, SERVER_CPP_REL)
    for rel, path in (
        (SCHEMA_REL, schema_path),
        (CLIENT_REL, client_path),
        (SERVER_H_REL, server_h_path),
        (SERVER_CPP_REL, server_cpp_path),
    ):
        if not os.path.isfile(path):
            print("{}: missing {}".format(invariant_id, rel.replace("\\", "/")))
            return 1

    schema_text = _read(schema_path)
    required_schema = (
        "authority_origin",
        "experience_id",
        "law_profile_id",
        "entitlements",
        "capability_set_hash",
        "epistemic_scope_id",
        "server_authoritative",
    )
    for marker in required_schema:
        if marker not in schema_text:
            print("{}: {} missing {}".format(invariant_id, SCHEMA_REL.replace("\\", "/"), marker))
            return 1

    client_text = _read(client_path)
    for marker in ("authority_context_id", "ctx.unset"):
        if marker not in client_text:
            print("{}: {} missing marker {}".format(invariant_id, CLIENT_REL.replace("\\", "/"), marker))
            return 1

    server_h_text = _read(server_h_path)
    server_cpp_text = _read(server_cpp_path)
    if "dom_authority_context" not in server_h_text:
        print("{}: {} missing dom_authority_context".format(invariant_id, SERVER_H_REL.replace("\\", "/")))
        return 1
    if "dom_server_authority_check_with_context" not in server_h_text:
        print("{}: {} missing dom_server_authority_check_with_context".format(invariant_id, SERVER_H_REL.replace("\\", "/")))
        return 1
    if "server_authoritative" not in server_cpp_text:
        print("{}: {} missing server_authoritative marker".format(invariant_id, SERVER_CPP_REL.replace("\\", "/")))
        return 1

    print("authority-context enforcement invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
