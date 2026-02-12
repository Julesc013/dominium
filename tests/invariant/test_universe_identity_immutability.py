import argparse
import os
import sys

from invariant_utils import is_override_active


IDENTITY_REL = os.path.join("schema", "universe", "universe_identity.schema")
STATE_REL = os.path.join("schema", "universe", "universe_state.schema")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _scan_runtime_for_mutation(repo_root: str):
    roots = ("engine", "game", "client", "server", "launcher", "setup")
    exts = (".c", ".cc", ".cpp", ".h", ".hpp", ".inl", ".py")
    tokens = (
        "set_universe_identity(",
        "update_universe_identity(",
        "mutate_universe_identity(",
        "rewrite_universe_identity(",
    )
    violations = []
    for rel_root in roots:
        abs_root = os.path.join(repo_root, rel_root)
        if not os.path.isdir(abs_root):
            continue
        for dirpath, dirnames, filenames in os.walk(abs_root):
            dirnames[:] = [name for name in dirnames if name not in {".git", ".vs", "out", "dist", "__pycache__"}]
            for filename in filenames:
                if not filename.lower().endswith(exts):
                    continue
                path = os.path.join(dirpath, filename)
                text = _read(path).lower()
                for token in tokens:
                    if token in text:
                        rel = path.replace("\\", "/")
                        violations.append("{} -> {}".format(rel, token))
                        break
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: UniverseIdentity stays immutable post-create.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-UNIVERSE_IDENTITY_IMMUTABLE"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    identity_path = os.path.join(repo_root, IDENTITY_REL)
    state_path = os.path.join(repo_root, STATE_REL)
    if not os.path.isfile(identity_path):
        print("{}: missing {}".format(invariant_id, IDENTITY_REL.replace("\\", "/")))
        return 1
    if not os.path.isfile(state_path):
        print("{}: missing {}".format(invariant_id, STATE_REL.replace("\\", "/")))
        return 1

    identity_text = _read(identity_path)
    state_text = _read(state_path)
    required_identity = (
        "universe_id",
        "global_seed",
        "domain_binding_ids",
        "physics_profile_id",
        "base_scenario_id",
        "compatibility_schema_refs",
        "immutable_after_create: bool",
    )
    required_state = (
        "universe_id",
        "time_ref",
        "refinement_state_refs",
        "agent_state_refs",
        "law_state_refs",
        "save_checkpoint_refs",
        "history_log_anchors",
    )
    for token in required_identity:
        if token not in identity_text:
            print("{}: {} missing {}".format(invariant_id, IDENTITY_REL.replace("\\", "/"), token))
            return 1
    for token in required_state:
        if token not in state_text:
            print("{}: {} missing {}".format(invariant_id, STATE_REL.replace("\\", "/"), token))
            return 1

    violations = _scan_runtime_for_mutation(repo_root)
    if violations:
        print("{}: forbidden universe identity mutation tokens found".format(invariant_id))
        for item in violations[:32]:
            print("- {}".format(item))
        return 1

    print("universe-identity-immutability invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
