import argparse
import json
import os
import subprocess
import sys


def run_inspect(repo_root, input_path):
    script = os.path.join(repo_root, "tools", "fab", "fab_inspect.py")
    cmd = [sys.executable, script, "--input", input_path, "--repo-root", repo_root, "--format", "json"]
    output = subprocess.check_output(cmd, cwd=repo_root)
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="FAB determinism tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    a_path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_good_a.json")
    b_path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_good_b.json")

    out_a = run_inspect(repo_root, a_path)
    out_b = run_inspect(repo_root, b_path)
    if out_a != out_b:
        print("fab determinism failed: outputs differ")
        return 1

    print("fab determinism OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
