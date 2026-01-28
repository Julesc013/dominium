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


def prepare_root(base, name, repo_root):
    root = os.path.join(base, name)
    ensure_clean_dir(root)
    ensure_dir(os.path.join(root, "data", "scenarios"))
    ensure_dir(os.path.join(root, "data", "variants"))
    ensure_dir(os.path.join(root, "data", "saves"))
    copy_fixture(repo_root, os.path.join("tests", "fixtures", "playtest", "scenario_minimal.scenario"),
                 os.path.join(root, "data", "scenarios", "default.scenario"))
    copy_fixture(repo_root, os.path.join("tests", "fixtures", "playtest", "variant_swap.variant"),
                 os.path.join(root, "data", "variants", "variant_swap.variant"))
    return root


def main():
    parser = argparse.ArgumentParser(description="Variant swapping replay tests.")
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

    ok = True
    hashes = []
    variant_id_expected = "org.dominium.playtest.variant.swap"

    for name in ("a", "b"):
        root = prepare_root(temp_root, name, repo_root)
        cmd = [
            args.client,
            "batch scenario-load path=data/scenarios/default.scenario variant=data/variants/variant_swap.variant; "
            "replay-save path=data/saves/session.replay",
        ]
        ok_run, _out = run_cmd(cmd, cwd=root)
        if not ok_run:
            sys.stderr.write("FAIL: scenario-load with variant failed in {}\n".format(name))
            ok = False
            continue
        replay_path = os.path.join(root, "data", "saves", "session.replay")
        if not os.path.isfile(replay_path):
            sys.stderr.write("FAIL: replay missing in {}\n".format(name))
            ok = False
            continue
        replay = parse_replay(replay_path)
        if variant_id_expected not in replay["meta"].get("scenario_variants", []):
            sys.stderr.write("FAIL: variant id missing from replay meta\n")
            ok = False
        hashes.append(hash_events(replay["events"]))

    if len(hashes) == 2 and hashes[0] != hashes[1]:
        sys.stderr.write("FAIL: replay event hashes differ across runs\n")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
