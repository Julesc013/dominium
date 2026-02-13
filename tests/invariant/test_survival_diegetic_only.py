import argparse
import json
import os
import sys

from invariant_utils import is_override_active


LAW_REL = os.path.join("data", "registries", "law_profiles.json")
BRIDGE_REL = os.path.join("client", "core", "client_command_bridge.c")


def _load(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: survival law remains diegetic-only.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SURVIVAL-DIEGETIC-CONTRACT"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    law_path = os.path.join(repo_root, LAW_REL)
    bridge_path = os.path.join(repo_root, BRIDGE_REL)
    for rel, path in ((LAW_REL, law_path), (BRIDGE_REL, bridge_path)):
        if not os.path.isfile(path):
            print("{}: missing {}".format(invariant_id, rel.replace("\\", "/")))
            return 1

    payload = _load(law_path)
    if payload is None:
        print("{}: invalid json {}".format(invariant_id, LAW_REL.replace("\\", "/")))
        return 1

    profiles = ((payload.get("record") or {}).get("profiles") or [])
    by_id = {}
    for row in profiles:
        if isinstance(row, dict):
            law_id = str(row.get("law_profile_id", "")).strip()
            if law_id:
                by_id[law_id] = row

    survival_ids = ("law.survival.softcore", "law.survival.hardcore", "survival.softcore")
    forbidden_entitlements = {"ui.console.command.read_only", "ui.console.command.read_write", "camera.mode.observer_truth"}
    for law_id in survival_ids:
        row = by_id.get(law_id)
        if not isinstance(row, dict):
            print("{}: missing {}".format(invariant_id, law_id))
            return 1
        allowed = [str(item).strip() for item in (row.get("allowed_lenses") or [])]
        forbidden = [str(item).strip() for item in (row.get("forbidden_lenses") or [])]
        entitlements = {str(item).strip() for item in (row.get("entitlements_granted") or [])}
        if "lens.diegetic.*" not in allowed:
            print("{}: {} must allow lens.diegetic.*".format(invariant_id, law_id))
            return 1
        if not any(item.startswith("lens.nondiegetic") for item in forbidden):
            print("{}: {} must forbid nondiegetic lenses".format(invariant_id, law_id))
            return 1
        if forbidden_entitlements & entitlements:
            print("{}: {} grants forbidden entitlements {}".format(
                invariant_id,
                law_id,
                ",".join(sorted(forbidden_entitlements & entitlements)),
            ))
            return 1

    bridge_text = _read(bridge_path)
    for marker in (
        "{ \"exp.survival\", \"law.survival.softcore\", 1, 0, 0, 0, 0, 0 }",
        "{ \"exp.hardcore\", \"law.survival.hardcore\", 1, 0, 0, 0, 0, 0 }",
        "refuse.entitlement_required",
    ):
        if marker not in bridge_text:
            print("{}: missing marker {} in {}".format(invariant_id, marker, BRIDGE_REL.replace("\\", "/")))
            return 1

    print("survival diegetic-only invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
