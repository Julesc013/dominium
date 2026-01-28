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
    parser = argparse.ArgumentParser(description="Distribution legacy pack tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    legacy_root = os.path.join("tests", "distribution", "fixtures", "packs_legacy")
    compat = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", legacy_root,
                       "--engine-pack-format", "1", "--format", "json"])
    if compat.get("ok"):
        print("legacy pack: expected refusal")
        return 1
    refusal = compat.get("refusal", {})
    if refusal.get("code") != "REFUSE_INTEGRITY_VIOLATION":
        print("legacy pack: expected integrity refusal")
        return 1

    print("distribution legacy pack OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
