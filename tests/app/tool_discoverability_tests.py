import argparse
import os
import shutil
import subprocess
import sys
import tempfile


CANONICAL_TOOLS = (
    "tool_ui_bind",
    "tool_ui_validate",
    "tool_ui_doc_annotate",
)


def _load_env_tools_lib(repo_root):
    dev_root = os.path.join(repo_root, "scripts", "dev")
    if dev_root not in sys.path:
        sys.path.insert(0, dev_root)
    import env_tools_lib

    return env_tools_lib


def _canonicalized_env(repo_root, base_env):
    tools_lib = _load_env_tools_lib(repo_root)
    tool_dir = tools_lib.canonical_tools_dir(repo_root)
    env = tools_lib.prepend_tools_to_path(dict(base_env), tool_dir)
    return env, tool_dir, tools_lib


def run_positive(repo_root):
    env, tool_dir, tools_lib = _canonicalized_env(repo_root, os.environ)

    if not os.path.isdir(tool_dir):
        raise RuntimeError("canonical tools directory missing: {}".format(tool_dir))

    for tool in CANONICAL_TOOLS:
        resolved = tools_lib.resolve_tool(tool, env)
        if not resolved:
            raise RuntimeError("tool not discoverable by PATH: {}".format(tool))
        help_proc = subprocess.run(
            [resolved, "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            env=env,
            check=False,
        )
        if help_proc.returncode != 0:
            raise RuntimeError("tool help failed {}: {}".format(tool, help_proc.stdout))

    bind_exec = tools_lib.resolve_tool("tool_ui_bind", env)
    if not bind_exec:
        raise RuntimeError("tool_ui_bind missing from canonical PATH")

    bind_proc = subprocess.run(
        [bind_exec, "--repo-root", repo_root, "--check"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        env=env,
        check=False,
    )
    if bind_proc.returncode != 0:
        raise RuntimeError("tool_ui_bind --check failed: {}".format(bind_proc.stdout))

    print("tool_discoverability=ok")
    return 0


def run_missing_path(repo_root):
    raw_env = os.environ.copy()
    raw_env["PATH"] = ""
    raw_env.pop("DOM_HOST_PATH", None)
    raw_env.pop("DOM_TOOLS_PATH", None)
    raw_env.pop("DOM_TOOLS_READY", None)

    repox = os.path.join(repo_root, "scripts", "ci", "check_repox_rules.py")
    proc = subprocess.run(
        [sys.executable, repox, "--repo-root", repo_root],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        env=raw_env,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "RepoX failed under empty PATH despite self-canonicalization:\n{}".format(proc.stdout)
        )
    if "RepoX governance rules OK." not in (proc.stdout or ""):
        raise RuntimeError("RepoX did not report success under empty PATH")

    gate_script = os.path.join(repo_root, "scripts", "dev", "gate.py")
    random_cwd = tempfile.mkdtemp(prefix="dom-gate-anycwd-")
    try:
        phase_proc = subprocess.run(
            [
                sys.executable,
                gate_script,
                "exitcheck",
                "--repo-root",
                repo_root,
                "--only-gate",
                "ui_bind_check",
            ],
            cwd=random_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            env=raw_env,
            check=False,
        )
        workspace_id = "test-tooldiscoverability-ws"
        doctor_proc = subprocess.run(
            [
                sys.executable,
                gate_script,
                "doctor",
                "--repo-root",
                repo_root,
                "--workspace-id",
                workspace_id,
            ],
            cwd=random_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            env=raw_env,
            check=False,
        )
    finally:
        shutil.rmtree(random_cwd, ignore_errors=True)
    if phase_proc.returncode != 0:
        raise RuntimeError(
            "gate.py ui_bind_check failed under empty PATH/any-CWD:\n{}".format(phase_proc.stdout)
        )
    if doctor_proc.returncode != 0:
        raise RuntimeError("gate.py doctor failed under empty PATH/any-CWD:\n{}".format(doctor_proc.stdout))
    if workspace_id not in (doctor_proc.stdout or ""):
        raise RuntimeError(
            "gate.py doctor did not report workspace_id under empty PATH/any-CWD:\n{}".format(doctor_proc.stdout)
        )

    print("tool_discoverability_missing_path=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Canonical tool discoverability tests.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--scenario", choices=("positive", "missing_path"), required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.scenario == "positive":
        return run_positive(repo_root)
    return run_missing_path(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
