import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, expect_code=0, expect_contains=None, cwd=None, env=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        cwd=cwd,
        env=env,
    )
    output = result.stdout
    ok = True
    if expect_code is not None:
        if isinstance(expect_code, (list, tuple, set)):
            if result.returncode not in expect_code:
                sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
                sys.stderr.write(output)
                ok = False
        elif result.returncode != expect_code:
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


def extract_refusal_lines(text, tag=None):
    lines = []
    for line in text.splitlines():
        if tag and tag not in line:
            continue
        if "result=unavailable" in line or "result=refused" in line or "refusal" in line:
            lines.append(line)
    return lines


def require_events(text, required, label):
    ok = True
    for token in required:
        if token not in text:
            sys.stderr.write("FAIL: missing '{}' in {}\n".format(token, label))
            ok = False
    return ok


def main():
    parser = argparse.ArgumentParser(description="Client menu parity tests (P3).")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    client_path = os.path.abspath(args.client)
    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)

    ok = True

    # Refusal parity for load-world with no saves.
    refusal_root = os.path.join(temp_root, "refusal")
    ensure_clean_dir(refusal_root)
    os.makedirs(os.path.join(refusal_root, "data", "saves"))
    refusal_env = dict(os.environ)
    refusal_env["DOM_DATA_ROOT"] = os.path.join(refusal_root, "data")
    refusal_env["DOM_INSTANCE_ROOT"] = os.path.join(refusal_root, "data")

    log_cli = os.path.join(refusal_root, "client_refusal_cli.log")
    log_gui = os.path.join(refusal_root, "client_refusal_gui.log")
    log_tui = os.path.join(refusal_root, "client_refusal_tui.log")

    ok = ok and run_cmd(
        [client_path, "--ui-log", log_cli, "load-world"],
        expect_code=(0, 3),
        cwd=refusal_root,
        env=refusal_env,
    )[0]
    ok = ok and run_cmd(
        [
            client_path,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-log",
            log_gui,
            "--ui-script",
            "load-world",
            "--ui-frames",
            "2",
        ],
        expect_code=(0, 3),
        cwd=refusal_root,
        env=refusal_env,
    )[0]
    ok = ok and run_cmd(
        [
            client_path,
            "--ui=tui",
            "--ui-log",
            log_tui,
            "--ui-script",
            "load-world",
            "--ui-frames",
            "2",
        ],
        expect_code=(0, 3),
        cwd=refusal_root,
        env=refusal_env,
    )[0]

    cli_refusal = extract_refusal_lines(read_text(log_cli), "client.world.load")
    gui_refusal = extract_refusal_lines(read_text(log_gui), "client.world.load")
    tui_refusal = extract_refusal_lines(read_text(log_tui), "client.world.load")
    if cli_refusal != gui_refusal or cli_refusal != tui_refusal:
        sys.stderr.write("FAIL: load-world refusal lines differ across CLI/TUI/GUI\n")
        ok = False

    # Prepare world + replay artifacts via CLI.
    flow_root = os.path.join(temp_root, "flow")
    ensure_clean_dir(flow_root)
    os.makedirs(os.path.join(flow_root, "data", "saves"))
    os.makedirs(os.path.join(flow_root, "data", "replays"))
    flow_env = dict(os.environ)
    flow_env["DOM_DATA_ROOT"] = os.path.join(flow_root, "data")
    flow_env["DOM_INSTANCE_ROOT"] = os.path.join(flow_root, "data")

    ok = ok and run_cmd(
        [client_path, "create-world template=builtin.minimal_system seed=1"],
        expect_contains=["world_create=ok", "world_save=ok"],
        cwd=flow_root,
        env=flow_env,
    )[0]

    save_dir = os.path.join(flow_root, "data", "saves")
    saves = [name for name in os.listdir(save_dir) if name.endswith(".save")]
    if not saves:
        sys.stderr.write("FAIL: no saves produced in {}\n".format(save_dir))
        ok = False
        saves = []
    if saves:
        save_path = os.path.join(save_dir, saves[0])
        replay_path = os.path.join(flow_root, "data", "replays", "session.replay")
        shutil.copyfile(save_path, replay_path)

    script = (
        "new-world,create-world,back,"
        "load-world,load-world,back,"
        "replay,replay,settings,accessibility-next,keybind-next,back,"
        "tools,back,exit"
    )
    log_gui_flow = os.path.join(flow_root, "client_gui_flow.log")
    log_tui_flow = os.path.join(flow_root, "client_tui_flow.log")

    ok = ok and run_cmd(
        [
            client_path,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-log",
            log_gui_flow,
            "--ui-script",
            script,
            "--ui-frames",
            "24",
        ],
        cwd=flow_root,
        env=flow_env,
    )[0]
    ok = ok and run_cmd(
        [
            client_path,
            "--ui=tui",
            "--ui-log",
            log_tui_flow,
            "--ui-script",
            script,
            "--ui-frames",
            "24",
        ],
        cwd=flow_root,
        env=flow_env,
    )[0]

    required_events = [
        "client.world.create",
        "client.world.save",
        "client.world.load",
        "client.replay.inspect",
        "client.settings",
        "client.tools",
    ]
    ok = ok and require_events(read_text(log_gui_flow), required_events, "GUI flow log")
    ok = ok and require_events(read_text(log_tui_flow), required_events, "TUI flow log")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
