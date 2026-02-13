import argparse
import hashlib
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


def _canonical_need_map(parameters: dict) -> str:
    payload = {
        key: parameters[key]
        for key in sorted(parameters.keys())
        if key.startswith("need.") or key in {"hunger.rate", "hydration.rate", "exposure.rate"}
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: survival need decay parameters are deterministic.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SURVIVAL-NEED-DECAY-DETERMINISTIC"
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

    process_rows = ((slice_payload.get("record") or {}).get("processes") or [])
    process_ids = {str(row.get("process_id", "")).strip() for row in process_rows if isinstance(row, dict)}
    if "process.need_tick" not in process_ids:
        print("{}: missing process.need_tick".format(invariant_id))
        return 1

    bundles = ((param_payload.get("record") or {}).get("bundles") or [])
    by_id = {}
    for row in bundles:
        if isinstance(row, dict):
            bundle_id = str(row.get("parameter_bundle_id", "")).strip()
            if bundle_id:
                by_id[bundle_id] = row

    required = ("survival.params.default", "survival.params.harsh")
    digests = []
    for bundle_id in required:
        row = by_id.get(bundle_id)
        if not isinstance(row, dict):
            print("{}: missing bundle {}".format(invariant_id, bundle_id))
            return 1
        parameters = row.get("parameters")
        if not isinstance(parameters, dict):
            print("{}: {} parameters must be object".format(invariant_id, bundle_id))
            return 1
        for key in ("need.energy.decay_rate", "need.hydration.decay_rate", "need.exposure.decay_rate"):
            value = parameters.get(key)
            if not isinstance(value, (int, float)) or value <= 0:
                print("{}: {} missing positive {}".format(invariant_id, bundle_id, key))
                return 1
        canonical = _canonical_need_map(parameters)
        digests.append(hashlib.sha256(canonical.encode("utf-8")).hexdigest())

    if len(set(digests)) != len(digests):
        print("{}: survival parameter bundles must not collapse to identical decay profiles".format(invariant_id))
        return 1

    print("survival need decay deterministic invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
