import argparse
import json
import os

from distribution_lib import (
    extract_record,
    is_reverse_dns,
    make_refusal,
    REFUSAL_INVALID,
)


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def read_profile(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def extract_pack_ids(recommended):
    pack_ids = []
    for entry in normalize_list(recommended):
        if isinstance(entry, dict):
            pack_id = entry.get("pack_id")
        else:
            pack_id = entry
        if isinstance(pack_id, str):
            pack_ids.append(pack_id)
    return sorted(set(pack_ids))


def extract_template_ids(templates):
    ids = []
    for entry in normalize_list(templates):
        if isinstance(entry, dict):
            tid = entry.get("template_id")
        else:
            tid = entry
        if isinstance(tid, str):
            ids.append(tid)
    return sorted(set(ids))


def main():
    parser = argparse.ArgumentParser(description="Inspect profile data.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    data = read_profile(args.input)
    record = extract_record(data)
    profile_id = record.get("profile_id")
    if not is_reverse_dns(profile_id):
        payload = {
            "ok": False,
            "refusal": make_refusal(*REFUSAL_INVALID, "invalid profile id", {"profile_id": profile_id}),
        }
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 2

    recommended_packs = extract_pack_ids(record.get("recommended_packs"))
    templates = extract_template_ids(record.get("default_world_templates"))

    payload = {
        "ok": True,
        "profile_id": profile_id,
        "recommended_packs": recommended_packs,
        "default_world_templates": templates,
    }

    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("profile_inspect: {}".format(profile_id))
    for pack_id in recommended_packs:
        print("recommended: {}".format(pack_id))
    for template_id in templates:
        print("template: {}".format(template_id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
