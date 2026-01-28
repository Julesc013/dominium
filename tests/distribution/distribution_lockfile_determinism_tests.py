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
    parser = argparse.ArgumentParser(description="Distribution lockfile determinism tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    lock_a = os.path.join("tests", "distribution", "fixtures", "lockfiles", "lockfile_a.json")
    lock_b = os.path.join("tests", "distribution", "fixtures", "lockfiles", "lockfile_b.json")

    out_a = run_tool(repo_root, "tools/distribution/lockfile_inspect.py",
                     ["--input", lock_a, "--format", "json"])
    out_b = run_tool(repo_root, "tools/distribution/lockfile_inspect.py",
                     ["--input", lock_b, "--format", "json"])
    if out_a != out_b:
        print("lockfile determinism: outputs differ")
        return 1

    print("distribution lockfile determinism OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
