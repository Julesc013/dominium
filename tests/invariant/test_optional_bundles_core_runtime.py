import argparse
import json
import os
import sys

from invariant_utils import is_override_active


BUNDLE_REL = os.path.join("data", "registries", "bundle_profiles.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: core runtime bundle remains required; defaults stay optional.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-DEFAULTS-OPTIONAL"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    path = os.path.join(repo_root, BUNDLE_REL)
    if not os.path.isfile(path):
        print("{}: missing {}".format(invariant_id, BUNDLE_REL.replace("\\", "/")))
        return 1

    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        print("{}: invalid json {}".format(invariant_id, BUNDLE_REL.replace("\\", "/")))
        return 1

    bundles = ((payload.get("record") or {}).get("bundles") or [])
    if not isinstance(bundles, list):
        print("{}: bundles must be list".format(invariant_id))
        return 1

    by_id = {}
    for row in bundles:
        if isinstance(row, dict):
            bundle_id = str(row.get("bundle_id", "")).strip()
            if bundle_id:
                by_id[bundle_id] = row

    core = by_id.get("bundle.core.runtime")
    compat_core = by_id.get("bundle.default_core")
    if core is None:
        print("{}: missing bundle.core.runtime".format(invariant_id))
        return 1
    if compat_core is None:
        print("{}: missing bundle.default_core".format(invariant_id))
        return 1

    core_optional = ((core.get("extensions") or {}).get("optional"))
    if core_optional is not False:
        print("{}: bundle.core.runtime must set extensions.optional=false".format(invariant_id))
        return 1
    if not (core.get("install_pack_ids") or []):
        print("{}: bundle.core.runtime must declare install_pack_ids".format(invariant_id))
        return 1

    compat_optional = ((compat_core.get("extensions") or {}).get("optional"))
    if compat_optional is not False:
        print("{}: bundle.default_core must set extensions.optional=false".format(invariant_id))
        return 1

    for bundle_id, row in sorted(by_id.items()):
        if bundle_id in {"bundle.core.runtime", "bundle.default_core"}:
            continue
        optional_flag = ((row.get("extensions") or {}).get("optional"))
        if optional_flag is not True:
            print("{}: {} must set extensions.optional=true".format(invariant_id, bundle_id))
            return 1

    print("optional-bundles invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
