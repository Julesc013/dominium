import argparse
import json
import os
import shutil
import subprocess
import sys


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def copy_fixture(repo_root, rel_path, dest_path):
    src = os.path.join(repo_root, rel_path)
    with open(src, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    ensure_dir(os.path.dirname(dest_path))
    with open(dest_path, "w", encoding="utf-8", errors="replace") as handle:
        handle.write(text)


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


def run_replay_run(python_exe, script, replay_path, threads):
    cmd = [python_exe, script, "--input", replay_path, "--format", "json", "--threads", str(threads)]
    output = subprocess.check_output(cmd)
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Replay regression hashing tests.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)

    root = os.path.join(temp_root, "run")
    ensure_clean_dir(root)
    ensure_dir(os.path.join(root, "data", "scenarios"))
    ensure_dir(os.path.join(root, "data", "saves"))
    copy_fixture(repo_root, os.path.join("tests", "fixtures", "playtest", "scenario_minimal.scenario"),
                 os.path.join(root, "data", "scenarios", "default.scenario"))

    cli_cmd = [
        args.client,
        "batch scenario-load path=data/scenarios/default.scenario; replay-save path=data/saves/session.replay",
    ]
    ok_run, _out = run_cmd(cli_cmd, cwd=root)
    if not ok_run:
        sys.stderr.write("FAIL: replay generation failed\n")
        return 1

    replay_path = os.path.join(root, "data", "saves", "session.replay")
    if not os.path.isfile(replay_path):
        sys.stderr.write("FAIL: replay missing\n")
        return 1

    script = os.path.join(repo_root, "tools", "playtest", "replay_run.py")
    run_a = run_replay_run(sys.executable, script, replay_path, 1)
    run_b = run_replay_run(sys.executable, script, replay_path, 4)

    if run_a.get("event_hash") != run_b.get("event_hash"):
        sys.stderr.write("FAIL: replay hash mismatch across thread counts\n")
        sys.stderr.write("A: {}\nB: {}\n".format(run_a.get("event_hash"), run_b.get("event_hash")))
        return 1

    print("replay regression OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
