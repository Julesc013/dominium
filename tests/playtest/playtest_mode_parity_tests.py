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


def copy_fixture(repo_root, rel_path, dest_path):
    src = os.path.join(repo_root, rel_path)
    with open(src, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    ensure_dir(os.path.dirname(dest_path))
    with open(dest_path, "w", encoding="utf-8", errors="replace") as handle:
        handle.write(text)


def prepare_root(base, name, repo_root, include_variant):
    root = os.path.join(base, name)
    ensure_clean_dir(root)
    ensure_dir(os.path.join(root, "data", "scenarios"))
    ensure_dir(os.path.join(root, "data", "saves"))
    if include_variant:
        ensure_dir(os.path.join(root, "data", "variants"))
    copy_fixture(repo_root, os.path.join("tests", "fixtures", "playtest", "scenario_minimal.scenario"),
                 os.path.join(root, "data", "scenarios", "default.scenario"))
    if include_variant:
        copy_fixture(repo_root,
                     os.path.join("tests", "fixtures", "playtest", "variant_server_authoritative.variant"),
                     os.path.join(root, "data", "variants", "server_authoritative.variant"))
    return root


def main():
    parser = argparse.ArgumentParser(description="Mode parity tests (SP vs server-authoritative).")
    parser.add_argument("--client", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)

    sys.path.insert(0, os.path.join(repo_root, "tools", "playtest"))
    try:
        from playtest_lib import parse_replay, hash_events
    except Exception:
        sys.stderr.write("FAIL: unable to import playtest_lib\n")
        return 1

    sp_root = prepare_root(temp_root, "singleplayer", repo_root, include_variant=False)
    sp_cmd = [
        args.client,
        "batch scenario-load path=data/scenarios/default.scenario; replay-save path=data/saves/session.replay",
    ]
    ok_sp, _sp_out = run_cmd(sp_cmd, cwd=sp_root)
    if not ok_sp:
        sys.stderr.write("FAIL: singleplayer replay generation failed\n")
        return 1

    server_root = prepare_root(temp_root, "server_auth", repo_root, include_variant=True)
    server_cmd = [
        args.client,
        "batch scenario-load path=data/scenarios/default.scenario "
        "variant=data/variants/server_authoritative.variant; replay-save path=data/saves/session.replay",
    ]
    ok_srv, _srv_out = run_cmd(server_cmd, cwd=server_root)
    if not ok_srv:
        sys.stderr.write("FAIL: server-authoritative replay generation failed\n")
        return 1

    sp_replay = os.path.join(sp_root, "data", "saves", "session.replay")
    srv_replay = os.path.join(server_root, "data", "saves", "session.replay")
    if not os.path.isfile(sp_replay) or not os.path.isfile(srv_replay):
        sys.stderr.write("FAIL: replay missing for parity test\n")
        return 1

    sp_hash = hash_events(parse_replay(sp_replay)["events"])
    srv_hash = hash_events(parse_replay(srv_replay)["events"])
    if sp_hash != srv_hash:
        sys.stderr.write("FAIL: event stream mismatch between modes\n")
        sys.stderr.write("SP: {}\nSRV: {}\n".format(sp_hash, srv_hash))
        return 1

    print("mode parity OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
