import argparse
import json
import os
import sys

from invariant_utils import is_override_active


LAW_REL = os.path.join("data", "registries", "law_profiles.json")
EXP_REL = os.path.join("data", "registries", "experience_profiles.json")
PARAM_REL = os.path.join("data", "registries", "parameter_bundles.json")


def _load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: experiences bind to valid law and parameter bundles.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-MODE-AS-PROFILES"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    law_path = os.path.join(repo_root, LAW_REL)
    exp_path = os.path.join(repo_root, EXP_REL)
    param_path = os.path.join(repo_root, PARAM_REL)
    for rel, path in ((LAW_REL, law_path), (EXP_REL, exp_path), (PARAM_REL, param_path)):
        if not os.path.isfile(path):
            print("{}: missing {}".format(invariant_id, rel.replace("\\", "/")))
            return 1

    law_payload = _load_json(law_path)
    exp_payload = _load_json(exp_path)
    param_payload = _load_json(param_path)
    if law_payload is None:
        print("{}: invalid json {}".format(invariant_id, LAW_REL.replace("\\", "/")))
        return 1
    if exp_payload is None:
        print("{}: invalid json {}".format(invariant_id, EXP_REL.replace("\\", "/")))
        return 1
    if param_payload is None:
        print("{}: invalid json {}".format(invariant_id, PARAM_REL.replace("\\", "/")))
        return 1

    laws = ((law_payload.get("record") or {}).get("profiles") or [])
    experiences = ((exp_payload.get("record") or {}).get("profiles") or [])
    bundles = ((param_payload.get("record") or {}).get("bundles") or [])
    if not isinstance(laws, list) or not isinstance(experiences, list) or not isinstance(bundles, list):
        print("{}: registries must expose list payloads".format(invariant_id))
        return 1

    law_ids = {str(row.get("law_profile_id", "")).strip() for row in laws if isinstance(row, dict)}
    bundle_ids = {str(row.get("parameter_bundle_id", "")).strip() for row in bundles if isinstance(row, dict)}

    required_experiences = {
        "exp.observer",
        "exp.survival",
        "exp.hardcore",
        "exp.creative",
        "exp.lab",
        "exp.mission",
    }
    seen_experiences = set()
    violations = []
    for row in experiences:
        if not isinstance(row, dict):
            violations.append("non-object experience entry")
            continue
        exp_id = str(row.get("experience_id", "")).strip()
        law_id = str(row.get("law_profile_id", "")).strip()
        bundle_id = str(row.get("default_parameter_bundle_id", "")).strip()
        if not exp_id:
            violations.append("experience missing experience_id")
            continue
        seen_experiences.add(exp_id)
        if law_id not in law_ids:
            violations.append("{} references unknown law profile {}".format(exp_id, law_id or "<empty>"))
        if bundle_id not in bundle_ids:
            violations.append("{} references unknown parameter bundle {}".format(exp_id, bundle_id or "<empty>"))

    missing = sorted(required_experiences - seen_experiences)
    for exp_id in missing:
        violations.append("missing required experience {}".format(exp_id))

    if violations:
        print("{}: experience profile binding failures".format(invariant_id))
        for item in violations[:32]:
            print("- {}".format(item))
        return 1

    print("experience-law-parameter binding invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
