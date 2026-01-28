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
    parser = argparse.ArgumentParser(description="Distribution zero-pack tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    empty_root = os.path.join("tests", "distribution", "fixtures", "empty_root")

    discover = run_tool(repo_root, "tools/distribution/pack_discover.py",
                        ["--repo-root", repo_root, "--root", empty_root, "--format", "json"])
    packs = discover.get("packs", [])
    if packs:
        print("zero-pack: expected no packs")
        return 1

    compat = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", empty_root, "--format", "json"])
    if not compat.get("ok"):
        print("zero-pack: expected ok")
        return 1

    print("distribution zero-pack OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
