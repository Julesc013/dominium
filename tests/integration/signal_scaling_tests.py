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


def read_text(path):
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def sha256_file(path):
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


def parse_event_lines(path):
    lines = read_lines(path)
    events = []
    in_events = False
    saw_events = False
    for line in lines:
        if line == REPLAY_HEADER:
            continue
        if line == "events_begin":
            in_events = True
            saw_events = True
            continue
        if line == "events_end":
            in_events = False
            continue
        if (saw_events and in_events) or (not saw_events and line):
            events.append(line)
    return events


def count_token(lines, token):
    return sum(1 for line in lines if token in line)


def count_text_token(text, token):
    return text.count(token)


def load_fixture_config(repo_root):
    cfg_path = os.path.join(repo_root, "tests", "perf", "exploration_fixtures", "fixtures.json")
    with open(cfg_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    parser = argparse.ArgumentParser(description="Signal scaling guard tests.")
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

    cfg = load_fixture_config(repo_root)
    fixtures = cfg.get("fixtures", [])
    ok = ok and require(fixtures, "fixtures list missing")
    if not ok:
        return 1

    metrics_by_fixture = {}
    replay_hashes = []

    for entry in fixtures:
        fixture_id = entry.get("id", "")
        root = entry.get("root", "")
        if not fixture_id or not root:
            ok = ok and require(False, "fixture entry missing id/root")
            continue

        fixture_dir = os.path.join(repo_root, "tests", "perf", "exploration_fixtures", root)
        data_root = os.path.join(temp_root, root, "data")
        saves_dir = os.path.join(data_root, "saves")
        replays_dir = os.path.join(data_root, "replays")
        ensure_clean_dir(data_root)
        os.makedirs(saves_dir, exist_ok=True)
        os.makedirs(replays_dir, exist_ok=True)

        env = dict(os.environ)
        env["DOM_INSTALL_ROOT"] = fixture_dir
        env["DOM_DATA_ROOT"] = data_root
        env["DOM_INSTANCE_ROOT"] = data_root

        ok = ok and run_cmd(
            [client_path, "create-world template=world.template.exploration_baseline seed=42"],
            expect_contains=["world_create=ok", "world_save=ok"],
            cwd=data_root,
            env=env,
        )[0]
        if not ok:
            continue

        save_files = [name for name in os.listdir(saves_dir) if name.endswith(".save")]
        ok = ok and require(save_files, "no saves produced for {}".format(fixture_id))
        if not ok:
            continue

        original_save = os.path.join(saves_dir, save_files[0])
        canonical_save = os.path.join(saves_dir, "world.save")
        shutil.copy2(original_save, canonical_save)

        save_rel = os.path.join("saves", "world.save")
        save2_rel = os.path.join("saves", "signals.save")
        replay_rel = os.path.join("replays", "signals.replay")
        save2_path = os.path.join(saves_dir, "signals.save")
        replay_path = os.path.join(replays_dir, "signals.replay")

        batch_cmd = (
            "batch load path={}; "
            "object-select type=org.dominium.core.signal.button; "
            "place pos=1,0,0; "
            "object-select type=org.dominium.core.signal.lamp; "
            "place pos=2,0,0; "
            "signal-connect from=1 to=2; "
            "signal-toggle id=1; "
            "save path={}; "
            "replay-save path={}"
        ).format(save_rel, save2_rel, replay_rel)

        ok = ok and run_cmd(
            [client_path, batch_cmd],
            expect_contains=["world_save=ok", "replay_save=ok"],
            cwd=data_root,
            env=env,
        )[0]

        ok = ok and require(os.path.isfile(save2_path), "save missing for {}".format(fixture_id))
        ok = ok and require(os.path.isfile(replay_path), "replay missing for {}".format(fixture_id))
        if not ok:
            continue

        events = parse_event_lines(replay_path)
        ok = ok and require(events, "replay events missing for {}".format(fixture_id))
        if not ok:
            continue

        replay_hashes.append(sha256_file(replay_path))

        log_path = os.path.join(temp_root, root, "ui_null.log")
        ui_script = (
            "load-world,load-world,interaction-select-signal-button,interaction-place,"
            "interaction-select-signal-lamp,interaction-place,signal-connect,interaction-signal,exit"
        )
        ok = ok and run_cmd(
            [
                client_path,
                "--ui=gui",
                "--headless",
                "--renderer",
                "null",
                "--ui-log",
                log_path,
                "--ui-script",
                ui_script,
                "--ui-frames",
                "24",
            ],
            cwd=data_root,
            env=env,
        )[0]
        ui_text = read_text(log_path)

        metrics = {
            "signal_connect_events": count_token(events, "client.signal.connect"),
            "signal_route_events": count_token(events, "client.signal.route"),
            "signal_indicate_events": count_token(events, "client.signal.indicate"),
            "signal_toggle_events": count_token(events, "client.signal.toggle"),
            "renderer_draw_calls": count_text_token(ui_text, "renderer.draw") + count_text_token(ui_text, "ui.render"),
            "renderer_traversal_nodes": count_text_token(ui_text, "node_id=") + count_text_token(ui_text, "topology."),
        }
        metrics_by_fixture[fixture_id] = metrics

        ok = ok and require(count_token(events, "expand") == 0,
                            "expand event seen in {}".format(fixture_id))
        ok = ok and require(count_token(events, "collapse") == 0,
                            "collapse event seen in {}".format(fixture_id))

    if not ok:
        return 1

    base_metrics = None
    for fixture_id, metrics in metrics_by_fixture.items():
        if base_metrics is None:
            base_metrics = metrics
            continue
        for key, value in base_metrics.items():
            if metrics.get(key) != value:
                sys.stderr.write("FAIL: metric mismatch {} for {} ({} != {})\n".format(
                    key, fixture_id, metrics.get(key), value))
                ok = False

    if len(set(replay_hashes)) > 1:
        sys.stderr.write("FAIL: replay hash mismatch across fixtures\n")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
