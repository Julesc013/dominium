import argparse
import json
import os
import sys

from invariant_utils import is_override_active


LAW_REL = os.path.join("data", "registries", "law_profiles.json")


def _load(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: hardcore survival forbids respawn.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SURVIVAL-HARDCORE-NO-RESPAWN"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    law_path = os.path.join(repo_root, LAW_REL)
    if not os.path.isfile(law_path):
        print("{}: missing {}".format(invariant_id, LAW_REL.replace("\\", "/")))
        return 1

    payload = _load(law_path)
    if payload is None:
        print("{}: invalid json {}".format(invariant_id, LAW_REL.replace("\\", "/")))
        return 1

    profiles = ((payload.get("record") or {}).get("profiles") or [])
    hardcore = None
    for row in profiles:
        if isinstance(row, dict) and str(row.get("law_profile_id", "")).strip() == "law.survival.hardcore":
            hardcore = row
            break
    if hardcore is None:
        print("{}: missing law.survival.hardcore".format(invariant_id))
        return 1

    persistence_rules = [str(item).strip() for item in (hardcore.get("persistence_rules") or [])]
    if "persistence.respawn.forbidden" not in persistence_rules:
        print("{}: hardcore must include persistence.respawn.forbidden".format(invariant_id))
        return 1

    forbidden_intents = [str(item).strip() for item in (hardcore.get("forbidden_intent_families") or [])]
    for intent in ("intent.revive", "intent.rollback"):
        if intent not in forbidden_intents:
            print("{}: hardcore must forbid {}".format(invariant_id, intent))
            return 1

    revoked = [str(item).strip() for item in (hardcore.get("capabilities_revoked") or [])]
    for capability in ("intent.revive", "intent.rollback"):
        if capability not in revoked:
            print("{}: hardcore must revoke capability {}".format(invariant_id, capability))
            return 1

    print("hardcore no-respawn invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
