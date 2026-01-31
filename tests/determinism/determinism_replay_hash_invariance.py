import argparse
import hashlib
import json
import os
import sys


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Determinism: replay hash invariance.")
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-DET-REPLAY-HASH"
    fixtures_root = os.path.join(repo_root, "tests", "fixtures", "perf")
    if not os.path.isdir(fixtures_root):
        print("{}: missing perf fixtures".format(invariant_id))
        return 1

    failures = []
    for fixture_name in sorted(os.listdir(fixtures_root)):
        fixture_dir = os.path.join(fixtures_root, fixture_name)
        if not os.path.isdir(fixture_dir):
            continue
        fixture_path = os.path.join(fixture_dir, "fixture.perf.json")
        if not os.path.isfile(fixture_path):
            continue
        fixture = load_json(fixture_path)
        replay_stub = fixture.get("replay_stub")
        if not replay_stub:
            continue
        replay_path = os.path.join(fixture_dir, replay_stub)
        if not os.path.isfile(replay_path):
            failures.append("{}: missing replay stub".format(fixture.get("fixture_id", fixture_name)))
            continue
        expected_hash = sha256_file(replay_path)

        metrics_cfg = fixture.get("metrics", {})
        thread_counts = metrics_cfg.get("thread_counts", [])
        paths = metrics_cfg.get("paths", {})
        for thread in thread_counts:
            path = paths.get(str(thread))
            if not path:
                continue
            metrics_path = os.path.join(fixture_dir, path)
            if not os.path.isfile(metrics_path):
                continue
            data = load_json(metrics_path)
            metrics = data.get("metrics", {})
            actual = metrics.get("replay_hash")
            if actual != expected_hash:
                failures.append("{}: replay hash mismatch on thread {}".format(
                    fixture.get("fixture_id", fixture_name), thread))

    if failures:
        print("{}: replay hash mismatches detected".format(invariant_id))
        for item in failures:
            print(item)
        return 1

    print("replay hash invariance OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
