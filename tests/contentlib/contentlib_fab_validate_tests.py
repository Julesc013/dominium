import argparse
import json
import os
import subprocess
import sys


PACKS = [
    "org.dominium.core.units",
    "org.dominium.core.interfaces",
    "org.dominium.core.materials.basic",
    "org.dominium.core.parts.basic",
    "org.dominium.core.processes.basic",
    "org.dominium.core.standards.basic",
    "org.dominium.worldgen.minimal",
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


def main():
    parser = argparse.ArgumentParser(description="CONTENTLIB FAB validation tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    # Map capability -> pack providers (within this pack set).
    capability_providers = {}
    manifests = {pack_id: load_pack_manifest(repo_root, pack_id) for pack_id in PACKS}
    for pack_id, record in manifests.items():
        for cap_id in extract_capabilities(record.get("provides")):
            capability_providers.setdefault(cap_id, []).append(pack_id)

    for pack_id in PACKS:
        record = manifests.get(pack_id, {})
        depends = extract_capabilities(record.get("depends") or record.get("dependencies"))
        include_packs = [pack_id]
        for dep in depends:
            include_packs.extend(capability_providers.get(dep, []))

        pack_paths = []
        for pid in sorted(set(include_packs)):
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

    print("CONTENTLIB FAB validation OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
