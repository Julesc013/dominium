import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, cwd=None, env=None, expect_codes=(0,)):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        cwd=cwd,
        env=env,
    )
    output = result.stdout or ""
    if result.returncode not in expect_codes:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_codes, cmd))
        sys.stderr.write(output)
        return False, output
    return True, output


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


def read_text(path):
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def contains_event(log_text, token):
    for line in log_text.splitlines():
        if token in line:
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Client CLI/TUI/GUI parity checks for canonical command bridge.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    client_path = os.path.abspath(args.client)
    temp_root = os.path.abspath(args.temp_root)
    data_root = os.path.join(temp_root, "data")
    ensure_clean_dir(data_root)
    os.makedirs(os.path.join(data_root, "saves"), exist_ok=True)
    os.makedirs(os.path.join(data_root, "replays"), exist_ok=True)

    env = dict(os.environ)
    env["DOM_DATA_ROOT"] = data_root
    env["DOM_INSTANCE_ROOT"] = data_root

    ok = True
    cli_log = os.path.join(temp_root, "cli.log")
    tui_log = os.path.join(temp_root, "tui.log")
    gui_log = os.path.join(temp_root, "gui.log")

    ok_cli, _ = run_cmd([client_path, "--ui-log", cli_log, "client.options.get"], env=env)
    ok = ok and ok_cli

    ok_tui, _ = run_cmd(
        [
            client_path,
            "--ui=tui",
            "--ui-log",
            tui_log,
            "--ui-script",
            "settings,exit",
            "--ui-frames",
            "6",
        ],
        env=env,
        expect_codes=(0, 3),
    )
    ok = ok and ok_tui

    ok_gui, _ = run_cmd(
        [
            client_path,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-log",
            gui_log,
            "--ui-script",
            "settings,exit",
            "--ui-frames",
            "6",
        ],
        env=env,
        expect_codes=(0, 3),
    )
    ok = ok and ok_gui

    cli_text = read_text(cli_log)
    tui_text = read_text(tui_log)
    gui_text = read_text(gui_log)

    ok = ok and require(contains_event(cli_text, "client.settings"), "CLI log missing client.settings event")
    ok = ok and require(contains_event(tui_text, "client.settings"), "TUI log missing client.settings event")
    ok = ok and require(contains_event(gui_text, "client.settings"), "GUI log missing client.settings event")

    if not ok:
        return 1
    print("client_parity=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
