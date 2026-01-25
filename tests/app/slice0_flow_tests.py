import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, expect_code=0, expect_nonzero=False, expect_contains=None, cwd=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        cwd=cwd,
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


def parse_save_info(path):
    info = {
        "header": "",
        "worlddef_hash": "",
        "worlddef_id": "",
        "worlddef_len": "",
        "schema_version": "",
    }
    if not os.path.isfile(path):
        return info
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if not info["header"] and line.startswith("DOMINIUM_SAVE_"):
                info["header"] = line
            if line.startswith("worlddef_hash="):
                info["worlddef_hash"] = line.split("=", 1)[1]
            elif line.startswith("worlddef_len="):
                info["worlddef_len"] = line.split("=", 1)[1]
            elif line.startswith("worlddef_id="):
                info["worlddef_id"] = line.split("=", 1)[1]
            elif line.startswith("schema_version="):
                info["schema_version"] = line.split("=", 1)[1]
    return info


def prepare_root(base, name):
    root = os.path.join(base, name)
    ensure_clean_dir(root)
    os.makedirs(os.path.join(root, "data", "saves"))
    return root


def check_nav_log(path):
    text = read_text(path)
    lines = [line for line in text.splitlines() if "event=client.nav.mode" in line]
    has_refused = any("result=refused" in line and "reason=policy" in line for line in lines)
    has_ok = any("result=ok" in line for line in lines)
    return has_refused, has_ok, lines


def main():
    parser = argparse.ArgumentParser(description="SLICE-0 world flow contracts.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)

    ok = True

    # CLI world creation (built-in templates, zero packs).
    cli_cmd = (
        "new-world template=builtin.minimal_system seed=1 "
        "policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free"
    )
    ok = ok and run_cmd(
        [args.client, cli_cmd],
        expect_contains=["world_create=ok", "template_id=builtin.minimal_system"],
    )[0]

    # TUI world creation.
    tui_root = prepare_root(temp_root, "tui")
    ok = ok and run_cmd(
        [
            args.client,
            "--ui=tui",
            "--ui-script",
            "new-world,create-world",
            "--ui-frames",
            "3",
        ],
        cwd=tui_root,
    )[0]

    # GUI world creation + save (deterministic output expected).
    gui_root_a = prepare_root(temp_root, "gui_a")
    ok = ok and run_cmd(
        [
            args.client,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-script",
            "new-world,create-world,save,exit",
            "--ui-frames",
            "5",
        ],
        cwd=gui_root_a,
    )[0]
    save_path_a = os.path.join(gui_root_a, "data", "saves", "world.save")
    if not os.path.isfile(save_path_a):
        sys.stderr.write("FAIL: GUI save file missing {}\n".format(save_path_a))
        ok = False
    info_a = parse_save_info(save_path_a)
    if info_a["header"] != "DOMINIUM_SAVE_V1":
        sys.stderr.write("FAIL: unexpected save header {}\n".format(info_a["header"]))
        ok = False
    if not info_a["worlddef_id"]:
        sys.stderr.write("FAIL: missing worlddef_id in {}\n".format(save_path_a))
        ok = False

    gui_root_b = prepare_root(temp_root, "gui_b")
    ok = ok and run_cmd(
        [
            args.client,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-script",
            "new-world,create-world,save,exit",
            "--ui-frames",
            "5",
        ],
        cwd=gui_root_b,
    )[0]
    save_path_b = os.path.join(gui_root_b, "data", "saves", "world.save")
    if not os.path.isfile(save_path_b):
        sys.stderr.write("FAIL: GUI save file missing {}\n".format(save_path_b))
        ok = False
    info_b = parse_save_info(save_path_b)
    if info_a["worlddef_hash"] and info_b["worlddef_hash"]:
        if info_a["worlddef_hash"] != info_b["worlddef_hash"]:
            sys.stderr.write("FAIL: worlddef hash mismatch across saves\n")
            sys.stderr.write("A: {}\nB: {}\n".format(info_a["worlddef_hash"], info_b["worlddef_hash"]))
            ok = False

    # Load round-trip (relative path avoids spaces).
    ok = ok and run_cmd(
        [args.client, "load path=data/saves/world.save"],
        expect_contains=["world_load=ok", "worlddef_id=" + info_a["worlddef_id"]],
        cwd=gui_root_a,
    )[0]

    # Replay inspection from save file.
    ok = ok and run_cmd(
        [args.client, "inspect-replay path=data/saves/world.save"],
        expect_contains=["replay_inspect=ok"],
        cwd=gui_root_a,
    )[0]

    # Navigation policy enforcement via UI script.
    nav_root = prepare_root(temp_root, "nav")
    nav_log = os.path.join(nav_root, "nav.log")
    ok = ok and run_cmd(
        [
            args.client,
            "--ui=gui",
            "--headless",
            "--renderer",
            "null",
            "--ui-log",
            nav_log,
            "--ui-script",
            "new-world,create-world,mode-orbit,mode-free,exit",
            "--ui-frames",
            "6",
        ],
        cwd=nav_root,
    )[0]
    has_refused, has_ok, mode_lines = check_nav_log(nav_log)
    if not has_refused or not has_ok:
        sys.stderr.write("FAIL: nav policy events missing in {}\n".format(nav_log))
        for line in mode_lines:
            sys.stderr.write(line + "\n")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
