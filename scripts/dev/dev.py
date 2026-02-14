#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys


CANONICAL_TOOLS = (
    "tool_ui_bind",
    "tool_ui_validate",
    "tool_ui_doc_annotate",
)


def _repo_root_from_args(value):
    if value:
        return os.path.abspath(value)
    here = os.path.abspath(__file__)
    return os.path.normpath(os.path.join(os.path.dirname(here), "..", ".."))


def _env_tools_path(repo_root):
    return os.path.join(repo_root, "scripts", "dev", "env_tools.py")


def _gate_path(repo_root):
    return os.path.join(repo_root, "scripts", "dev", "gate.py")


def _run_env_tools(repo_root, args, workspace_id=""):
    cmd = [sys.executable, _env_tools_path(repo_root), "--repo-root", repo_root]
    if workspace_id:
        cmd.extend(["--workspace-id", workspace_id])
    cmd += list(args)
    return subprocess.run(cmd, check=False)


def _run_env_tools_capture(repo_root, args, workspace_id=""):
    cmd = [sys.executable, _env_tools_path(repo_root), "--repo-root", repo_root]
    if workspace_id:
        cmd.extend(["--workspace-id", workspace_id])
    cmd += list(args)
    return subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )


def cmd_tools_list(repo_root, workspace_id=""):
    proc = _run_env_tools_capture(repo_root, ["print-path"], workspace_id=workspace_id)
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        return proc.returncode
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    tool_dir = lines[-1] if lines else ""
    print("tools_dir={}".format(tool_dir.replace("\\", "/")))
    for tool in CANONICAL_TOOLS:
        path = os.path.join(tool_dir, tool + (".exe" if os.name == "nt" else ""))
        status = "present" if os.path.isfile(path) else "missing"
        print("{}={}".format(tool, status))
    return 0


def cmd_tools_doctor(repo_root, workspace_id=""):
    python_cmd = "python"
    if shutil.which(python_cmd) is None:
        python_cmd = "python3"
    return _run_env_tools(
        repo_root,
        ["run", "--", python_cmd, _env_tools_path(repo_root), "--repo-root", repo_root, "doctor", "--require-path"],
        workspace_id=workspace_id,
    ).returncode


def cmd_tools_ui_bind(repo_root, passthrough, workspace_id=""):
    args = ["run", "--", "tool_ui_bind"] + list(passthrough)
    return _run_env_tools(repo_root, args, workspace_id=workspace_id).returncode


def cmd_gate(repo_root, action, passthrough, workspace_id=""):
    cmd = [sys.executable, _gate_path(repo_root), action, "--repo-root", repo_root]
    if workspace_id:
        cmd.extend(["--workspace-id", workspace_id])
    cmd += list(passthrough)
    return subprocess.run(cmd, check=False).returncode


def build_parser():
    parser = argparse.ArgumentParser(description="Developer convenience wrapper commands.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--workspace-id", default="")
    sub = parser.add_subparsers(dest="group", required=True)

    tools = sub.add_parser("tools", help="Canonical tool wrapper commands.")
    tools_sub = tools.add_subparsers(dest="action", required=True)

    tools_sub.add_parser("list", help="List canonical tools and presence under canonical tools root.")
    tools_sub.add_parser("doctor", help="Run canonical tool discoverability doctor through adapter.")

    ui_bind = tools_sub.add_parser("ui_bind", help="Run tool_ui_bind through canonical adapter.")
    ui_bind.add_argument("args", nargs=argparse.REMAINDER)

    gate = sub.add_parser("gate", help="Run autonomous gate workflow.")
    gate_sub = gate.add_subparsers(dest="action", required=True)
    gate_sub.add_parser("precheck", help="Run dependency-aware minimal precheck gates.")
    gate_sub.add_parser("taskcheck", help="Run dependency-aware task gates without strict exits.")
    gate_sub.add_parser("exitcheck", help="Run strict exit gates with dependency checks.")
    gate_sub.add_parser("dev", help="Run RepoX + strict build with remediation.")
    gate_sub.add_parser("verify", help="Run RepoX + strict build + full TestX with remediation.")
    gate_sub.add_parser("strict", help="Run strict profile with impacted shards.")
    gate_sub.add_parser("full", help="Run full profile with sharded heavy runners.")
    gate_sub.add_parser("snapshot", help="Run strict snapshot and write SNAPSHOT_ONLY audit artifacts.")
    gate_sub.add_parser("dist", help="Run verify lane then explicit dist targets.")
    gate_sub.add_parser("doctor", help="Show canonical gate environment diagnostics.")
    gate_sub.add_parser("remediate", help="Run remediation-mode diagnostics for RepoX stage.")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    repo_root = _repo_root_from_args(args.repo_root)
    if args.group == "tools" and args.action == "list":
        return cmd_tools_list(repo_root, workspace_id=args.workspace_id)
    if args.group == "tools" and args.action == "doctor":
        return cmd_tools_doctor(repo_root, workspace_id=args.workspace_id)
    if args.group == "tools" and args.action == "ui_bind":
        passthrough = list(args.args)
        if passthrough and passthrough[0] == "--":
            passthrough = passthrough[1:]
        return cmd_tools_ui_bind(repo_root, passthrough, workspace_id=args.workspace_id)
    if args.group == "gate":
        return cmd_gate(repo_root, args.action, [], workspace_id=args.workspace_id)
    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
