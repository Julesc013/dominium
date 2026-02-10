#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys

from env_tools_lib import (
    CANONICAL_TOOL_IDS,
    WORKSPACE_ID_ENV_KEY,
    canonical_workspace_dirs,
    canonical_workspace_id,
    canonicalize_env_for_workspace,
    canonical_tools_dir_details,
    prepend_tools_to_path,
    resolve_tool,
    sanitize_workspace_id,
)

def _norm(path):
    return os.path.normpath(path)


def _norm_case(path):
    return os.path.normcase(_norm(path))


def _resolve_tool_dir(repo_root, platform_id="", arch_id="", ws_id=""):
    return canonical_tools_dir_details(repo_root, platform_id, arch_id, ws_id=ws_id)


def _tool_filename(tool_id):
    if os.name == "nt":
        return tool_id + ".exe"
    return tool_id


def _split_path(path_value):
    if not path_value:
        return []
    return [item for item in path_value.split(os.pathsep) if item]


def _prepend_path(path_value, tool_dir):
    return prepend_tools_to_path({"PATH": path_value}, tool_dir).get("PATH", "")


def _tool_status(repo_root, tool_dir, require_path):
    files_missing = []
    names_unresolvable = []
    for tool_id in CANONICAL_TOOL_IDS:
        expected = os.path.join(tool_dir, _tool_filename(tool_id))
        if not os.path.isfile(expected):
            files_missing.append(expected)
        if require_path and not resolve_tool(tool_id, os.environ):
            names_unresolvable.append(tool_id)
    ok = (not files_missing) and (not names_unresolvable)
    return {
        "ok": ok,
        "repo_root": repo_root.replace("\\", "/"),
        "tool_dir": tool_dir.replace("\\", "/"),
        "required_tools": list(CANONICAL_TOOL_IDS),
        "missing_files": [path.replace("\\", "/") for path in files_missing],
        "unresolvable_tool_names": sorted(names_unresolvable),
        "path_contains_tool_dir": _norm_case(tool_dir) in {
            _norm_case(item) for item in _split_path(os.environ.get("PATH", ""))
        },
    }


def _shell_quote_sh(value):
    return "'" + value.replace("'", "'\"'\"'") + "'"


def _shell_quote_ps(value):
    return "'" + value.replace("'", "''") + "'"


def _handle_print_path(args):
    ws_id = sanitize_workspace_id_or_default(args.repo_root, args.workspace_id)
    tool_dir, _, _, _ = _resolve_tool_dir(args.repo_root, args.platform, args.arch, ws_id=ws_id)
    print(tool_dir)
    return 0


def _handle_export(args):
    ws_id = sanitize_workspace_id_or_default(args.repo_root, args.workspace_id)
    tool_dir, _, _, _ = _resolve_tool_dir(args.repo_root, args.platform, args.arch, ws_id=ws_id)
    status = _tool_status(args.repo_root, tool_dir, require_path=False)
    if status["missing_files"]:
        print("refuse.tools_dir_missing")
        print(json.dumps(status, indent=2, sort_keys=False))
        return 2

    updated_path = _prepend_path(os.environ.get("PATH", ""), tool_dir)
    shell = args.shell.lower()
    if shell == "cmd":
        print('@set "DOM_TOOLS_PATH={}"'.format(tool_dir))
        print('@set "DOM_TOOLS_READY=1"')
        print('@set "PATH={}"'.format(updated_path))
        return 0
    if shell in ("powershell", "ps1"):
        print("$env:DOM_TOOLS_PATH = {}".format(_shell_quote_ps(tool_dir)))
        print("$env:DOM_TOOLS_READY = '1'")
        print("$env:PATH = {}".format(_shell_quote_ps(updated_path)))
        return 0
    if shell in ("sh", "bash"):
        print("export DOM_TOOLS_PATH={}".format(_shell_quote_sh(tool_dir)))
        print("export DOM_TOOLS_READY='1'")
        print("export PATH={}".format(_shell_quote_sh(updated_path)))
        return 0

    print("refuse.shell_unsupported: {}".format(args.shell))
    return 2


