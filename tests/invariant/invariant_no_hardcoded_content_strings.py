import argparse
import os
import subprocess
import sys

from invariant_utils import is_override_active


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: no hardcoded pack/world IDs in code.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-NO-HARDCODED-CONTENT"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    script = os.path.join(repo_root, "tests", "invariant", "content_id_reference_tests.py")
    result = subprocess.run([sys.executable, script, "--repo-root", repo_root],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        print("{}: hardcoded content identifiers detected".format(invariant_id))
        if result.stdout:
            print(result.stdout.strip())
        return result.returncode

    if result.stdout:
        print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
