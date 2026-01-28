import argparse
import json
import os
import subprocess
import sys


def run_tool(repo_root, script_rel, input_path):
    script = os.path.join(repo_root, script_rel)
    cmd = [sys.executable, script, "--input", input_path, "--repo-root", repo_root, "--format", "json"]
    result = subprocess.run(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    output = result.stdout
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="FAB refusal tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    bad_path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_bad_interface.json")

    validate_out = run_tool(repo_root, "tools/fab/fab_validate.py", bad_path)
    if validate_out.get("ok"):
        print("fab_refusal: expected validation failure")
        return 1
    refusal = validate_out.get("refusal", {})
    if refusal.get("code") != "REFUSE_INTEGRITY_VIOLATION":
        print("fab_refusal: expected integrity refusal")
        return 1

    inspect_out = run_tool(repo_root, "tools/fab/fab_inspect.py", bad_path)
    edges = inspect_out.get("edges", [])
    if not edges:
        print("fab_refusal: expected edges to inspect")
        return 1
    refused = [edge for edge in edges if edge.get("compat") == "refused"]
    if not refused:
        print("fab_refusal: expected refused edge")
        return 1
    if refused[0].get("refusal", {}).get("code") != "REFUSE_INTEGRITY_VIOLATION":
        print("fab_refusal: expected refusal code on edge")
        return 1

    print("fab refusal tests OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
