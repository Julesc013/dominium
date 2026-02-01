import argparse
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Contract: compliance report presence.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-REPORT-COMPLIANCE"
    canon_invariant = "INV-REPORT-CANON"
    script = os.path.join(repo_root, "scripts", "ci", "compliance_report.py")
    if not os.path.isfile(script):
        print("{}: missing compliance_report.py".format(invariant_id))
        return 1

    result = subprocess.run([sys.executable, script, "--repo-root", repo_root],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        print("{}: compliance report failed".format(invariant_id))
        if result.stdout:
            print(result.stdout.strip())
        return result.returncode

    output = result.stdout or ""
    required = [
        "COMPLIANCE_REPORT",
        "build_number:",
        "schema_versions:",
        "invariants_enforced:",
    ]
    canon_required = ["CANON_COMPLIANCE_REPORT"]
    missing = [token for token in required if token not in output]
    if missing:
        print("{}: compliance report missing fields: {}".format(invariant_id, ", ".join(missing)))
        if output:
            print(output.strip())
        return 1
    missing_canon = [token for token in canon_required if token not in output]
    if missing_canon:
        print("{}: compliance report missing canon section: {}".format(canon_invariant, ", ".join(missing_canon)))
        if output:
            print(output.strip())
        return 1

    print("compliance report OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
