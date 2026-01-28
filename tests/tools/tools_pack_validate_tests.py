import argparse
import hashlib
import json
import os
import subprocess
import sys


def file_hash(path):
    data = open(path, "rb").read()
    return hashlib.sha256(data).hexdigest()


def run_pack_validate(repo_root, pack_root):
    script = os.path.join(repo_root, "tools", "pack", "pack_validate.py")
    cmd = [sys.executable, script, "--pack-root", pack_root, "--repo-root", repo_root, "--format", "json"]
    output = subprocess.check_output(cmd, cwd=repo_root)
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="pack_validate tool tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    pack_root = os.path.join(repo_root, "data", "packs", "org.dominium.core.units")
    manifest = os.path.join(pack_root, "pack_manifest.json")
    readme = os.path.join(pack_root, "docs", "README.md")

    before_manifest = file_hash(manifest)
    before_readme = file_hash(readme)

    out_a = run_pack_validate(repo_root, pack_root)
    out_b = run_pack_validate(repo_root, pack_root)

    after_manifest = file_hash(manifest)
    after_readme = file_hash(readme)

    if before_manifest != after_manifest or before_readme != after_readme:
        print("pack_validate mutated input files")
        return 1
    if not out_a.get("ok"):
        print("pack_validate failed unexpectedly")
        return 1
    if out_a != out_b:
        print("pack_validate nondeterministic")
        return 1

    print("pack_validate OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
