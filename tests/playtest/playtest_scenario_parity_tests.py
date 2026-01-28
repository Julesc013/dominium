import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, cwd=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        cwd=cwd,
    )
    return result.returncode == 0, result.stdout


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def parse_save_info(path):
    info = {"worlddef_id": "", "worlddef_hash": ""}
    if not os.path.isfile(path):
        return info
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("worlddef_id="):
                info["worlddef_id"] = line.split("=", 1)[1]
            elif line.startswith("worlddef_hash="):
                info["worlddef_hash"] = line.split("=", 1)[1]
    return info


def copy_fixture(repo_root, rel_path, dest_path):
    src = os.path.join(repo_root, rel_path)
    with open(src, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    ensure_dir(os.path.dirname(dest_path))
    with open(dest_path, "w", encoding="utf-8", errors="replace") as handle:
        handle.write(text)


def prepare_root(base, name, repo_root):
    root = os.path.join(base, name)
    ensure_clean_dir(root)
    ensure_dir(os.path.join(root, "data", "scenarios"))
    ensure_dir(os.path.join(root, "data", "saves"))
    copy_fixture(repo_root, os.path.join("tests", "fixtures", "playtest", "scenario_minimal.scenario"),
                 os.path.join(root, "data", "scenarios", "default.scenario"))
    return root


def main():
    parser = argparse.ArgumentParser(description="Scenario load parity across CLI/TUI/GUI.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)

    ok = True

    cli_root = prepare_root(temp_root, "cli", repo_root)
    cli_cmd = [
        args.client,
        "batch scenario-load path=data/scenarios/default.scenario; save",
    ]
    ok_cli, _cli_out = run_cmd(cli_cmd, cwd=cli_root)
    if not ok_cli:
        sys.stderr.write("FAIL: CLI scenario-load failed\n")
        ok = False
    cli_save = os.path.join(cli_root, "data", "saves", "world.save")
    if not os.path.isfile(cli_save):
        sys.stderr.write("FAIL: CLI save missing {}\n".format(cli_save))
        ok = False
    cli_info = parse_save_info(cli_save)

    tui_root = prepare_root(temp_root, "tui", repo_root)
    tui_cmd = [
        args.client,
        "--ui=tui",
        "--ui-script",
        "scenario-load,save,exit",
        "--ui-frames",
        "5",
    ]
    ok_tui, _tui_out = run_cmd(tui_cmd, cwd=tui_root)
    if not ok_tui:
        sys.stderr.write("FAIL: TUI scenario-load failed\n")
        ok = False
    tui_save = os.path.join(tui_root, "data", "saves", "world.save")
    if not os.path.isfile(tui_save):
        sys.stderr.write("FAIL: TUI save missing {}\n".format(tui_save))
        ok = False
    tui_info = parse_save_info(tui_save)

    gui_root = prepare_root(temp_root, "gui", repo_root)
    gui_cmd = [
        args.client,
        "--ui=gui",
        "--headless",
        "--renderer",
        "null",
        "--ui-script",
        "scenario-load,save,exit",
        "--ui-frames",
        "5",
    ]
    ok_gui, _gui_out = run_cmd(gui_cmd, cwd=gui_root)
    if not ok_gui:
        sys.stderr.write("FAIL: GUI scenario-load failed\n")
        ok = False
    gui_save = os.path.join(gui_root, "data", "saves", "world.save")
    if not os.path.isfile(gui_save):
        sys.stderr.write("FAIL: GUI save missing {}\n".format(gui_save))
        ok = False
    gui_info = parse_save_info(gui_save)

    if cli_info["worlddef_id"] and tui_info["worlddef_id"] and gui_info["worlddef_id"]:
        if not (cli_info["worlddef_id"] == tui_info["worlddef_id"] == gui_info["worlddef_id"]):
            sys.stderr.write("FAIL: worlddef_id mismatch across modes\n")
            sys.stderr.write("CLI: {}\nTUI: {}\nGUI: {}\n".format(
                cli_info["worlddef_id"], tui_info["worlddef_id"], gui_info["worlddef_id"]
            ))
            ok = False
    else:
        sys.stderr.write("FAIL: missing worlddef_id in one or more saves\n")
        ok = False

    if cli_info["worlddef_hash"] and tui_info["worlddef_hash"] and gui_info["worlddef_hash"]:
        if not (cli_info["worlddef_hash"] == tui_info["worlddef_hash"] == gui_info["worlddef_hash"]):
            sys.stderr.write("FAIL: worlddef_hash mismatch across modes\n")
            sys.stderr.write("CLI: {}\nTUI: {}\nGUI: {}\n".format(
                cli_info["worlddef_hash"], tui_info["worlddef_hash"], gui_info["worlddef_hash"]
            ))
            ok = False
    else:
        sys.stderr.write("FAIL: missing worlddef_hash in one or more saves\n")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
