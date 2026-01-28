import argparse
import json
import os
import subprocess
import sys


def run_tool(repo_root, script_rel, args):
    script = os.path.join(repo_root, script_rel)
    cmd = [sys.executable, script] + args
    result = subprocess.run(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return json.loads(result.stdout.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Distribution pack transition tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    empty_root = os.path.join("tests", "distribution", "fixtures", "empty_root")
    bundle_root = os.path.join("tests", "distribution", "fixtures", "packs_maximal")

    compat_empty = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                            ["--repo-root", repo_root, "--root", empty_root, "--format", "json"])
    if not compat_empty.get("ok"):
        print("pack transition: expected ok on empty")
        return 1

    compat_bundle = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                             ["--repo-root", repo_root, "--root", bundle_root, "--format", "json"])
    if not compat_bundle.get("ok"):
        print("pack transition: expected ok on bundle")
        return 1

    print("distribution pack transition OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
