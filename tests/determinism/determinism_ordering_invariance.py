import argparse
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Determinism: ordering invariance.")
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-DET-ORDERING"
    script = os.path.join(repo_root, "tests", "contract", "deterministic_ordering_tests.py")
    result = subprocess.run([sys.executable, script, "--repo-root", repo_root],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        print("{}: ordering invariance failed".format(invariant_id))
        if result.stdout:
            print(result.stdout.strip())
        return result.returncode

    if result.stdout:
        print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
