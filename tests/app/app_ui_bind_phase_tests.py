import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="UI_BIND_PHASE contract test.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--tool", required=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    tool_path = args.tool

    cmd = [
        tool_path,
        "--repo-root",
        repo_root,
        "--ui-index",
        os.path.join(repo_root, "tools", "ui_index", "ui_index.json"),
        "--out-dir",
        os.path.join(repo_root, "libs", "appcore", "ui_bind"),
        "--check",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return proc.returncode

    print("UI_BIND_PHASE OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
