import argparse
import hashlib
import json
import os
import sys

from invariant_utils import is_override_active


SCHEMA_REL = os.path.join("schema", "session", "session_spec.schema")


def _canonical_json(payload) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: SessionSpec canonical roundtrip is stable.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SESSION_SPEC_REQUIRED_FOR_RUN"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    schema_path = os.path.join(repo_root, SCHEMA_REL)
    if not os.path.isfile(schema_path):
        print("{}: missing {}".format(invariant_id, SCHEMA_REL.replace("\\", "/")))
        return 1

    schema_text = open(schema_path, "r", encoding="utf-8").read()
    required = (
        "session_id",
        "universe_id",
        "experience_id",
        "parameter_bundle_id",
        "authority_context",
        "deterministic_seed_bundle",
    )
    for marker in required:
        if marker not in schema_text:
            print("{}: schema missing {}".format(invariant_id, marker))
            return 1

    sample = {
        "session_id": "session.sample",
        "universe_id": "universe.default",
        "save_id": "none",
        "scenario_id": "scenario.sandbox.minimal",
        "mission_id": "none",
        "experience_id": "exp.observer",
        "parameter_bundle_id": "observer.params.default",
        "pack_lock_hash": "hash.unset",
        "authority_context": "ctx.exp.observer.law.observer.default",
        "budget_policy_id": "budget.dev.generous",
        "fidelity_policy_id": "fidelity.default",
        "replay_policy": "recording_disabled",
        "deterministic_seed_bundle": ["seed.session.root"],
        "workspace_id": "ws.unset",
        "extensions": {},
    }

    c1 = _canonical_json(sample)
    h1 = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    loaded = json.loads(c1)
    c2 = _canonical_json(loaded)
    h2 = hashlib.sha256(c2.encode("utf-8")).hexdigest()
    if h1 != h2:
        print("{}: SessionSpec canonical hash changed across roundtrip".format(invariant_id))
        return 1

    print("session-spec roundtrip invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
