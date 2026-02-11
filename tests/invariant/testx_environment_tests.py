import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def _run(cmd, cwd, env):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def _runner_command(repo_root):
    return [
        sys.executable,
        os.path.join(repo_root, "scripts", "dev", "run_testx.py"),
        "--repo-root",
        repo_root,
        "--test-dir",
        os.path.join(repo_root, "out", "build", "vs2026", "verify"),
        "--include-regex",
        "inv_repox_rules",
        "--output-on-failure",
    ]


def case_empty_path(repo_root):
    env = dict(os.environ)
    env["PATH"] = ""
    env.pop("DOM_HOST_PATH", None)
    env.pop("DOM_TOOLS_PATH", None)
    proc = _run(_runner_command(repo_root), cwd=repo_root, env=env)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        return 1
    print("test_testx_empty_path=ok")
    return 0


def case_arbitrary_cwd(repo_root):
    env = dict(os.environ)
    random_cwd = tempfile.mkdtemp(prefix="dom-testx-cwd-")
    try:
        proc = _run(_runner_command(repo_root), cwd=random_cwd, env=env)
    finally:
        shutil.rmtree(random_cwd, ignore_errors=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        return 1
    print("test_testx_arbitrary_cwd=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="TestX self-contained environment checks.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--case", choices=("empty_path", "arbitrary_cwd"), required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    if args.case == "empty_path":
        return case_empty_path(repo_root)
    return case_arbitrary_cwd(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
