import argparse
import json
import os
import sys

from invariant_utils import is_override_active


LAW_PROFILES_REL = os.path.join("data", "registries", "law_profiles.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: survival law forbids nondiegetic lenses.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SURVIVAL-NO-NONDIEGETIC-LENSES"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    path = os.path.join(repo_root, LAW_PROFILES_REL)
    if not os.path.isfile(path):
        print("{}: missing {}".format(invariant_id, LAW_PROFILES_REL.replace("\\", "/")))
        return 1

    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        print("{}: invalid json {}".format(invariant_id, LAW_PROFILES_REL.replace("\\", "/")))
        return 1

    profiles = ((payload.get("record") or {}).get("profiles") or [])
    if not isinstance(profiles, list):
        print("{}: profiles must be list".format(invariant_id))
        return 1

    profile = None
    for row in profiles:
        if isinstance(row, dict) and str(row.get("law_profile_id", "")).strip() == "survival.softcore":
            profile = row
            break
    if profile is None:
        print("{}: missing law profile survival.softcore".format(invariant_id))
        return 1

    forbidden = profile.get("forbidden_lenses")
    if not isinstance(forbidden, list):
        print("{}: survival.softcore forbidden_lenses must be list".format(invariant_id))
        return 1

    if not any(str(item).strip().startswith("lens.nondiegetic") for item in forbidden):
        print("{}: survival.softcore must forbid lens.nondiegetic.*".format(invariant_id))
        return 1

    print("survival-no-nondiegetic-lenses invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
