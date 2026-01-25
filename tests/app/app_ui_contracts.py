import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, expect_code=0, expect_nonzero=False, expect_contains=None, env=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        env=env,
    )
    output = result.stdout
    ok = True
    if expect_nonzero:
        if result.returncode == 0:
            sys.stderr.write("FAIL: expected non-zero exit for {}\n".format(cmd))
            sys.stderr.write(output)
            ok = False
    elif expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        ok = False
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                ok = False
                break
    return ok, output


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def read_text(path):
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_supported_renderers(output):
    renderers = []
    for line in output.splitlines():
        if not line.startswith("renderer="):
            continue
        parts = line.split()
        head = parts[0]
        name = head.split("=", 1)[1] if "=" in head else ""
        supported = "supported=1" in line
        if name and supported:
            renderers.append(name)
    return renderers


def compare_event_logs(label, cli_cmd, gui_cmd):
    cli_ok, _cli_out = run_cmd(cli_cmd)
    gui_ok, _gui_out = run_cmd(gui_cmd)
    if not cli_ok or not gui_ok:
        sys.stderr.write("FAIL: {} command execution failed\n".format(label))
        return False
    cli_log = read_text(cli_cmd[cli_cmd.index("--ui-log") + 1])
    gui_log = read_text(gui_cmd[gui_cmd.index("--ui-log") + 1])
    if cli_log != gui_log:
        sys.stderr.write("FAIL: {} event logs differ\n".format(label))
        sys.stderr.write("CLI:\n{}\nGUI:\n{}\n".format(cli_log, gui_log))
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="UI-0 TestX contracts.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--launcher", required=True)
    parser.add_argument("--tools", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)

    ok = True

    # 1) Zero-pack GUI boot (launcher, headless).
    ok = ok and run_cmd(
        [args.launcher, "--ui=gui", "--headless", "--renderer", "null", "--ui-frames", "1"]
    )[0]

    # 2) GUI navigation with null renderer (launcher).
    nav_log = os.path.join(temp_root, "launcher_nav.log")
    ok = ok and run_cmd(
        [
            args.launcher,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-script",
            "new-world,settings,back,exit",
            "--ui-frames",
            "4",
            "--ui-log",
            nav_log,
        ]
    )[0]
    nav_text = read_text(nav_log)
    if ("launcher.new_world" not in nav_text or
            "launcher.settings" not in nav_text or
            "launcher.exit" not in nav_text):
        sys.stderr.write("FAIL: launcher navigation log missing events\n")
        ok = False

    # 3) CLI ↔ GUI parity (launcher/tools/client).
    log_cli = os.path.join(temp_root, "launcher_cli.log")
    log_gui = os.path.join(temp_root, "launcher_gui.log")
    ok = ok and compare_event_logs(
        "launcher.new_world",
        [args.launcher, "--ui-log", log_cli, "new-world"],
        [
            args.launcher,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-log",
            log_gui,
            "--ui-script",
            "new-world",
            "--ui-frames",
            "2",
        ],
    )
    log_tui = os.path.join(temp_root, "launcher_tui.log")
    ok = ok and compare_event_logs(
        "launcher.new_world.tui",
        [args.launcher, "--ui-log", log_cli, "new-world"],
        [
            args.launcher,
            "--ui=tui",
            "--ui-log",
            log_tui,
            "--ui-script",
            "new-world",
            "--ui-frames",
            "2",
        ],
    )

    log_cli = os.path.join(temp_root, "tools_cli.log")
    log_gui = os.path.join(temp_root, "tools_gui.log")
    ok = ok and compare_event_logs(
        "tools.settings",
        [args.tools, "--ui-log", log_cli, "settings"],
        [
            args.tools,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-log",
            log_gui,
            "--ui-script",
            "settings",
            "--ui-frames",
            "2",
        ],
    )
    log_tui = os.path.join(temp_root, "tools_tui.log")
    ok = ok and compare_event_logs(
        "tools.settings.tui",
        [args.tools, "--ui-log", log_cli, "settings"],
        [
            args.tools,
            "--ui=tui",
            "--ui-log",
            log_tui,
            "--ui-script",
            "settings",
            "--ui-frames",
            "2",
        ],
    )

    log_cli = os.path.join(temp_root, "client_cli.log")
    log_gui = os.path.join(temp_root, "client_gui.log")
    ok = ok and compare_event_logs(
        "client.world.create",
        [args.client, "--ui-log", log_cli, "new-world"],
        [
            args.client,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-log",
            log_gui,
            "--ui-script",
            "new-world,create-world",
            "--ui-frames",
            "3",
        ],
    )
    log_tui = os.path.join(temp_root, "client_tui.log")
    ok = ok and compare_event_logs(
        "client.world.create.tui",
        [args.client, "--ui-log", log_cli, "new-world"],
        [
            args.client,
            "--ui=tui",
            "--ui-log",
            log_tui,
            "--ui-script",
            "new-world,create-world",
            "--ui-frames",
            "3",
        ],
    )

    # 4) UI cannot mutate state (tools inspect before/after GUI).
    ok_before, before_out = run_cmd([args.tools, "inspect"])
    ok = ok and ok_before
    ok = ok and run_cmd(
        [
            args.tools,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-script",
            "settings",
            "--ui-frames",
            "2",
        ]
    )[0]
    ok_after, after_out = run_cmd([args.tools, "inspect"])
    ok = ok and ok_after
    if ok_before and ok_after and before_out != after_out:
        sys.stderr.write("FAIL: tools inspect output changed after UI run\n")
        ok = False

    # 5) Headless GUI execution in CI (client).
    ok = ok and run_cmd(
        [args.client, "--ui=gui", "--headless", "--renderer", "null", "--ui-frames", "1"]
    )[0]

    # 6) Renderer swap does not affect behavior (launcher).
    caps_ok, caps_out = run_cmd([args.launcher, "capabilities"])
    ok = ok and caps_ok
    renderers = parse_supported_renderers(caps_out) if caps_ok else []
    preferred = []
    if "null" in renderers:
        preferred.append("null")
    if "soft" in renderers:
        preferred.append("soft")
    for name in renderers:
        if name not in preferred:
            preferred.append(name)
    if len(preferred) < 2:
        sys.stderr.write("FAIL: not enough renderers for swap test\n")
        ok = False
    else:
        swap_a = preferred[0]
        swap_b = preferred[1]
        log_a = os.path.join(temp_root, "swap_a.log")
        log_b = os.path.join(temp_root, "swap_b.log")
        ok = ok and run_cmd(
            [
                args.launcher,
                "--ui=gui",
                "--headless",
                "--renderer",
                swap_a,
                "--ui-log",
                log_a,
                "--ui-script",
                "new-world",
                "--ui-frames",
                "2",
            ]
        )[0]
        ok = ok and run_cmd(
            [
                args.launcher,
                "--ui=gui",
                "--headless",
                "--renderer",
                swap_b,
                "--ui-log",
                log_b,
                "--ui-script",
                "new-world",
                "--ui-frames",
                "2",
            ]
        )[0]
        if read_text(log_a) != read_text(log_b):
            sys.stderr.write("FAIL: renderer swap logs differ ({}, {})\n".format(swap_a, swap_b))
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
