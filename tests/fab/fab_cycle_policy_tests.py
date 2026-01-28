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
    parser = argparse.ArgumentParser(description="FAB cycle policy tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    forbidden_path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_cycle_forbidden.json")
    allowed_path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_cycle_allowed.json")

    forbidden_out = run_validate(repo_root, forbidden_path)
    if forbidden_out.get("ok"):
        print("fab_cycle_policy: expected forbidden cycle to fail")
        return 1
    issues = forbidden_out.get("issues", [])
    if not any(issue.get("code") == "cycle_forbidden" for issue in issues):
        print("fab_cycle_policy: expected cycle_forbidden issue")
        return 1

    allowed_out = run_validate(repo_root, allowed_path)
    if not allowed_out.get("ok"):
        print("fab_cycle_policy: expected allowed cycle to pass")
        return 1

    print("fab cycle policy OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
