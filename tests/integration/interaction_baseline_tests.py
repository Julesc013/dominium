import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys


REPLAY_HEADER = "DOMINIUM_REPLAY_V1"


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
    output = result.stdout or ""
    if expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False, output
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                return False, output
    return True, output


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return [line.rstrip("\n\r") for line in handle]


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def require_report(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            payload = json.load(handle)
    except Exception as exc:
        sys.stderr.write("FAIL: compat_report unreadable {} ({})\n".format(path, exc))
        return False
    required = [
        "context",
        "install_id",
        "instance_id",
        "runtime_id",
        "capability_baseline",
        "required_capabilities",
        "provided_capabilities",
        "missing_capabilities",
        "compatibility_mode",
        "refusal_codes",
        "mitigation_hints",
        "timestamp",
        "extensions",
    ]
    ok = True
    for key in required:
        if key not in payload:
            sys.stderr.write("FAIL: compat_report missing {}\n".format(key))
            ok = False
    return ok


def require_events(text, required, label):
    ok = True
    for token in required:
        if token not in text:
            sys.stderr.write("FAIL: missing '{}' in {}\n".format(token, label))
            ok = False
    return ok


def require_save_interactions(path):
    lines = read_lines(path)
    ok = True
    ok = ok and require(any(line == "interactions_begin" for line in lines), "missing interactions_begin")
    ok = ok and require(any(line == "interactions_end" for line in lines), "missing interactions_end")
    ok = ok and require(any(line.startswith("interaction_next_id=") for line in lines),
                        "missing interaction_next_id")
    ok = ok and require(any(line.startswith("interaction_selected_type=") for line in lines),
                        "missing interaction_selected_type")
    ok = ok and require(any(line.startswith("interaction_tool=") for line in lines),
                        "missing interaction_tool")
    ok = ok and require(any(line.startswith("interaction_object") for line in lines),
                        "missing interaction_object")
    ok = ok and require(any(line.startswith("policy.interaction=") for line in lines),
                        "missing policy.interaction")
    return ok


def main():
    parser = argparse.ArgumentParser(description="Interaction baseline I0 integration tests.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    client_path = os.path.abspath(args.client)
    temp_root = os.path.abspath(args.temp_root)
    repo_root = os.path.abspath(args.repo_root)

    ok = True
    ok = ok and require(os.path.isfile(client_path), "client binary missing")
    if not ok:
        return 1

    ensure_clean_dir(temp_root)
    data_root = os.path.join(temp_root, "data")
    saves_dir = os.path.join(data_root, "saves")
    replays_dir = os.path.join(data_root, "replays")
    os.makedirs(saves_dir, exist_ok=True)
    os.makedirs(replays_dir, exist_ok=True)

    env = dict(os.environ)
    env["DOM_DATA_ROOT"] = data_root
    env["DOM_INSTANCE_ROOT"] = data_root
    env["DOM_INSTALL_ROOT"] = repo_root

    ok = ok and run_cmd(
        [client_path, "create-world template=world.template.exploration_baseline seed=42"],
        expect_contains=["world_create=ok", "world_save=ok"],
        cwd=repo_root,
        env=env,
    )[0]

    save_files = [name for name in os.listdir(saves_dir) if name.endswith(".save")]
    ok = ok and require(save_files, "no saves produced")
    if not ok:
        return 1

    base_save = os.path.join(saves_dir, save_files[0])
    base_save_rel = os.path.join("saves", save_files[0])
    save_path = os.path.join(saves_dir, "interaction.save")
    save_rel = os.path.join("saves", "interaction.save")
    save_removed_path = os.path.join(saves_dir, "interaction_removed.save")
    save_removed_rel = os.path.join("saves", "interaction_removed.save")
    replay_path = os.path.join(replays_dir, "interaction.replay")
    replay_rel = os.path.join("replays", "interaction.replay")

    batch_cmd = (
        "batch load path={}; "
        "object-select type=org.dominium.core.interaction.beacon; "
        "place pos=1,0,0; "
        "signal-toggle id=1; "
        "measure id=1; "
        "object-inspect id=1; "
        "save path={}; "
        "remove id=1; "
        "save path={}; "
        "replay-save path={}"
    ).format(base_save_rel, save_rel, save_removed_rel, replay_rel)

    ok = ok and run_cmd(
        [client_path, batch_cmd],
        expect_contains=["world_save=ok", "replay_save=ok"],
        cwd=data_root,
        env=env,
    )[0]

    ok = ok and require(os.path.isfile(save_path), "interaction save missing")
    ok = ok and require(os.path.isfile(save_removed_path), "removed save missing")
    ok = ok and require(os.path.isfile(replay_path), "replay missing")
    if not ok:
        return 1

    save_report = save_path + ".compat_report.json"
    replay_report = replay_path + ".compat_report.json"
    ok = ok and require(os.path.isfile(save_report), "save compat_report missing")
    ok = ok and require(os.path.isfile(replay_report), "replay compat_report missing")
    ok = ok and require_report(save_report)
    ok = ok and require_report(replay_report)

    ok = ok and require_save_interactions(save_path)

    replay_lines = read_lines(replay_path)
    ok = ok and require(replay_lines, "replay file empty")
    if replay_lines:
        ok = ok and require(replay_lines[0].strip() == REPLAY_HEADER, "replay header mismatch")
    ok = ok and require(any("client.interaction.place" in line for line in replay_lines),
                        "replay place event missing")
    ok = ok and require(any("client.interaction.signal" in line for line in replay_lines),
                        "replay signal event missing")
    ok = ok and require(any("client.interaction.measure" in line for line in replay_lines),
                        "replay measure event missing")
    ok = ok and require(any("client.interaction.inspect" in line for line in replay_lines),
                        "replay inspect event missing")
    ok = ok and require(any("client.interaction.remove" in line for line in replay_lines),
                        "replay remove event missing")
    ok = ok and require(not any("expand" in line for line in replay_lines), "expand event seen in replay")
    ok = ok and require(not any("collapse" in line for line in replay_lines), "collapse event seen in replay")

    replay2_path = os.path.join(replays_dir, "interaction_repeat.replay")
    replay2_rel = os.path.join("replays", "interaction_repeat.replay")
    batch_cmd_repeat = (
        "batch load path={}; "
        "object-select type=org.dominium.core.interaction.beacon; "
        "place pos=1,0,0; "
        "signal-toggle id=1; "
        "measure id=1; "
        "object-inspect id=1; "
        "save path={}; "
        "remove id=1; "
        "save path={}; "
        "replay-save path={}"
    ).format(base_save_rel, save_rel, save_removed_rel, replay2_rel)

    ok = ok and run_cmd(
        [client_path, batch_cmd_repeat],
        expect_contains=["replay_save=ok"],
        cwd=data_root,
        env=env,
    )[0]
    ok = ok and require(os.path.isfile(replay2_path), "repeat replay missing")
    if ok:
        ok = ok and require(file_hash(replay_path) == file_hash(replay2_path),
                            "replay hash mismatch (non-deterministic)")

    inspector = os.path.join(repo_root, "tools", "inspect", "interaction_inspector.py")
    ok = ok and run_cmd(
        [sys.executable, inspector, "--save", save_path, "--format", "text"],
        cwd=repo_root,
        env=env,
    )[0]
    ok = ok and run_cmd(
        [sys.executable, inspector, "--replay", replay_path, "--format", "text"],
        cwd=repo_root,
        env=env,
    )[0]
    ok = ok and run_cmd(
        [sys.executable, inspector, "--diff", replay_path, replay2_path, "--format", "text"],
        cwd=repo_root,
        env=env,
    )[0]

    ui_script = (
        "load-world,load-world,interaction-select-beacon,interaction-place,interaction-signal,"
        "interaction-measure,interaction-inspect,interaction-remove,save,replay-save,exit"
    )
    log_gui = os.path.join(temp_root, "client_gui.log")
    log_tui = os.path.join(temp_root, "client_tui.log")

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
            ui_script,
            "--ui-frames",
            "24",
        ],
        cwd=repo_root,
        env=env,
    )[0]
    ok = ok and run_cmd(
        [
            client_path,
            "--ui=tui",
            "--ui-log",
            log_tui,
            "--ui-script",
            ui_script,
            "--ui-frames",
            "24",
        ],
        cwd=repo_root,
        env=env,
    )[0]

    if ok:
        required_events = [
            "client.interaction.select",
            "client.interaction.place",
            "client.interaction.signal",
            "client.interaction.measure",
            "client.interaction.inspect",
            "client.interaction.remove",
            "client.world.save",
            "client.replay.save",
        ]
        with open(log_gui, "r", encoding="utf-8", errors="replace") as handle:
            gui_text = handle.read()
        with open(log_tui, "r", encoding="utf-8", errors="replace") as handle:
            tui_text = handle.read()
        ok = ok and require_events(gui_text, required_events, "GUI log")
        ok = ok and require_events(tui_text, required_events, "TUI log")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
