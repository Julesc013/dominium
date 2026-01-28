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
    parser = argparse.ArgumentParser(description="FAB edge compatibility tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_edge_mismatch.json")
    inspect_out = run_tool(repo_root, "tools/fab/fab_inspect.py", path)
    edges = inspect_out.get("edges", [])
    target = [edge for edge in edges if edge.get("edge_id") == "dominium.test.edge.mismatch"]
    if not target:
        print("fab_edge_compat: missing edge report")
        return 1
    edge = target[0]
    if edge.get("compat") != "refused":
        print("fab_edge_compat: expected refused compatibility")
        return 1
    refusal = edge.get("refusal", {})
    if refusal.get("code") != "REFUSE_INTEGRITY_VIOLATION":
        print("fab_edge_compat: expected integrity refusal")
        return 1
    trace = edge.get("trace", {})
    if trace.get("from_interface_id") != "dominium.test.interface.mech.high":
        print("fab_edge_compat: missing from_interface_id trace")
        return 1
    if trace.get("to_interface_id") != "dominium.test.interface.mech.low":
        print("fab_edge_compat: missing to_interface_id trace")
        return 1

    print("fab edge compatibility OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
