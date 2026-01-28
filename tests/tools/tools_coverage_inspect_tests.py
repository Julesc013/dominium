import argparse
import json
import os
import subprocess
import sys


def run_coverage(repo_root, pack_ids):
    script = os.path.join(repo_root, "tools", "coverage", "coverage_inspect.py")
    cmd = [sys.executable, script, "--repo-root", repo_root, "--format", "json"]
    for pack_id in pack_ids:
        cmd.extend(["--pack-id", pack_id])
    output = subprocess.check_output(cmd, cwd=repo_root)
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="coverage_inspect tool tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    pack_ids = ["org.dominium.core.ecology.basic", "org.dominium.worldgen.anchors.planetary"]
    out_a = run_coverage(repo_root, pack_ids)
    out_b = run_coverage(repo_root, pack_ids)

    levels = out_a.get("levels", {})
    if "C-A" not in levels:
        print("coverage_inspect missing levels")
        return 1
    status = levels["C-A"].get("status")
    if status not in ("UNSUPPORTED", "PARTIAL", "COMPLETE"):
        print("coverage_inspect invalid status")
        return 1
    if out_a != out_b:
        print("coverage_inspect nondeterministic")
        return 1

    print("coverage_inspect OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
