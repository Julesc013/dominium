import argparse
import json
import os
import subprocess
import sys


PACKS = [
    "org.dominium.core.materials.extended",
    "org.dominium.core.parts.extended",
    "org.dominium.core.assemblies.extended",
    "org.dominium.core.processes.extended",
    "org.dominium.core.quality.extended",
    "org.dominium.core.standards.extended",
    "org.dominium.core.instruments.extended",
    "org.dominium.core.hazards.extended",
]

FAB_KEYS = [
    "materials",
    "interfaces",
    "parts",
    "assemblies",
    "process_families",
    "instruments",
    "standards",
    "qualities",
    "batches",
    "hazards",
    "substances",
]


def run_validate(repo_root, input_path):
    script = os.path.join(repo_root, "tools", "fab", "fab_validate.py")
    cmd = [sys.executable, script, "--input", input_path, "--repo-root", repo_root, "--format", "json"]
    result = subprocess.run(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return json.loads(result.stdout.decode("utf-8"))


def load_pack_manifest(repo_root, pack_id):
    path = os.path.join(repo_root, "data", "packs", pack_id, "pack_manifest.json")
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data.get("record", data)


def extract_capabilities(entries):
    out = []
    for entry in entries or []:
        if isinstance(entry, dict):
            cap_id = entry.get("capability_id")
        else:
            cap_id = entry
        if isinstance(cap_id, str):
            out.append(cap_id)
    return out


def merge_fab_packs(pack_paths):
    merged = {key: [] for key in FAB_KEYS}
    for path in pack_paths:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        for key in FAB_KEYS:
            merged[key].extend(data.get(key) or [])
    return merged


def write_temp_json(payload):
    import tempfile
    handle = tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8")
    json.dump(payload, handle, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    handle.close()
    return handle.name


def build_provider_map(manifests):
    providers = {}
    for pack_id, record in manifests.items():
        for cap_id in extract_capabilities(record.get("provides")):
            providers.setdefault(cap_id, []).append(pack_id)
    for cap_id in providers:
        providers[cap_id] = sorted(set(providers[cap_id]))
    return providers


def extract_depends(record):
    return sorted(set(extract_capabilities(record.get("depends") or record.get("dependencies"))))


def resolve_dependency_closure(pack_id, manifests, providers):
    include = set()
    queue = [pack_id]
    while queue:
        current = queue.pop(0)
        if current in include:
            continue
        include.add(current)
        record = manifests.get(current, {})
        for cap_id in extract_depends(record):
            for provider in providers.get(cap_id, []):
                if provider not in include:
                    queue.append(provider)
    return sorted(include)


def main():
    parser = argparse.ArgumentParser(description="DATA-1 FAB validation tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    manifests = {pack_id: load_pack_manifest(repo_root, pack_id) for pack_id in PACKS}
    providers = build_provider_map(manifests)

    for pack_id in PACKS:
        include_packs = resolve_dependency_closure(pack_id, manifests, providers)
        pack_paths = []
        for pid in include_packs:
            fab_path = os.path.join(repo_root, "data", "packs", pid, "data", "fab_pack.json")
            if not os.path.isfile(fab_path):
                print("missing fab_pack.json for {}".format(pid))
                return 1
            pack_paths.append(fab_path)

        merged = merge_fab_packs(pack_paths)
        temp_path = write_temp_json(merged)
        output = run_validate(repo_root, temp_path)
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        if not output.get("ok"):
            print("fab_validate failed for {}".format(pack_id))
            return 1

        # Determinism check: reverse order merge yields same validation result.
        merged_rev = merge_fab_packs(list(reversed(pack_paths)))
        temp_path_rev = write_temp_json(merged_rev)
        output_rev = run_validate(repo_root, temp_path_rev)
        try:
            os.unlink(temp_path_rev)
        except OSError:
            pass
        if output_rev.get("ok") != output.get("ok"):
            print("fab_validate nondeterministic for {}".format(pack_id))
            return 1

    print("DATA-1 FAB validation OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
