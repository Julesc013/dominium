import argparse
import json
import os
import subprocess
import sys


def run_validate(repo_root, input_path):
    script = os.path.join(repo_root, "tools", "fab", "fab_validate.py")
    cmd = [sys.executable, script, "--input", input_path, "--repo-root", repo_root, "--format", "json"]
    result = subprocess.run(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = result.stdout
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="FAB legacy safety tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    pack_path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_empty.json")
    out = run_validate(repo_root, pack_path)
    if out.get("ok"):
        print("fab legacy safety: expected refusal on empty pack")
        return 1
    refusal = out.get("refusal", {})
    if refusal.get("code") != "REFUSE_INVALID_INTENT":
        print("fab legacy safety: expected invalid intent refusal")
        return 1

    print("fab legacy safety OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
