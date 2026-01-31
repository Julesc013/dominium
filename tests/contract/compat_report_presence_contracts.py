import argparse
import json
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Contract: compat_report presence for ops.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-OPS-COMPAT-REPORT"
    ops_cli = os.path.join(repo_root, "tools", "ops", "ops_cli.py")
    if not os.path.isfile(ops_cli):
        print("{}: missing ops_cli.py (ops not present)".format(invariant_id))
        return 1

    cmd = [sys.executable, ops_cli, "compat", "tools", "--context", "load"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        print("{}: ops compat command failed".format(invariant_id))
        if result.stdout:
            print(result.stdout.strip())
        return result.returncode

    try:
        payload = json.loads(result.stdout)
    except ValueError:
        print("{}: ops compat output is not valid JSON".format(invariant_id))
        if result.stdout:
            print(result.stdout.strip())
        return 1

    if "compat_report" not in payload:
        print("{}: compat_report missing in ops output".format(invariant_id))
        return 1

    print("compat_report presence OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
