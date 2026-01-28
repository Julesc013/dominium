import argparse
import json
import os
import subprocess
import sys


def run_diff(repo_root, left_path, right_path):
    script = os.path.join(repo_root, "tools", "fab", "fab_diff.py")
    cmd = [sys.executable, script, "--left", left_path, "--right", right_path, "--format", "json"]
    output = subprocess.check_output(cmd, cwd=repo_root)
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="fab_diff tool tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    left_path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_good_a.json")
    right_path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_good_b.json")

    out_a = run_diff(repo_root, left_path, right_path)
    out_b = run_diff(repo_root, left_path, right_path)

    if out_a.get("impact") not in ("none", "additive", "potentially_breaking", "breaking"):
        print("fab_diff missing impact")
        return 1
    if out_a != out_b:
        print("fab_diff nondeterministic")
        return 1

    print("fab_diff OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
