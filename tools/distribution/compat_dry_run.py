import argparse
import json
import os

from distribution_lib import (
    discover_pack_manifests,
    extract_record,
    is_reverse_dns,
    make_refusal,
    REFUSAL_CAPABILITY,
    REFUSAL_INTEGRITY,
    REFUSAL_INVALID,
)


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def extract_pack_ids(recommended):
    ids = []
    for entry in normalize_list(recommended):
        if isinstance(entry, dict):
            pack_id = entry.get("pack_id")
        else:
            pack_id = entry
        if isinstance(pack_id, str):
            ids.append(pack_id)
    return sorted(set(ids))


def extract_capabilities(packs):
    cap_map = {}
    for pack in packs:
        pack_id = pack.get("pack_id")
        for cap_id in pack.get("provides", []):
            cap_map.setdefault(cap_id, []).append(pack_id)
    for cap_id in cap_map:
        cap_map[cap_id] = sorted(set(cap_map[cap_id]))
    return cap_map


def check_lockfile(lockfile, pack_ids):
    record = extract_record(lockfile)
    missing = []
    resolutions = normalize_list(record.get("resolutions"))
    for entry in resolutions:
        if not isinstance(entry, dict):
            continue
        provider = entry.get("provider_pack_id")
        if isinstance(provider, str) and provider not in pack_ids:
            missing.append(provider)
    return sorted(set(missing))


def main():
    parser = argparse.ArgumentParser(description="Dry-run compatibility check for packs and lockfiles.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--root", action="append", default=[])
    parser.add_argument("--require-capability", action="append", default=[])
    parser.add_argument("--lockfile")
    parser.add_argument("--profile")
    parser.add_argument("--engine-pack-format", type=int, default=0)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    roots = args.root if args.root else ["data/packs"]
    packs = discover_pack_manifests(roots, repo_root)

    incompatible = []
    if args.engine_pack_format > 0:
        for pack in packs:
            fmt = pack.get("pack_format_version")
            if isinstance(fmt, int) and fmt > args.engine_pack_format:
                incompatible.append(pack.get("pack_id"))
    incompatible = sorted(set([p for p in incompatible if p]))

    pack_ids = sorted(set([p.get("pack_id") for p in packs if p.get("pack_id")]))
    cap_map = extract_capabilities(packs)
    required_caps = sorted(set([cap for cap in args.require_capability if isinstance(cap, str)]))
    missing_caps = [cap for cap in required_caps if cap not in cap_map]

    missing_packs = []
    if args.lockfile:
        lockfile = load_json(args.lockfile)
        missing_packs = check_lockfile(lockfile, pack_ids)

    recommended_present = []
    recommended_missing = []
    if args.profile:
        profile = load_json(args.profile)
        record = extract_record(profile)
        profile_id = record.get("profile_id")
        if not is_reverse_dns(profile_id):
            payload = {
                "ok": False,
                "refusal": make_refusal(*REFUSAL_INVALID, "invalid profile id", {"profile_id": profile_id}),
            }
            print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
            return 2
        recommended = extract_pack_ids(record.get("recommended_packs"))
        for pack_id in recommended:
            if pack_id in pack_ids:
                recommended_present.append(pack_id)
            else:
                recommended_missing.append(pack_id)

    ok = not missing_caps and not missing_packs and not incompatible
    refusal = None
    if incompatible:
        refusal = make_refusal(*REFUSAL_INTEGRITY, "unsupported pack format",
                               {"incompatible_packs": incompatible})
    elif missing_caps or missing_packs:
        refusal = make_refusal(*REFUSAL_CAPABILITY, "missing required capabilities",
                               {"missing_capabilities": missing_caps, "missing_packs": missing_packs})

    output = {
        "ok": ok,
        "required_capabilities": required_caps,
        "missing_capabilities": missing_caps,
        "missing_packs": missing_packs,
        "incompatible_packs": incompatible,
        "recommended_packs_present": recommended_present,
        "recommended_packs_missing": recommended_missing,
        "refusal": refusal,
    }

    if args.format == "json":
        print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0 if ok else 2

    if ok:
        print("compat_dry_run: ok")
        return 0
    print("compat_dry_run: failed")
    if refusal:
        print("refusal {}".format(refusal.get("code")))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
