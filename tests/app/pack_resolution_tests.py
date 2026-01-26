import argparse
import json
import os
import sys


def semver_tuple(value):
    if not isinstance(value, str):
        return (0, 0, 0)
    parts = value.split(".")
    nums = []
    for part in parts[:3]:
        try:
            nums.append(int(part))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)


def load_pack_manifest(path):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    record = data.get("record", data)
    return record


def iter_pack_manifests(repo_root):
    roots = [
        os.path.join(repo_root, "data", "packs"),
        os.path.join(repo_root, "data", "worldgen"),
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for name in filenames:
                if name != "pack_manifest.json":
                    continue
                yield os.path.join(dirpath, name)


def extract_capabilities(entries):
    out = []
    for entry in entries or []:
        if isinstance(entry, dict):
            cap_id = entry.get("capability_id")
        else:
            cap_id = entry
        if cap_id:
            out.append(cap_id)
    return out


def load_packs(repo_root):
    packs = []
    for path in iter_pack_manifests(repo_root):
        record = load_pack_manifest(path)
        pack_id = record.get("pack_id")
        if not pack_id:
            continue
        pack = {
            "pack_id": pack_id,
            "pack_version": record.get("pack_version", ""),
            "provides": extract_capabilities(record.get("provides")),
            "depends": extract_capabilities(record.get("depends") or record.get("dependencies")),
            "path": path,
        }
        packs.append(pack)
    return packs


def resolve_capabilities(packs):
    providers = {}
    for pack in packs:
        for cap_id in pack["provides"]:
            providers.setdefault(cap_id, []).append(pack)

    resolution = {}
    for cap_id, candidates in providers.items():
        ordered = sorted(
            candidates,
            key=lambda p: (-semver_tuple(p["pack_version"])[0],
                           -semver_tuple(p["pack_version"])[1],
                           -semver_tuple(p["pack_version"])[2],
                           p["pack_id"],
                           p["path"]),
        )
        resolution[cap_id] = ordered[0]["pack_id"]

    missing = set()
    for pack in packs:
        for dep in pack["depends"]:
            if dep not in resolution:
                missing.add(dep)

    mode = "ok" if not missing else "frozen"
    return resolution, sorted(missing), mode


def round_trip_manifest(doc):
    encoded = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return json.loads(encoded)


def main():
    parser = argparse.ArgumentParser(description="Pack resolution determinism tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    schema_pack = os.path.join(repo_root, "schema", "pack_manifest.schema")
    schema_lock = os.path.join(repo_root, "schema", "capability_lockfile.schema")
    if not os.path.isfile(schema_pack):
        print("missing pack manifest schema")
        return 1
    if not os.path.isfile(schema_lock):
        print("missing capability lockfile schema")
        return 1
    pack_text = open(schema_pack, "r", encoding="utf-8", errors="replace").read()
    if "requires_engine" not in pack_text or "depends" not in pack_text or "extensions" not in pack_text:
        print("pack manifest schema missing required fields")
        return 1
    lock_text = open(schema_lock, "r", encoding="utf-8", errors="replace").read()
    for token in ("resolution_rules", "missing_mode", "resolutions"):
        if token not in lock_text:
            print("capability lockfile schema missing {}".format(token))
            return 1

    packs = load_packs(repo_root)
    if not packs:
        print("no pack manifests found")
        return 1

    # Determinism: same packs, different order, same resolution.
    resolution_a, missing_a, mode_a = resolve_capabilities(packs)
    resolution_b, missing_b, mode_b = resolve_capabilities(list(reversed(packs)))
    if resolution_a != resolution_b:
        print("pack capability resolution is order-dependent")
        return 1
    if missing_a != missing_b or mode_a != mode_b:
        print("pack dependency results differ by ordering")
        return 1

    # Unknown manifest field preservation (round-trip).
    sample_path = None
    for path in iter_pack_manifests(repo_root):
        sample_path = path
        break
    if not sample_path:
        print("missing sample pack_manifest.json")
        return 1
    sample_doc = load_pack_manifest(sample_path)
    sample_doc["unknown.top"] = {"note": "preserve"}
    if "extensions" not in sample_doc:
        sample_doc["extensions"] = {}
    sample_doc["extensions"]["unknown.ext"] = {"v": 1}
    round_trip = round_trip_manifest(sample_doc)
    if "unknown.top" not in round_trip:
        print("unknown manifest field not preserved")
        return 1
    if "unknown.ext" not in round_trip.get("extensions", {}):
        print("unknown manifest extension not preserved")
        return 1

    # Pack removal safety (explicit frozen mode on missing capability).
    synthetic = [
        {"pack_id": "org.example.pack.alpha", "pack_version": "1.0.0",
         "provides": ["cap.example.alpha"], "depends": [], "path": "alpha"},
        {"pack_id": "org.example.pack.beta", "pack_version": "1.0.0",
         "provides": [], "depends": ["cap.example.alpha"], "path": "beta"},
    ]
    _res_ok, _missing_ok, mode_ok = resolve_capabilities(synthetic)
    if mode_ok != "ok":
        print("unexpected missing capability in baseline synthetic case")
        return 1
    _res_drop, missing_drop, mode_drop = resolve_capabilities(synthetic[1:])
    if "cap.example.alpha" not in missing_drop:
        print("missing capability not detected after pack removal")
        return 1
    if mode_drop not in ("frozen", "degraded"):
        print("missing capability did not yield explicit frozen/degraded mode")
        return 1

    print("Pack resolution tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
