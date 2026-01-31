import argparse
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Contract: schema unknown field preservation.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-SCHEMA-UNKNOWN-PRESERVE"
    script = os.path.join(repo_root, "tests", "schema", "schema_unknown_field_tests.py")
    result = subprocess.run([sys.executable, script, "--repo-root", repo_root],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        print("{}: schema unknown-field roundtrip failed".format(invariant_id))
        if result.stdout:
            print(result.stdout.strip())
        return result.returncode

    if result.stdout:
        print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
