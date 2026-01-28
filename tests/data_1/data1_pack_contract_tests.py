import argparse
import json
import os
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

EXPECTED_PROVIDES = {
    "org.dominium.core.materials.extended": [
        "org.dominium.core.materials",
        "org.dominium.core.materials.extended",
    ],
    "org.dominium.core.parts.extended": [
        "org.dominium.core.interfaces",
        "org.dominium.core.interfaces.extended",
        "org.dominium.core.parts",
        "org.dominium.core.parts.extended",
    ],
    "org.dominium.core.assemblies.extended": [
        "org.dominium.core.assemblies.extended",
    ],
    "org.dominium.core.processes.extended": [
        "org.dominium.core.processes",
        "org.dominium.core.processes.extended",
    ],
    "org.dominium.core.quality.extended": [
        "org.dominium.core.quality.extended",
    ],
    "org.dominium.core.standards.extended": [
        "org.dominium.core.standards",
        "org.dominium.core.standards.extended",
    ],
    "org.dominium.core.instruments.extended": [
        "org.dominium.core.instruments.extended",
    ],
    "org.dominium.core.hazards.extended": [
        "org.dominium.core.hazards.extended",
    ],
}

EXPECTED_DEPENDS = {
    "org.dominium.core.parts.extended": [
        "org.dominium.core.materials.extended",
    ],
    "org.dominium.core.assemblies.extended": [
        "org.dominium.core.interfaces.extended",
        "org.dominium.core.parts.extended",
        "org.dominium.core.processes.extended",
    ],
    "org.dominium.core.processes.extended": [
        "org.dominium.core.instruments.extended",
        "org.dominium.core.standards.extended",
    ],
    "org.dominium.core.quality.extended": [
        "org.dominium.core.processes.extended",
        "org.dominium.core.standards.extended",
    ],
    "org.dominium.core.instruments.extended": [
        "org.dominium.core.standards.extended",
    ],
}

MATURITY_LABELS = {"PARAMETRIC", "STRUCTURAL", "BOUNDED", "INCOMPLETE"}


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


def extract_depends(record):
    deps = extract_capabilities(record.get("depends") or record.get("dependencies"))
    return sorted(set(deps))


def validate_readme(readme_path):
    text = read_text(readme_path)
    for line in text.splitlines():
        if line.strip().startswith("Maturity:"):
            label = line.split(":", 1)[1].strip()
            return label in MATURITY_LABELS
    return False


def main():
    parser = argparse.ArgumentParser(description="DATA-1 pack contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

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

        expected_caps = sorted(EXPECTED_PROVIDES.get(pack_id, []))
        provides = sorted(set(extract_capabilities(record.get("provides"))))
        if provides != expected_caps:
            print("provides mismatch for {}".format(pack_id))
            return 1

        expected_depends = sorted(EXPECTED_DEPENDS.get(pack_id, []))
        depends = extract_depends(record)
        if depends != expected_depends:
            print("depends mismatch for {}".format(pack_id))
            return 1

        docs_readme = os.path.join(pack_dir, "docs", "README.md")
        if not os.path.isfile(docs_readme):
            print("missing pack docs README for {}".format(pack_id))
            return 1
        if not validate_readme(docs_readme):
            print("README missing maturity label for {}".format(pack_id))
            return 1

        data_dir = os.path.join(pack_dir, "data")
        if not os.path.isdir(data_dir):
            print("missing data dir for {}".format(pack_id))
            return 1
        if not os.path.isfile(os.path.join(data_dir, "fab_pack.json")):
            print("missing fab_pack.json for {}".format(pack_id))
            return 1

    print("DATA-1 pack contracts OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
