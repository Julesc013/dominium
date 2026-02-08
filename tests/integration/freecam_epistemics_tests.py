import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, cwd=None, env=None, expect_code=0):
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


def parse_status_block(text):
    data = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return [line.rstrip("\n\r") for line in handle]


def main():
    parser = argparse.ArgumentParser(description="Freecam epistemic integration checks.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    client_path = os.path.abspath(args.client)
    temp_root = os.path.abspath(args.temp_root)
    repo_root = os.path.abspath(args.repo_root)
    data_root = os.path.join(temp_root, "data")
    saves_dir = os.path.join(data_root, "saves")
    replays_dir = os.path.join(data_root, "replays")

    ok = True
    ok = ok and require(os.path.isfile(client_path), "client binary missing")
    if not ok:
        return 1

    ensure_clean_dir(data_root)
    os.makedirs(saves_dir, exist_ok=True)
    os.makedirs(replays_dir, exist_ok=True)

    env = dict(os.environ)
    env["DOM_DATA_ROOT"] = data_root
    env["DOM_INSTANCE_ROOT"] = data_root
    env["DOM_INSTALL_ROOT"] = repo_root

    ok, out = run_cmd(
        [client_path, "create-world template=world.template.exploration_baseline seed=42 policy.debug="],
        cwd=repo_root,
        env=env,
    )
    if not ok:
        sys.stderr.write(out)
        return 1

    save_files = [name for name in os.listdir(saves_dir) if name.endswith(".save")]
    ok = require(bool(save_files), "create-world produced no save")
    if not ok:
        return 1

    canonical_save = os.path.join(saves_dir, "world.save")
    shutil.copy2(os.path.join(saves_dir, save_files[0]), canonical_save)
    save_rel = os.path.join("saves", "world.save")
    replay_rel = os.path.join("replays", "freecam.replay")
    replay_path = os.path.join(replays_dir, "freecam.replay")

    ok, baseline_out = run_cmd(
        [client_path, "batch load path={}; where".format(save_rel)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "baseline where command failed")
    if not ok:
        return 1
    baseline = parse_status_block(baseline_out)
    baseline_pos = baseline.get("position", "")
    ok = ok and require(bool(baseline_pos), "baseline position missing")
    if not ok:
        return 1

    ok, pose_out = run_cmd(
        [client_path, "batch load path={}; camera.set_mode embodied; camera.set_pose pos=9,8,7; where".format(save_rel)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "camera.set_pose command failed")
    if not ok:
        return 1
    pose_state = parse_status_block(pose_out)
    ok = ok and require(
        pose_state.get("position", "") == baseline_pos,
        "camera.set_pose changed authoritative position",
    )
    if not ok:
        return 1

    ok, memory_out_a = run_cmd(
        [client_path, "batch load path={}; camera.set_mode memory; where; refusal".format(save_rel)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "memory freecam command failed")
    if not ok:
        return 1
    ok, memory_out_b = run_cmd(
        [client_path, "batch load path={}; camera.set_mode memory; where; refusal".format(save_rel)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "memory freecam repeat command failed")
    ok = ok and require(memory_out_a == memory_out_b, "memory freecam output is non-deterministic")
    if not ok:
        return 1

    ok, observer_out = run_cmd(
        [client_path, "batch load path={}; camera.set_mode observer; refusal; where".format(save_rel)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "observer freecam command failed")
    ok = ok and require("refusal_code=WD-REFUSAL-SCHEMA" in observer_out, "observer freecam was not refused")
    ok = ok and require(
        "CAMERA_REFUSE_ENTITLEMENT" in observer_out,
        "observer freecam refusal detail missing entitlement code",
    )
    ok = ok and require("camera=camera.first_person" in observer_out, "observer refusal changed active camera")
    if not ok:
        return 1

    ok, replay_out = run_cmd(
        [client_path, "batch load path={}; camera.set_mode embodied; camera-next; replay-save path={}".format(save_rel, replay_rel)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "replay-save command failed")
    ok = ok and require(os.path.isfile(replay_path), "replay file missing")
    if not ok:
        return 1

    replay_lines = read_lines(replay_path)
    replay_text = "\n".join(replay_lines)
    ok = ok and require("client.nav.camera" in replay_text, "camera event missing from replay stream")
    for forbidden in ("truth_snapshot_stream", "authoritative_world_state", "hidden_truth_cache"):
        ok = ok and require(forbidden not in replay_text, "forbidden truth token in replay: {}".format(forbidden))
    if not ok:
        return 1

    print("freecam_epistemics=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
