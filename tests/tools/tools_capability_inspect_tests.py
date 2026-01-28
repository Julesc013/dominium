import argparse
import json
import os
import subprocess
import sys


def run_inspect(repo_root, pack_ids):
    script = os.path.join(repo_root, "tools", "pack", "capability_inspect.py")
    cmd = [sys.executable, script, "--repo-root", repo_root, "--format", "json"]
    for pack_id in pack_ids:
        cmd.extend(["--pack-id", pack_id])
    output = subprocess.check_output(cmd, cwd=repo_root)
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="capability_inspect tool tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    pack_ids = ["org.dominium.core.units", "org.dominium.worldgen.minimal"]
    out_a = run_inspect(repo_root, pack_ids)
    out_b = run_inspect(repo_root, pack_ids)

    provides = out_a.get("selection", {}).get("provides", [])
    if "org.dominium.core.units" not in provides:
        print("capability_inspect missing core.units")
        return 1
    if "org.dominium.worldgen.minimal" not in provides:
        print("capability_inspect missing worldgen.minimal")
        return 1
    if out_a != out_b:
        print("capability_inspect nondeterministic")
        return 1

    print("capability_inspect OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
