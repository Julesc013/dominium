import argparse
import json
import os
import subprocess
import sys


def _run(cmd, cwd):
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def main():
    parser = argparse.ArgumentParser(description="CompatX pack compatibility matrix tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    cmd = [
        sys.executable,
        os.path.join(repo_root, "tools", "compatx", "compatx.py"),
        "pack-validate",
        "--repo-root",
        repo_root,
    ]
    result = _run(cmd, repo_root)
    if result.returncode != 0:
        print(result.stdout)
        return 1
    try:
        payload = json.loads(result.stdout or "{}")
    except ValueError:
        print(result.stdout)
        return 1
    if payload.get("result") != "complete":
        print(result.stdout)
        return 1
    if not bool(payload.get("sample_transition_found", False)):
        print(result.stdout)
        return 1

    print("compatx_pack_matrix_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

