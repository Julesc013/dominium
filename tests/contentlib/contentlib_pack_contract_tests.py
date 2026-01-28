import argparse
import json
import os
import random
import re
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

EXPECTED_PROVIDES = {
    "org.dominium.core.units": "org.dominium.core.units",
    "org.dominium.core.interfaces": "org.dominium.core.interfaces",
    "org.dominium.core.materials.basic": "org.dominium.core.materials",
    "org.dominium.core.parts.basic": "org.dominium.core.parts",
    "org.dominium.core.processes.basic": "org.dominium.core.processes",
    "org.dominium.core.standards.basic": "org.dominium.core.standards",
    "org.dominium.worldgen.minimal": "org.dominium.worldgen.minimal",
}

EXPECTED_DEPENDS = {
    "org.dominium.core.parts.basic": [
        "org.dominium.core.interfaces",
        "org.dominium.core.materials",
    ],
}


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_pack_toml_value(text, key):
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith(key):
            continue
        if "=" not in line:
            continue
        _left, right = line.split("=", 1)
        value = right.strip()
        if value.startswith("\"") and value.endswith("\""):
            return value[1:-1]
    return None


def load_pack_manifest(path):
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


def build_provider_map(pack_records):
    providers = {}
    for record in pack_records:
        pack_id = record.get("pack_id")
        for cap_id in extract_capabilities(record.get("provides")):
            providers.setdefault(cap_id, []).append(pack_id)
    return providers


def find_missing_dependencies(pack_records):
    providers = build_provider_map(pack_records)
    missing = {}
    for record in pack_records:
        pack_id = record.get("pack_id")
        deps = extract_capabilities(record.get("depends") or record.get("dependencies"))
        for cap_id in deps:
            if cap_id not in providers:
                missing.setdefault(pack_id, []).append(cap_id)
    return missing


def deterministic_resolution(pack_records):
    providers = build_provider_map(pack_records)
    resolution = {}
    for cap_id, pack_ids in providers.items():
        resolution[cap_id] = sorted(pack_ids)[0]
    return resolution


def main():
    parser = argparse.ArgumentParser(description="CONTENTLIB pack contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    pack_records = []
    for pack_id in PACKS:
        pack_dir = os.path.join(repo_root, "data", "packs", pack_id)
        if not os.path.isdir(pack_dir):
            print("missing pack dir: {}".format(pack_id))
            return 1

        pack_toml = os.path.join(pack_dir, "pack.toml")
        if not os.path.isfile(pack_toml):
            print("missing pack.toml: {}".format(pack_id))
            return 1

        pack_toml_text = read_text(pack_toml)
        toml_pack_id = parse_pack_toml_value(pack_toml_text, "pack_id")
        if toml_pack_id != pack_id:
            print("pack.toml pack_id mismatch for {}".format(pack_id))
            return 1
        if not parse_pack_toml_value(pack_toml_text, "pack_version"):
            print("pack.toml missing pack_version for {}".format(pack_id))
            return 1

        pack_manifest = os.path.join(pack_dir, "pack_manifest.json")
        if not os.path.isfile(pack_manifest):
            print("missing pack_manifest.json: {}".format(pack_id))
            return 1
        record = load_pack_manifest(pack_manifest)
        if record.get("pack_id") != pack_id:
            print("pack_manifest pack_id mismatch for {}".format(pack_id))
            return 1
        expected_cap = EXPECTED_PROVIDES.get(pack_id)
        provides = extract_capabilities(record.get("provides"))
        if expected_cap not in provides:
            print("pack_manifest missing capability for {}".format(pack_id))
            return 1

        docs_readme = os.path.join(pack_dir, "docs", "README.md")
        if not os.path.isfile(docs_readme):
            print("missing pack docs README for {}".format(pack_id))
            return 1

        data_dir = os.path.join(pack_dir, "data")
        if not os.path.isdir(data_dir):
            print("missing data dir for {}".format(pack_id))
            return 1

        pack_records.append(record)

        expected_depends = EXPECTED_DEPENDS.get(pack_id, [])
        depends = sorted(set(extract_capabilities(record.get("depends") or record.get("dependencies"))))
        if depends != sorted(expected_depends):
            print("depends mismatch for {}".format(pack_id))
            return 1

    # Cross-pack references: parts -> materials/interfaces
    materials_path = os.path.join(repo_root, "data", "packs", "org.dominium.core.materials.basic", "data", "fab_pack.json")
    interfaces_path = os.path.join(repo_root, "data", "packs", "org.dominium.core.interfaces", "data", "fab_pack.json")
    parts_path = os.path.join(repo_root, "data", "packs", "org.dominium.core.parts.basic", "data", "fab_pack.json")
    materials = json.load(open(materials_path, "r", encoding="utf-8")).get("materials", [])
    interfaces = json.load(open(interfaces_path, "r", encoding="utf-8")).get("interfaces", [])
    parts = json.load(open(parts_path, "r", encoding="utf-8")).get("parts", [])

    material_ids = {m.get("material_id") for m in materials if isinstance(m, dict)}
    interface_ids = {i.get("interface_id") for i in interfaces if isinstance(i, dict)}
    for part in parts:
        if not isinstance(part, dict):
            continue
        mat_id = (part.get("material_ref") or {}).get("material_id")
        if mat_id not in material_ids:
            print("part references unknown material: {}".format(mat_id))
            return 1
        for iface_ref in part.get("interfaces") or []:
            iface_id = iface_ref.get("interface_id") if isinstance(iface_ref, dict) else None
            if iface_id not in interface_ids:
                print("part references unknown interface: {}".format(iface_id))
                return 1

    # Deterministic capability resolution across orderings.
    canonical = deterministic_resolution(pack_records)
    rng = random.Random(42)
    shuffled = list(pack_records)
    rng.shuffle(shuffled)
    if canonical != deterministic_resolution(shuffled):
        print("capability resolution is order-dependent")
        return 1

    # Pack removal safety: removing materials/interfaces yields explicit missing dependencies for parts.
    subset = [record for record in pack_records if record.get("pack_id") not in (
        "org.dominium.core.materials.basic",
        "org.dominium.core.interfaces",
    )]
    missing = find_missing_dependencies(subset)
    missing_parts = missing.get("org.dominium.core.parts.basic", [])
    if "org.dominium.core.materials" not in missing_parts or "org.dominium.core.interfaces" not in missing_parts:
        print("missing dependency not detected for parts pack")
        return 1

    print("CONTENTLIB pack contracts OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
