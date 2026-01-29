import argparse
import os
import subprocess
import sys

from invariant_utils import is_override_active


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: deterministic ordering policy enforced.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-DET-ORDERING"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    script = os.path.join(repo_root, "tests", "contract", "deterministic_ordering_tests.py")
    return subprocess.call([sys.executable, script, "--repo-root", repo_root])


if __name__ == "__main__":
    sys.exit(main())
