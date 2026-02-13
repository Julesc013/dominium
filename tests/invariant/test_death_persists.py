import argparse
import json
import os
import sys

from invariant_utils import is_override_active


LAW_REL = os.path.join("data", "registries", "law_profiles.json")
SLICE_REL = os.path.join("data", "registries", "survival_vertical_slice.json")


def _load(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: survival death state is represented and persisted by contract.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SURVIVAL-DEATH-PERSISTS"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    law_path = os.path.join(repo_root, LAW_REL)
    slice_path = os.path.join(repo_root, SLICE_REL)
    for rel, path in ((LAW_REL, law_path), (SLICE_REL, slice_path)):
        if not os.path.isfile(path):
            print("{}: missing {}".format(invariant_id, rel.replace("\\", "/")))
            return 1

    law_payload = _load(law_path)
    slice_payload = _load(slice_path)
    if law_payload is None:
        print("{}: invalid json {}".format(invariant_id, LAW_REL.replace("\\", "/")))
        return 1
    if slice_payload is None:
        print("{}: invalid json {}".format(invariant_id, SLICE_REL.replace("\\", "/")))
        return 1

    field_rows = ((slice_payload.get("record") or {}).get("agent_fields") or [])
    field_ids = {str(row.get("field_id", "")).strip() for row in field_rows if isinstance(row, dict)}
    for field_id in ("status.alive", "health.hp"):
        if field_id not in field_ids:
            print("{}: missing agent field {}".format(invariant_id, field_id))
            return 1

    process_rows = ((slice_payload.get("record") or {}).get("processes") or [])
    process_ids = {str(row.get("process_id", "")).strip() for row in process_rows if isinstance(row, dict)}
    if "process.death_process" not in process_ids:
        print("{}: missing process.death_process".format(invariant_id))
        return 1

    profiles = ((law_payload.get("record") or {}).get("profiles") or [])
    by_id = {}
    for row in profiles:
        if isinstance(row, dict):
            law_id = str(row.get("law_profile_id", "")).strip()
            if law_id:
                by_id[law_id] = row

    for law_id in ("law.survival.softcore", "law.survival.hardcore"):
        row = by_id.get(law_id)
        if not isinstance(row, dict):
            print("{}: missing {}".format(invariant_id, law_id))
            return 1
        persistence = [str(item).strip() for item in (row.get("persistence_rules") or [])]
        if not persistence:
            print("{}: {} must declare persistence rules".format(invariant_id, law_id))
            return 1
        if not any(item.startswith("persistence.respawn.") for item in persistence):
            print("{}: {} must define respawn persistence policy".format(invariant_id, law_id))
            return 1

    print("survival death persistence invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
