import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, expect_code=0):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    if result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(result.stdout)
        return False, result.stdout
    return True, result.stdout


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def read_text(path):
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def extract_refusal_lines(text):
    lines = []
    for line in text.splitlines():
        if "result=unavailable" in line or "result=refused" in line or "refusal" in line:
            lines.append(line)
    return lines


def main():
    parser = argparse.ArgumentParser(description="UX-1 presentation parity tests.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--launcher", required=True)
    parser.add_argument("--tools", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "ux")
    preset_path = os.path.join(fixture_root, "accessibility", "accessibility.high_contrast.preset")
    pack_en = os.path.join(fixture_root, "locale_packs", "org.dominium.l10n.en_us")
    pack_zz = os.path.join(fixture_root, "locale_packs", "org.dominium.l10n.zz_test")

    for path in (preset_path, pack_en, pack_zz):
        if not os.path.exists(path):
            sys.stderr.write("FAIL: missing fixture {}\n".format(path))
            return 1

    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)

    ok = True

    # Accessibility presets must not affect event logs.
    log_default = os.path.join(temp_root, "launcher_default.log")
    log_access = os.path.join(temp_root, "launcher_access.log")
    ok = ok and run_cmd([args.launcher, "--ui-log", log_default, "new-world"])[0]
    ok = ok and run_cmd(
        [args.launcher, "--ui-log", log_access, "--accessibility-preset", preset_path, "new-world"]
    )[0]
    if read_text(log_default) != read_text(log_access):
        sys.stderr.write("FAIL: accessibility preset changed launcher event log\n")
        ok = False

    # Localization swap must not affect event logs.
    log_en = os.path.join(temp_root, "launcher_locale_en.log")
    log_zz = os.path.join(temp_root, "launcher_locale_zz.log")
    ok = ok and run_cmd(
        [
            args.launcher,
            "--ui-log",
            log_en,
            "--locale-pack",
            pack_en,
            "--locale",
            "en_US",
            "new-world",
        ]
    )[0]
    ok = ok and run_cmd(
        [
            args.launcher,
            "--ui-log",
            log_zz,
            "--locale-pack",
            pack_zz,
            "--locale",
            "zz_TEST",
            "new-world",
        ]
    )[0]
    if read_text(log_en) != read_text(log_zz):
        sys.stderr.write("FAIL: localization swap changed launcher event log\n")
        ok = False

    # Refusal parity across CLI/TUI/GUI.
    log_cli = os.path.join(temp_root, "launcher_refusal_cli.log")
    log_gui = os.path.join(temp_root, "launcher_refusal_gui.log")
    log_tui = os.path.join(temp_root, "launcher_refusal_tui.log")
    ok = ok and run_cmd([args.launcher, "--ui-log", log_cli, "load-world"])[0]
    ok = ok and run_cmd(
        [
            args.launcher,
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
        ]
    )[0]
    ok = ok and run_cmd(
        [
            args.launcher,
            "--ui=tui",
            "--ui-log",
            log_tui,
            "--ui-script",
            "load-world",
            "--ui-frames",
            "2",
        ]
    )[0]
    cli_refusal = extract_refusal_lines(read_text(log_cli))
    gui_refusal = extract_refusal_lines(read_text(log_gui))
    tui_refusal = extract_refusal_lines(read_text(log_tui))
    if cli_refusal != gui_refusal or cli_refusal != tui_refusal:
        sys.stderr.write("FAIL: refusal lines differ across CLI/TUI/GUI\n")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
