import argparse
import json
import os
import sys

from invariant_utils import is_override_active


LAW_REL = os.path.join("data", "registries", "law_profiles.json")
MATRIX_REL = os.path.join("data", "registries", "presentation_matrix.json")
BRIDGE_REL = os.path.join("client", "core", "client_command_bridge.c")


def _load_json(path: str):
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


def _find_law(payload: dict, law_id: str):
    rows = ((payload.get("record") or {}).get("profiles") or [])
    for row in rows:
        if isinstance(row, dict) and str(row.get("law_profile_id", "")).strip() == law_id:
            return row
    return None


def _find_matrix_row(payload: dict, law_id: str):
    rows = ((payload.get("record") or {}).get("rows") or [])
    for row in rows:
        if isinstance(row, dict) and str(row.get("law_profile_id", "")).strip() == law_id:
            return row
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: observer profile always requires watermark.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-PRESENTATION-MATRIX-INTEGRITY"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    law_path = os.path.join(repo_root, LAW_REL)
    matrix_path = os.path.join(repo_root, MATRIX_REL)
    bridge_path = os.path.join(repo_root, BRIDGE_REL)
    for rel, path in ((LAW_REL, law_path), (MATRIX_REL, matrix_path), (BRIDGE_REL, bridge_path)):
        if not os.path.isfile(path):
            print("{}: missing {}".format(invariant_id, rel.replace("\\", "/")))
            return 1

    law_payload = _load_json(law_path)
    matrix_payload = _load_json(matrix_path)
    if not isinstance(law_payload, dict):
        print("{}: invalid json {}".format(invariant_id, LAW_REL.replace("\\", "/")))
        return 1
    if not isinstance(matrix_payload, dict):
        print("{}: invalid json {}".format(invariant_id, MATRIX_REL.replace("\\", "/")))
        return 1

    observer_law = _find_law(law_payload, "law.observer.default")
    if not isinstance(observer_law, dict):
        print("{}: missing law.observer.default".format(invariant_id))
        return 1
    if str(observer_law.get("watermark_policy", "")).strip() != "observer":
        print("{}: law.observer.default must use watermark_policy=observer".format(invariant_id))
        return 1

    matrix_row = _find_matrix_row(matrix_payload, "law.observer.default")
    if not isinstance(matrix_row, dict):
        print("{}: presentation matrix missing law.observer.default row".format(invariant_id))
        return 1
    if matrix_row.get("watermark_required") is not True:
        print("{}: observer matrix row must set watermark_required=true".format(invariant_id))
        return 1

    bridge_text = _read(bridge_path)
    for marker in (
        "{ \"exp.observer\", \"law.observer.default\", 1, 1, 1, 0, 1, 1 }",
        "g_selection.watermark_observer ? \"OBSERVER MODE\" : \"none\"",
    ):
        if marker not in bridge_text:
            print("{}: missing marker '{}' in {}".format(invariant_id, marker, BRIDGE_REL.replace("\\", "/")))
            return 1

    print("observer watermark invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
