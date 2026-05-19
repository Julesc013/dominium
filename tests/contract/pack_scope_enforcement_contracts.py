import argparse
import os
import sys


ALLOWED_DIRS = {
    "data",
    "assets",
    "content",
    "schema",
    "scenarios",
    "ui",
    "docs",
}

ALLOWED_FILES = {
    "pack.json",
    "pack.toml",
    "pack.manifest",
    "pack_manifest.json",
    "pack.capabilities.json",
    "pack.compat.json",
    "pack.trust.json",
    "README.md",
    "README.txt",
    "LICENSE",
    "LICENSE.md",
    "CHANGELOG.md",
    ".keep",
}

PACK_CATEGORIES = {
    "blueprint",
    "core",
    "derived",
    "domain",
    "example",
    "experience",
    "law",
    "official",
    "reality",
    "representation",
    "spec",
    "tool",
    "worldgen",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Contract: pack scope enforcement.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    packs_root = os.path.join(repo_root, "content", "packs")

    invariant_id = "INV-PACK-SCOPE"
    if not os.path.isdir(packs_root):
        print("{}: missing content/packs directory".format(invariant_id))
        return 1

    violations = []
    for category in sorted(os.listdir(packs_root)):
        category_path = os.path.join(packs_root, category)
        if not os.path.isdir(category_path):
            continue
        if category not in PACK_CATEGORIES:
            violations.append("{}: unknown pack category".format(category))
            continue
        for pack_name in sorted(os.listdir(category_path)):
            pack_path = os.path.join(category_path, pack_name)
            if not os.path.isdir(pack_path):
                continue
            pack_toml = os.path.join(pack_path, "pack.toml")
            pack_manifest = os.path.join(pack_path, "pack.manifest")
            pack_json = os.path.join(pack_path, "pack.json")
            pack_manifest_json = os.path.join(pack_path, "pack_manifest.json")
            if not (
                os.path.isfile(pack_toml)
                or os.path.isfile(pack_manifest)
                or os.path.isfile(pack_json)
                or os.path.isfile(pack_manifest_json)
            ):
                violations.append("{}: missing pack manifest".format(pack_name))
            for entry in os.listdir(pack_path):
                entry_path = os.path.join(pack_path, entry)
                if os.path.isdir(entry_path):
                    if entry not in ALLOWED_DIRS:
                        violations.append("{}: forbidden directory '{}'".format(pack_name, entry))
                else:
                    if entry not in ALLOWED_FILES:
                        violations.append("{}: forbidden file '{}'".format(pack_name, entry))

    if violations:
        print("{}: pack scope violations detected".format(invariant_id))
        for item in sorted(violations):
            print(item)
        return 1

    print("pack scope enforcement OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
