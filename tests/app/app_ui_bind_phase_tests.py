import argparse
import os
import subprocess
import sys


def _load_env_tools_lib(repo_root):
    dev_root = os.path.join(repo_root, "scripts", "dev")
    if dev_root not in sys.path:
        sys.path.insert(0, dev_root)
    import env_tools_lib

    return env_tools_lib


def main():
    parser = argparse.ArgumentParser(description="UI_BIND_PHASE contract test.")
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    tools_lib = _load_env_tools_lib(repo_root)
    tool_dir = tools_lib.canonical_tools_dir(repo_root)
    env = tools_lib.prepend_tools_to_path(dict(os.environ), tool_dir)
    bind_exec = tools_lib.resolve_tool("tool_ui_bind", env)
    if not bind_exec:
        sys.stderr.write("tool_ui_bind missing from canonical PATH\n")
        return 2

    cmd = [
        bind_exec,
        "--repo-root",
        repo_root,
        "--ui-index",
        os.path.join(repo_root, "tools", "ui_index", "ui_index.json"),
        "--out-dir",
        os.path.join(repo_root, "libs", "appcore", "ui_bind"),
        "--check",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return proc.returncode

    print("UI_BIND_PHASE OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
