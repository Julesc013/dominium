import argparse
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: C++17 restricted library subset.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    validator = os.path.join(repo_root, "tools", "validators", "build", "check_cpp17_forbidden_library_use.py")
    if not os.path.isfile(validator):
        print("INV-LANG-CPP17: missing validator {}".format(validator))
        return 1
    result = subprocess.run(
        [sys.executable, validator, "--repo-root", repo_root, "--strict"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.stdout:
        print(result.stdout.strip())
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
