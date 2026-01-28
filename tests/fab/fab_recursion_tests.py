import argparse
import json
import os
import subprocess
import sys


def run_inspect(repo_root, input_path):
    script = os.path.join(repo_root, "tools", "fab", "fab_inspect.py")
    cmd = [sys.executable, script, "--input", input_path, "--repo-root", repo_root, "--format", "json"]
    output = subprocess.check_output(cmd, cwd=repo_root)
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="FAB recursion tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    pack_path = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_recursive.json")
    out = run_inspect(repo_root, pack_path)
    assemblies = {entry.get("assembly_id"): entry for entry in out.get("assemblies", [])}

    parent = assemblies.get("dominium.game.assembly.parent")
    if not parent:
        print("fab recursion: missing parent assembly")
        return 1
    if parent.get("total_mass") != 100:
        print("fab recursion: expected total_mass=100, got {}".format(parent.get("total_mass")))
        return 1
    hosted = parent.get("hosted_processes", [])
    if hosted != ["dominium.game.process_family.child", "dominium.game.process_family.parent"]:
        print("fab recursion: hosted processes mismatch")
        return 1

    print("fab recursion OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
