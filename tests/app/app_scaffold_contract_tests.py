import argparse
import os
import re
import sys


GUI_STUBS = [
    ("launcher", "launcher/gui/launcher_app_win32.cpp"),
    ("setup", "setup/gui/setup_app_win32.cpp"),
    ("client", "client/gui/client_app_win32.cpp"),
    ("server", "server/gui/server_app_win32.cpp"),
    ("tools", "tools/gui/tools_app_win32.cpp"),
]

REQUIRED_UI_SYMBOLS = [
    "domui_win32_register_accessibility",
    "domui_win32_enable_keyboard_nav",
    "domui_win32_set_dpi_scale",
    "domui_win32_load_ui_ir",
    "domui_win32_run_shell",
]

ALLOWED_CONTRACT_INCLUDES = {
    "domino/core/types.h",
}


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def iter_contract_headers(repo_root):
    base = os.path.join(repo_root, "libs", "contracts", "include", "dom_contracts")
    for name in os.listdir(base):
        if not name.startswith("app_") or not name.endswith(".h"):
            continue
        yield os.path.join(base, name)


def check_contract_includes(repo_root, violations):
    include_re = re.compile(r"#include\\s+[\"<]([^\">]+)[\">]")
    for path in iter_contract_headers(repo_root):
        rel = os.path.relpath(path, repo_root).replace("\\", "/")
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for lineno, line in enumerate(handle, start=1):
                match = include_re.search(line)
                if not match:
                    continue
                inc = match.group(1)
                if inc in ALLOWED_CONTRACT_INCLUDES:
                    continue
                if inc.startswith("dom_contracts/"):
                    continue
                violations.append(
                    "{}:{}: forbidden include '{}'".format(rel, lineno, inc)
                )


def load_registry_commands(repo_root):
    registry_path = os.path.join(
        repo_root, "libs", "appcore", "command", "command_registry.c"
    )
    text = read_text(registry_path)
    cmd_re = re.compile(r"\\{\\s*DOM_APP_CMD_[^,]+,\\s*\"([^\"]+)\"")
    return set(cmd_re.findall(text))


def check_ui_header(repo_root, violations):
    header_path = os.path.join(
        repo_root, "shared_ui_win32", "include", "dom_ui_win32", "ui_win32.h"
    )
    if not os.path.isfile(header_path):
        violations.append("missing shared UI header: {}".format(header_path))
        return
    text = read_text(header_path)
    for symbol in REQUIRED_UI_SYMBOLS:
        if symbol not in text:
            violations.append("missing UI symbol '{}' in {}".format(symbol, header_path))


def check_gui_stub(repo_root, name, rel_path, registry_names, violations):
    abs_path = os.path.join(repo_root, rel_path)
    if not os.path.isfile(abs_path):
        violations.append("missing GUI stub: {}".format(rel_path))
        return
    text = read_text(abs_path)
    if "command/command_registry.h" not in text:
        violations.append("{}: missing command_registry include".format(rel_path))
    if "appcore_dispatch_command" not in text:
        violations.append("{}: missing appcore_dispatch_command call".format(rel_path))
    include_re = re.compile(r"#include\\s+\"([^\"]+)\"")
    for match in include_re.findall(text):
        if match in ("command/command_registry.h", "dom_ui_win32/ui_win32.h"):
            continue
        if match.startswith("domino/") or match.startswith("dominium/"):
            violations.append("{}: forbidden include '{}'".format(rel_path, match))
    find_re = re.compile(r"appcore_command_find\\(\"([^\"]+)\"\\)")
    for cmd_name in find_re.findall(text):
        if cmd_name not in registry_names:
            violations.append(
                "{}: command '{}' not found in registry".format(rel_path, cmd_name)
            )


def check_gui_targets(targets, violations):
    for label, path in targets.items():
        if not path:
            continue
        if not os.path.isfile(path):
            violations.append("missing GUI target '{}' at {}".format(label, path))
            continue
        if os.path.getsize(path) == 0:
            violations.append("empty GUI target '{}' at {}".format(label, path))


def main():
    parser = argparse.ArgumentParser(description="APP-AUTO-0 scaffold contract checks.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--launcher-gui")
    parser.add_argument("--setup-gui")
    parser.add_argument("--client-gui")
    parser.add_argument("--server-gui")
    parser.add_argument("--tools-gui")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    violations = []

    check_contract_includes(repo_root, violations)
    check_ui_header(repo_root, violations)

    registry_names = load_registry_commands(repo_root)
    for name, rel_path in GUI_STUBS:
        check_gui_stub(repo_root, name, rel_path, registry_names, violations)

    check_gui_targets(
        {
            "launcher": args.launcher_gui,
            "setup": args.setup_gui,
            "client": args.client_gui,
            "server": args.server_gui,
            "tools": args.tools_gui,
        },
        violations,
    )

    if violations:
        for violation in violations:
            sys.stderr.write("FAIL: {}\n".format(violation))
        return 1

    print("APP-AUTO-0 scaffold contract checks OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
