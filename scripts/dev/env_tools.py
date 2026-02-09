#!/usr/bin/env python3
import argparse
import json
import os
import platform
import shutil
import sys


CANONICAL_TOOL_IDS = (
    "tool_ui_bind",
    "tool_ui_validate",
    "tool_ui_doc_annotate",
)


def _norm(path):
    return os.path.normpath(path)


def _norm_case(path):
    return os.path.normcase(_norm(path))


def _host_platform_id():
    sys_name = platform.system().lower()
    if sys_name.startswith("win"):
        return "winnt"
    if sys_name == "linux":
        return "linux"
    if sys_name == "darwin":
        return "macosx"
    raise RuntimeError("refuse.platform_unsupported: {}".format(sys_name))


def _host_arch_candidates():
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64"):
        return ["x64", "x86_64"]
    if machine in ("x86", "i386", "i686"):
        return ["x86", "x86_32"]
    if machine in ("arm64", "aarch64"):
        return ["arm64"]
    if machine.startswith("arm"):
        return ["arm", "arm32"]
    return [machine]


def _resolve_tool_dir(repo_root, platform_id="", arch_id=""):
    plat = platform_id or _host_platform_id()
    candidates = [arch_id] if arch_id else _host_arch_candidates()
    candidates = [item for item in candidates if item]
    for arch in candidates:
        candidate = os.path.join(repo_root, "dist", "sys", plat, arch, "bin", "tools")
        if os.path.isdir(candidate):
            return _norm(candidate), plat, arch, candidates
    arch = candidates[0] if candidates else "x64"
    fallback = os.path.join(repo_root, "dist", "sys", plat, arch, "bin", "tools")
    return _norm(fallback), plat, arch, candidates


def _tool_filename(tool_id):
    if os.name == "nt":
        return tool_id + ".exe"
    return tool_id


def _split_path(path_value):
    if not path_value:
        return []
    return [item for item in path_value.split(os.pathsep) if item]


def _prepend_path(path_value, tool_dir):
    items = _split_path(path_value)
    norm_tool = _norm_case(tool_dir)
    kept = []
    seen = set()
    for item in items:
        norm_item = _norm_case(item)
        if norm_item in seen:
            continue
        seen.add(norm_item)
        if norm_item == norm_tool:
            continue
        kept.append(item)
    return os.pathsep.join([tool_dir] + kept)


def _tool_status(repo_root, tool_dir, require_path):
    files_missing = []
    names_unresolvable = []
    for tool_id in CANONICAL_TOOL_IDS:
        expected = os.path.join(tool_dir, _tool_filename(tool_id))
        if not os.path.isfile(expected):
            files_missing.append(expected)
        if require_path and shutil.which(_tool_filename(tool_id)) is None and shutil.which(tool_id) is None:
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
    tool_dir, _, _, _ = _resolve_tool_dir(args.repo_root, args.platform, args.arch)
    print(tool_dir)
    return 0


def _handle_export(args):
    tool_dir, _, _, _ = _resolve_tool_dir(args.repo_root, args.platform, args.arch)
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
    tool_dir, platform_id, arch_id, candidates = _resolve_tool_dir(args.repo_root, args.platform, args.arch)
    status = _tool_status(args.repo_root, tool_dir, require_path=args.require_path)
    status["platform"] = platform_id
    status["arch"] = arch_id
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


def _build_parser():
    parser = argparse.ArgumentParser(description="Canonical tool PATH adapter.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--platform", default="")
    parser.add_argument("--arch", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("print-path", help="Print canonical tools directory path.")

    p_export = sub.add_parser("export", help="Emit shell commands to set canonical PATH.")
    p_export.add_argument("--shell", default="cmd")

    p_doctor = sub.add_parser("doctor", help="Validate canonical tools path and tool discoverability.")
    p_doctor.add_argument("--require-path", action="store_true")
    p_doctor.add_argument("--format", choices=("text", "json"), default="text")
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
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
