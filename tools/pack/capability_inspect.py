import argparse
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "distribution")))

from distribution_lib import (  # noqa: E402
    discover_pack_manifests,
    extract_record,
    load_json,
)


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def extract_capabilities(entries):
    out = []
    for entry in normalize_list(entries):
        if isinstance(entry, dict):
            cap_id = entry.get("capability_id")
        else:
            cap_id = entry
        if isinstance(cap_id, str):
            out.append(cap_id)
    return out


def load_manifest(path):
    payload = load_json(path)
    return extract_record(payload)


def load_baseline(path):
    payload = load_json(path)
    record = extract_record(payload)
    required = extract_capabilities(record.get("required_capabilities"))
    optional = extract_capabilities(record.get("optional_capabilities"))
    return {
        "baseline_id": record.get("baseline_id"),
        "baseline_version": record.get("baseline_version"),
        "required": sorted(set(required)),
        "optional": sorted(set(optional)),
    }


def build_provider_map(packs):
    providers = {}
    for pack in packs:
        for cap_id in pack.get("provides") or []:
            providers.setdefault(cap_id, []).append(pack.get("pack_id"))
    for cap_id in providers:
        providers[cap_id] = sorted(set(providers[cap_id]))
    return providers


def selection_from_ids(all_packs, ids):
    pack_map = {pack.get("pack_id"): pack for pack in all_packs}
    selected = []
    missing = []
    for pack_id in ids:
        pack = pack_map.get(pack_id)
        if pack:
            selected.append(pack)
        else:
            missing.append(pack_id)
    return selected, sorted(missing)


def selection_from_roots(roots):
    selected = []
    for root in roots:
        manifest = os.path.join(root, "pack_manifest.json")
        if os.path.isfile(manifest):
            record = load_manifest(manifest)
            if record.get("pack_id"):
                selected.append({
                    "pack_id": record.get("pack_id"),
                    "pack_version": record.get("pack_version"),
                    "provides": extract_capabilities(record.get("provides")),
                    "depends": extract_capabilities(record.get("depends") or record.get("dependencies")),
                    "root": os.path.abspath(root),
                    "manifest_relpath": "pack_manifest.json",
                })
    return selected


def compute_transitive(pack_list, provider_map):
    required_caps = sorted(set(cap for pack in pack_list for cap in pack.get("depends") or []))
    closure_caps = set(required_caps)
    closure_packs = set(pack.get("pack_id") for pack in pack_list)
    queue = list(required_caps)
    while queue:
        cap_id = queue.pop(0)
        for provider in provider_map.get(cap_id, []):
            if provider not in closure_packs:
                closure_packs.add(provider)
            # pull dependencies from provider if available in selection
            for pack in pack_list:
                if pack.get("pack_id") == provider:
                    for dep in pack.get("depends") or []:
                        if dep not in closure_caps:
                            closure_caps.add(dep)
                            queue.append(dep)
    return sorted(closure_caps), sorted(closure_packs)


def main():
    parser = argparse.ArgumentParser(description="Inspect pack capabilities and dependencies.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--pack-id", action="append", default=[])
    parser.add_argument("--pack-root", action="append", default=[])
    parser.add_argument("--baseline", default=None)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    all_packs = discover_pack_manifests(["data/packs", "data/worldgen"], repo_root)
    provider_map = build_provider_map(all_packs)

    selected = []
    missing = []
    if args.pack_id:
        selected, missing = selection_from_ids(all_packs, args.pack_id)
    if args.pack_root:
        selected.extend(selection_from_roots(args.pack_root))

    if not selected:
        selected = all_packs

    for pack in selected:
        depends = extract_capabilities(pack.get("depends") or pack.get("dependencies"))
        pack["depends"] = sorted(set(depends))
        pack["provides"] = sorted(set(pack.get("provides") or []))

    provided = sorted(set(cap for pack in selected for cap in pack.get("provides") or []))
    required = sorted(set(cap for pack in selected for cap in pack.get("depends") or []))
    closure_caps, closure_packs = compute_transitive(selected, provider_map)

    overlaps = {}
    conflicts = {}
    for cap_id, providers in provider_map.items():
        if len(providers) > 1:
            overlaps[cap_id] = providers
    for cap_id in provided:
        providers = [pack.get("pack_id") for pack in selected if cap_id in (pack.get("provides") or [])]
        providers = sorted(set([p for p in providers if p]))
        if len(providers) > 1:
            conflicts[cap_id] = providers

    baseline = None
    baseline_status = None
    if args.baseline:
        baseline = load_baseline(args.baseline)
        missing_required = [cap for cap in baseline["required"] if cap not in provided]
        baseline_status = {
            "baseline_id": baseline["baseline_id"],
            "baseline_version": baseline["baseline_version"],
            "missing_required": missing_required,
            "missing_optional": [cap for cap in baseline["optional"] if cap not in provided],
        }

    output = {
        "ok": True,
        "selection": {
            "pack_count": len(selected),
            "packs": sorted([pack.get("pack_id") for pack in selected]),
            "missing_packs": missing,
            "provides": provided,
            "requires": required,
        },
        "transitive": {
            "required_capabilities": closure_caps,
            "closure_packs": closure_packs,
        },
        "overlaps": overlaps,
        "conflicts": conflicts,
        "baseline": baseline_status,
    }

    if args.format == "json":
        print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("capability_inspect: packs={}".format(len(selected)))
    print("provides={}".format(len(provided)))
    print("requires={}".format(len(required)))
    if conflicts:
        print("conflicts={}".format(len(conflicts)))
    else:
        print("conflicts=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
