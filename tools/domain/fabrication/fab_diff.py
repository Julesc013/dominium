import argparse
import json
import os

from fab_lib import load_json


ID_KEYS = {
    "materials": "material_id",
    "interfaces": "interface_id",
    "parts": "part_id",
    "assemblies": "assembly_id",
    "process_families": "process_family_id",
    "instruments": "instrument_id",
    "standards": "standard_id",
    "qualities": "quality_id",
    "batches": "batch_id",
    "hazards": "hazard_id",
    "substances": "substance_id",
}


def resolve_fab_path(path):
    if os.path.isdir(path):
        candidate = os.path.join(path, "data", "fab_pack.json")
        if os.path.isfile(candidate):
            return candidate, path
    return path, detect_pack_root(path)


def detect_pack_root(input_path):
    if not isinstance(input_path, str):
        return None
    norm = input_path.replace("\\", "/")
    if norm.endswith("/data/fab_pack.json"):
        return os.path.dirname(os.path.dirname(input_path))
    return None


def parse_maturity(pack_root):
    if not pack_root:
        return None
    readme = os.path.join(pack_root, "docs", "README.md")
    if not os.path.isfile(readme):
        return None
    with open(readme, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    for raw in text.splitlines():
        line = raw.strip()
        if line.lower().startswith("maturity:"):
            value = line.split(":", 1)[1].strip().rstrip(".")
            return value.upper()
    return None


def index_by_id(entries, key):
    out = {}
    if isinstance(entries, list):
        for entry in entries:
            if isinstance(entry, dict):
                rec_id = entry.get(key)
                if isinstance(rec_id, str):
                    out[rec_id] = entry
    return out


def stable_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def diff_section(left_list, right_list, key):
    left_map = index_by_id(left_list, key)
    right_map = index_by_id(right_list, key)
    left_ids = set(left_map.keys())
    right_ids = set(right_map.keys())
    added = sorted(right_ids - left_ids)
    removed = sorted(left_ids - right_ids)
    changed = []
    for rec_id in sorted(left_ids & right_ids):
        if stable_json(left_map[rec_id]) != stable_json(right_map[rec_id]):
            changed.append(rec_id)
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": sorted(left_ids & right_ids - set(changed)),
    }


def compatibility_impact(diff):
    if diff["removed"]:
        return "breaking"
    if diff["changed"]:
        return "potentially_breaking"
    if diff["added"]:
        return "additive"
    return "none"


def main():
    parser = argparse.ArgumentParser(description="Diff two FAB packs.")
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    left_path, left_root = resolve_fab_path(args.left)
    right_path, right_root = resolve_fab_path(args.right)

    left = load_json(left_path)
    right = load_json(right_path)

    diffs = {}
    summary = {"breaking": False, "potentially_breaking": False, "additive": False}
    for section, key in ID_KEYS.items():
        diff = diff_section(left.get(section) or [], right.get(section) or [], key)
        diffs[section] = diff
        impact = compatibility_impact(diff)
        if impact == "breaking":
            summary["breaking"] = True
        elif impact == "potentially_breaking":
            summary["potentially_breaking"] = True
        elif impact == "additive":
            summary["additive"] = True

    impact = "none"
    if summary["breaking"]:
        impact = "breaking"
    elif summary["potentially_breaking"]:
        impact = "potentially_breaking"
    elif summary["additive"]:
        impact = "additive"

    maturity = {
        "left": parse_maturity(left_root),
        "right": parse_maturity(right_root),
    }
    maturity["changed"] = maturity["left"] != maturity["right"]

    payload = {
        "ok": True,
        "left": {"path": left_path, "pack_root": left_root},
        "right": {"path": right_path, "pack_root": right_root},
        "impact": impact,
        "maturity": maturity,
        "diffs": diffs,
    }

    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("fab_diff: impact={}".format(impact))
    for section, diff in diffs.items():
        print("{} +{} -{} ~{}".format(section, len(diff["added"]), len(diff["removed"]), len(diff["changed"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
