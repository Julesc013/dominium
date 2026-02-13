import argparse
import json
import os
import sys

from invariant_utils import is_override_active


SLICE_REL = os.path.join("data", "registries", "survival_vertical_slice.json")
PARAM_REL = os.path.join("data", "registries", "parameter_bundles.json")


def _load(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: shelter process contract reduces exposure.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SURVIVAL-SHELTER-REDUCES-EXPOSURE"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    slice_path = os.path.join(repo_root, SLICE_REL)
    param_path = os.path.join(repo_root, PARAM_REL)
    for rel, path in ((SLICE_REL, slice_path), (PARAM_REL, param_path)):
        if not os.path.isfile(path):
            print("{}: missing {}".format(invariant_id, rel.replace("\\", "/")))
            return 1

    slice_payload = _load(slice_path)
    param_payload = _load(param_path)
    if slice_payload is None:
        print("{}: invalid json {}".format(invariant_id, SLICE_REL.replace("\\", "/")))
        return 1
    if param_payload is None:
        print("{}: invalid json {}".format(invariant_id, PARAM_REL.replace("\\", "/")))
        return 1

    assemblies = ((slice_payload.get("record") or {}).get("assemblies") or [])
    processes = ((slice_payload.get("record") or {}).get("processes") or [])
    process_ids = {str(row.get("process_id", "")).strip() for row in processes if isinstance(row, dict)}

    shelter = None
    for row in assemblies:
        if isinstance(row, dict) and str(row.get("assembly_id", "")).strip() == "assembly.shelter_basic":
            shelter = row
            break
    if shelter is None:
        print("{}: missing assembly.shelter_basic".format(invariant_id))
        return 1
    if "shelter.rating" not in [str(field).strip() for field in (shelter.get("fields") or [])]:
        print("{}: shelter assembly must include shelter.rating".format(invariant_id))
        return 1

    for process_id in ("process.build_shelter", "process.exposure_tick"):
        if process_id not in process_ids:
            print("{}: missing {}".format(invariant_id, process_id))
            return 1

    bundles = ((param_payload.get("record") or {}).get("bundles") or [])
    by_id = {}
    for row in bundles:
        if isinstance(row, dict):
            bundle_id = str(row.get("parameter_bundle_id", "")).strip()
            if bundle_id:
                by_id[bundle_id] = row

    for bundle_id in ("survival.params.default", "survival.params.harsh"):
        row = by_id.get(bundle_id)
        if not isinstance(row, dict):
            print("{}: missing bundle {}".format(invariant_id, bundle_id))
            return 1
        params = row.get("parameters") or {}
        multiplier = params.get("exposure.shelter_multiplier")
        if not isinstance(multiplier, (int, float)):
            print("{}: {} missing exposure.shelter_multiplier".format(invariant_id, bundle_id))
            return 1
        if multiplier >= 1.0:
            print("{}: {} shelter multiplier must be < 1.0".format(invariant_id, bundle_id))
            return 1

    print("shelter exposure reduction invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
