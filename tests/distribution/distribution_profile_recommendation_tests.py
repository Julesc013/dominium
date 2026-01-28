import argparse
import json
import os
import subprocess
import sys


def run_tool(repo_root, script_rel, args):
    script = os.path.join(repo_root, script_rel)
    cmd = [sys.executable, script] + args
    result = subprocess.run(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return json.loads(result.stdout.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Distribution profile recommendation tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    profile_path = os.path.join("tests", "distribution", "fixtures", "profiles", "profile.casual.json")
    bundle_root = os.path.join("tests", "distribution", "fixtures", "packs_maximal")
    expected_recommended = sorted([
        "org.dominium.core.units",
        "org.dominium.worldgen.minimal",
    ])

    profile = run_tool(repo_root, "tools/distribution/profile_inspect.py",
                       ["--input", profile_path, "--format", "json"])
    if not profile.get("ok"):
        print("profile recommendation: expected ok")
        return 1
    if profile.get("recommended_packs") != expected_recommended:
        print("profile recommendation: mismatch")
        return 1

    compat = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", bundle_root, "--profile", profile_path, "--format", "json"])
    present = sorted(compat.get("recommended_packs_present", []))
    missing = sorted(compat.get("recommended_packs_missing", []))
    if present != expected_recommended or missing:
        print("profile recommendation: unexpected present/missing")
        return 1

    print("distribution profile recommendation OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
