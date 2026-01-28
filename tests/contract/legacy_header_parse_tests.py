import argparse
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Public header legacy-parse wrapper.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    script_path = os.path.join(repo_root, "tests", "app", "legacy_header_tests.py")
    if not os.path.isfile(script_path):
        print("missing legacy header test script: {}".format(script_path))
        return 1

    cmd = [sys.executable, script_path, "--repo-root", repo_root]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.stdout:
        print(result.stdout.strip())
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
