import argparse
import hashlib
import json
import os
import pathlib
import sys


REQUIRED_METRICS = [
    "active_tier2_domains",
    "active_tier1_domains",
    "processes_per_tick",
    "macro_events_per_tick",
    "collapse_expand_ops_per_tick",
    "agent_planning_steps_per_tick",
    "macro_time_steps_per_tick",
    "snapshot_ops_per_tick",
    "serialization_ops_per_tick",
    "refusal_counts_total",
    "refusal_counts_budget",
    "refusal_counts_capability",
    "refusal_counts_validation",
    "refusal_counts_unknown",
    "memory_peak_kb",
    "memory_plateau_kb",
    "cross_shard_msgs_per_tick",
    "cross_shard_bytes_per_tick",
    "event_hash",
    "metrics_hash",
    "replay_hash",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_kv_file(path, header):
    data = {}
    with open(path, "r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle.readlines()]
    lines = [line for line in lines if line]
    if not lines or lines[0] != header:
        raise RuntimeError("Missing header {} in {}".format(header, path))
    for line in lines[1:]:
        if line.endswith("_begin") or line.endswith("_end"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def normalize_metrics(metrics):
    ignore = {"thread_count", "platform", "run_id", "observed_at"}
    return {k: v for k, v in metrics.items() if k not in ignore}


def main():
    parser = argparse.ArgumentParser(description="PERF-1 fixture contracts.")
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    repo_root = pathlib.Path(args.repo_root)
    fixture_root = repo_root / "tests" / "fixtures" / "perf"
    guard_path = repo_root / "tests" / "perf" / "perf_guards.json"

    if not fixture_root.is_dir():
        print("FAIL: missing perf fixtures root {}".format(fixture_root))
        return 1
    if not guard_path.is_file():
        print("FAIL: missing perf guard file {}".format(guard_path))
        return 1

    guards = load_json(guard_path).get("guards", [])
    guard_map = {g["id"]: g for g in guards}

    expected = {
        "galaxy_scale_civ": "perf.galaxy_scale_civ",
        "local_density_extreme": "perf.local_density_extreme",
        "deep_history": "perf.deep_history",
        "thrash_attempt": "perf.thrash_attempt",
        "mmo_style_load": "perf.mmo_style_load",
    }

    ok = True

    for folder, fixture_id in expected.items():
        root = fixture_root / folder
        if not root.is_dir():
            print("FAIL: missing fixture folder {}".format(root))
            ok = False
            continue
        fixture_path = root / "fixture.perf.json"
        if not fixture_path.is_file():
            print("FAIL: missing fixture.perf.json in {}".format(root))
            ok = False
            continue
        fixture = load_json(fixture_path)
        if fixture.get("fixture_id") != fixture_id:
            print("FAIL: fixture_id mismatch in {}".format(fixture_path))
            ok = False
        scenario_path = root / fixture.get("scenario_path", "")
        variant_path = root / fixture.get("variant_path", "")
        replay_path = root / fixture.get("replay_stub", "")
        if not scenario_path.is_file():
            print("FAIL: missing scenario {}".format(scenario_path))
            ok = False
        if not variant_path.is_file():
            print("FAIL: missing variant {}".format(variant_path))
            ok = False
        if not replay_path.is_file():
            print("FAIL: missing replay stub {}".format(replay_path))
            ok = False

        try:
            scenario = parse_kv_file(scenario_path, "DOMINIUM_SCENARIO_V1")
            for key in ("scenario_id", "scenario_version", "world_template", "world_seed"):
                if key not in scenario:
                    raise RuntimeError("missing {}".format(key))
        except Exception as exc:
            print("FAIL: scenario parse {} ({})".format(scenario_path, exc))
            ok = False

        try:
            variant = parse_kv_file(variant_path, "DOMINIUM_VARIANT_V1")
            for key in ("variant_id", "variant_version"):
                if key not in variant:
                    raise RuntimeError("missing {}".format(key))
        except Exception as exc:
            print("FAIL: variant parse {} ({})".format(variant_path, exc))
            ok = False

        limits = fixture.get("limits", {})
        minimums = fixture.get("minimums", {})
        guards_used = fixture.get("guards", [])
        tolerance_kb = fixture.get("memory_plateau_tolerance_kb", 0)
        if not isinstance(tolerance_kb, int) or tolerance_kb <= 0:
            print("FAIL: missing memory_plateau_tolerance_kb in {}".format(fixture_path))
            ok = False

        for guard_id in guards_used:
            if guard_id not in guard_map:
                print("FAIL: unknown guard {} in {}".format(guard_id, fixture_path))
                ok = False

        metrics_cfg = fixture.get("metrics", {})
        paths = metrics_cfg.get("paths", {})
        thread_counts = metrics_cfg.get("thread_counts", [])
        for thread in thread_counts:
            key = str(thread)
            if key not in paths:
                print("FAIL: missing metrics path for thread {} in {}".format(thread, fixture_path))
                ok = False

        metrics_by_thread = {}
        for thread in thread_counts:
            path = root / paths[str(thread)]
            if not path.is_file():
                print("FAIL: missing metrics file {}".format(path))
                ok = False
                continue
            data = load_json(path)
            metrics_by_thread[thread] = data

            metrics = data.get("metrics", {})
            for key in REQUIRED_METRICS:
                if key not in metrics:
                    print("FAIL: missing metric {} in {}".format(key, path))
                    ok = False
            if not data.get("collapse_expand_invariants_ok", False):
                print("FAIL: collapse/expand invariants not ok in {}".format(path))
                ok = False

            if replay_path.is_file():
                expected_hash = sha256_file(replay_path)
                if metrics.get("replay_hash") != expected_hash:
                    print("FAIL: replay hash mismatch in {}".format(path))
                    ok = False

            peak = metrics.get("memory_peak_kb")
            plateau = metrics.get("memory_plateau_kb")
            if isinstance(peak, int) and isinstance(plateau, int):
                if plateau > peak or (peak - plateau) > tolerance_kb:
                    print("FAIL: memory plateau drift in {}".format(path))
                    ok = False

            for key, max_value in limits.items():
                if key not in metrics:
                    print("FAIL: limit metric {} missing in {}".format(key, path))
                    ok = False
                    continue
                if metrics[key] > max_value:
                    print("FAIL: {} exceeded in {} ({} > {})".format(key, path, metrics[key], max_value))
                    ok = False

            for key, min_value in minimums.items():
                if key not in metrics:
                    print("FAIL: minimum metric {} missing in {}".format(key, path))
                    ok = False
                    continue
                if metrics[key] < min_value:
                    print("FAIL: {} below minimum in {} ({} < {})".format(key, path, metrics[key], min_value))
                    ok = False

            for guard_id in guards_used:
                guard = guard_map.get(guard_id)
                if not guard:
                    continue
                metric = guard["metric"]
                max_value = guard["max"]
                if metric not in metrics:
                    print("FAIL: guard metric {} missing in {}".format(metric, path))
                    ok = False
                    continue
                if metrics[metric] > max_value:
                    print("FAIL: guard {} exceeded in {} ({} > {})".format(
                        guard_id, path, metrics[metric], max_value))
                    ok = False

        if 1 in metrics_by_thread and 4 in metrics_by_thread:
            m1 = normalize_metrics(metrics_by_thread[1])
            m4 = normalize_metrics(metrics_by_thread[4])
            if m1 != m4:
                print("FAIL: metrics differ across threads for {}".format(fixture_id))
                ok = False

        if fixture.get("expected_refusal_budget_min") is not None:
            expected_min = fixture.get("expected_refusal_budget_min", 0)
            for thread in thread_counts:
                metrics = metrics_by_thread.get(thread, {}).get("metrics", {})
                if metrics.get("refusal_counts_budget", 0) < expected_min:
                    print("FAIL: refusal budget below min in {} thread {}".format(fixture_id, thread))
                    ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
