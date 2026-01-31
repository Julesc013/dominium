import argparse
import os
import sys


ALLOWED_DIRS = {
    "data",
    "content",
    "schema",
    "ui",
    "docs",
}

ALLOWED_FILES = {
    "pack.toml",
    "pack.manifest",
    "pack_manifest.json",
    "README.md",
    "README.txt",
    "LICENSE",
    "LICENSE.md",
    "CHANGELOG.md",
    ".keep",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Contract: pack scope enforcement.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    packs_root = os.path.join(repo_root, "data", "packs")

    invariant_id = "INV-PACK-SCOPE"
    if not os.path.isdir(packs_root):
        print("{}: missing data/packs directory".format(invariant_id))
        return 1

    violations = []
    for pack_name in sorted(os.listdir(packs_root)):
        pack_path = os.path.join(packs_root, pack_name)
        if not os.path.isdir(pack_path):
            continue
        pack_toml = os.path.join(pack_path, "pack.toml")
        pack_manifest = os.path.join(pack_path, "pack.manifest")
        if not (os.path.isfile(pack_toml) or os.path.isfile(pack_manifest)):
            violations.append("{}: missing pack.toml or pack.manifest".format(pack_name))
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
