import argparse
import json
import os
import sys


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_metrics(metrics):
    ignore = {"thread_count", "platform", "run_id", "observed_at"}
    return {k: v for k, v in metrics.items() if k not in ignore}


def main() -> int:
    parser = argparse.ArgumentParser(description="Determinism: thread-count invariance.")
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-DET-THREADCOUNT"
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
        metrics_cfg = fixture.get("metrics", {})
        thread_counts = metrics_cfg.get("thread_counts", [])
        paths = metrics_cfg.get("paths", {})
        metrics_by_thread = {}
        for thread in thread_counts:
            path = paths.get(str(thread))
            if not path:
                continue
            metrics_path = os.path.join(fixture_dir, path)
            if not os.path.isfile(metrics_path):
                continue
            data = load_json(metrics_path)
            metrics_by_thread[thread] = normalize_metrics(data.get("metrics", {}))
        if len(metrics_by_thread) < 2:
            continue
        threads = sorted(metrics_by_thread.keys())
        baseline = metrics_by_thread[threads[0]]
        for thread in threads[1:]:
            if metrics_by_thread[thread] != baseline:
                failures.append("{}: metrics differ between threads {} and {}".format(
                    fixture.get("fixture_id", fixture_name), threads[0], thread))

    if failures:
        print("{}: thread-count invariance failures detected".format(invariant_id))
        for item in failures:
            print(item)
        return 1

    print("thread-count invariance OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