def _handle_doctor(args):
    ws_id = sanitize_workspace_id_or_default(args.repo_root, args.workspace_id)
    tool_dir, platform_id, arch_id, candidates = _resolve_tool_dir(
        args.repo_root, args.platform, args.arch, ws_id=ws_id
    )
    status = _tool_status(args.repo_root, tool_dir, require_path=args.require_path)
    ws_dirs = canonical_workspace_dirs(
        args.repo_root, ws_id=ws_id, platform_id=platform_id, arch_id=arch_id
    )
    status["platform"] = platform_id
    status["arch"] = arch_id
    status["workspace_id"] = ws_dirs["workspace_id"]
    status["workspace_build_root"] = ws_dirs["build_root"].replace("\\", "/")
    status["workspace_dist_root"] = ws_dirs["dist_root"].replace("\\", "/")
    status["workspace_remediation_root"] = ws_dirs["remediation_root"].replace("\\", "/")
    status["arch_candidates"] = list(candidates)
    status["refusal_code"] = "ok" if status["ok"] else "refuse.tool_discoverability_failed"

    if args.format == "json":
        print(json.dumps(status, indent=2, sort_keys=False))
    else:
        if status["ok"]:
            print("tools_path=ok")
            print("tools_dir={}".format(status["tool_dir"]))
        else:
            print("tools_path=fail")
            if status["missing_files"]:
                print("missing_files={}".format(",".join(status["missing_files"])))
            if status["unresolvable_tool_names"]:
                print("unresolvable={}".format(",".join(status["unresolvable_tool_names"])))
            print("refusal_code={}".format(status["refusal_code"]))
    return 0 if status["ok"] else 2


def _handle_run(args):
    if not args.argv:
        print("refuse.command_missing")
        return 2
    cmd = list(args.argv)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    argv0 = cmd[0]
    if "/" in argv0 or "\\" in argv0:
        print("refuse.path_invocation_forbidden: {}".format(argv0))
        return 2

    ws_id = sanitize_workspace_id_or_default(args.repo_root, args.workspace_id)
    tool_dir, platform_id, arch_id, _ = _resolve_tool_dir(args.repo_root, args.platform, args.arch, ws_id=ws_id)
    status = _tool_status(args.repo_root, tool_dir, require_path=False)
    if status["missing_files"]:
        print("refuse.tools_dir_missing")
        print(json.dumps(status, indent=2, sort_keys=False))
        return 2

    env, ws_dirs = canonicalize_env_for_workspace(
        os.environ.copy(),
        args.repo_root,
        ws_id=ws_id,
        platform_id=platform_id,
        arch_id=arch_id,
    )
    env[WORKSPACE_ID_ENV_KEY] = ws_dirs["workspace_id"]
    exec_path = shutil.which(argv0, path=env["PATH"])
    if not exec_path and os.name == "nt":
        exec_path = shutil.which(argv0 + ".exe", path=env["PATH"])
    if exec_path:
        cmd[0] = exec_path
    proc = subprocess.run(cmd, env=env, check=False)
    return int(proc.returncode)


def sanitize_workspace_id_or_default(repo_root, workspace_id):
    explicit = sanitize_workspace_id(workspace_id or "")
    if explicit:
        return explicit
    return canonical_workspace_id(repo_root, env=os.environ)


def _build_parser():
    parser = argparse.ArgumentParser(description="Canonical tool PATH adapter.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--platform", default="")
    parser.add_argument("--arch", default="")
    parser.add_argument("--workspace-id", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("print-path", help="Print canonical tools directory path.")

    p_export = sub.add_parser("export", help="Emit shell commands to set canonical PATH.")
    p_export.add_argument("--shell", default="cmd")

    p_doctor = sub.add_parser("doctor", help="Validate canonical tools path and tool discoverability.")
    p_doctor.add_argument("--require-path", action="store_true")
    p_doctor.add_argument("--format", choices=("text", "json"), default="text")

    p_run = sub.add_parser("run", help="Run a command with canonical tools PATH applied.")
    p_run.add_argument("argv", nargs=argparse.REMAINDER)
    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()
    args.repo_root = _norm(os.path.abspath(args.repo_root))
    if args.command == "print-path":
        return _handle_print_path(args)
    if args.command == "export":
        return _handle_export(args)
    if args.command == "doctor":
        return _handle_doctor(args)
    if args.command == "run":
        return _handle_run(args)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
