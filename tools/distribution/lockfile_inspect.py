import argparse
import json
import os

from distribution_lib import extract_record, make_refusal, REFUSAL_INVALID


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def sorted_resolutions(resolutions):
    out = []
    for entry in normalize_list(resolutions):
        if not isinstance(entry, dict):
            continue
        out.append(entry)
    out.sort(key=lambda item: (item.get("capability_id", ""), item.get("provider_pack_id", "")))
    return out


def sorted_pack_refs(pack_refs):
    out = []
    for entry in normalize_list(pack_refs):
        if isinstance(entry, dict):
            pack_id = entry.get("pack_id")
        else:
            pack_id = None
        if pack_id:
            out.append({"pack_id": pack_id, "version_constraint": entry.get("version_constraint") if isinstance(entry, dict) else None})
    out.sort(key=lambda item: (item.get("pack_id", ""), item.get("version_constraint") or ""))
    return out


def main():
    parser = argparse.ArgumentParser(description="Inspect capability lockfiles.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    record = extract_record(payload)
    lock_id = record.get("lock_id")
    lock_version = record.get("lock_format_version")
    resolutions = sorted_resolutions(record.get("resolutions"))
    pack_refs = sorted_pack_refs(record.get("pack_refs"))

    if not lock_id or lock_version is None:
        payload = {
            "ok": False,
            "refusal": make_refusal(*REFUSAL_INVALID, "invalid lockfile", {"lock_id": lock_id}),
        }
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 2

    output = {
        "ok": True,
        "lock_id": lock_id,
        "lock_format_version": lock_version,
        "resolutions": resolutions,
        "pack_refs": pack_refs,
    }

    if args.format == "json":
        print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("lockfile_inspect: {}".format(lock_id))
    print("resolutions={}".format(len(resolutions)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
