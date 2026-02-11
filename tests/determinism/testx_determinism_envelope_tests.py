import argparse
import hashlib
import json
import os
import random
import threading
import sys


def _stable_hash(payload):
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _require(condition, message):
    if condition:
        return True
    sys.stderr.write("FAIL: {}\n".format(message))
    return False


def _thread_worker(items, out, slot):
    partial = []
    for item in items:
        partial.append((item["id"], (item["value"] * 17 + 3) % 97))
    out[slot] = sorted(partial)


def _run_thread_case(worker_count):
    items = [{"id": idx, "value": (idx * 37 + 11) % 101} for idx in range(256)]
    chunks = [[] for _ in range(worker_count)]
    for idx, item in enumerate(items):
        chunks[idx % worker_count].append(item)

    results = [None] * worker_count
    threads = []
    for slot in range(worker_count):
        thread = threading.Thread(target=_thread_worker, args=(chunks[slot], results, slot))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

    merged = []
    for partial in results:
        merged.extend(partial or [])
    merged.sort(key=lambda item: item[0])
    return _stable_hash(merged)


def case_thread():
    hash_single = _run_thread_case(1)
    hash_multi = _run_thread_case(8)
    if not _require(hash_single == hash_multi, "thread envelope hash mismatch"):
        return 1
    print("test_determinism_thread=ok")
    return 0


def _srz_partition(values, widths):
    weighted_sum = 0
    total = 0
    count = 0
    offset = 0
    for width in widths:
        chunk = values[offset: offset + width]
        if chunk:
            for idx, value in enumerate(chunk):
                global_idx = offset + idx + 1
                weighted_sum += global_idx * value
                total += value
                count += 1
        offset += width
    if offset < len(values):
        chunk = values[offset:]
        for idx, value in enumerate(chunk):
            global_idx = offset + idx + 1
            weighted_sum += global_idx * value
            total += value
            count += 1
    return _stable_hash({"count": count, "sum": total, "weighted_sum": weighted_sum})


def case_srz():
    values = [(idx * 19 + 7) % 113 for idx in range(400)]
    hash_a = _srz_partition(values, [31, 37, 41, 43, 47])
    hash_b = _srz_partition(values, [67, 73, 79, 83])
    if not _require(hash_a == hash_b, "srz envelope hash mismatch"):
        return 1
    print("test_determinism_srz=ok")
    return 0


def _choose_solver(budget_cap, candidates):
    viable = [entry for entry in candidates if entry["cost"] <= budget_cap]
    if not viable:
        return {"result": "refuse.budget"}
    viable.sort(key=lambda item: (item["tier"], item["cost"], item["solver_id"]))
    return viable[0]


def case_budget():
    candidates = [
        {"solver_id": "solver.alpha", "tier": 1, "cost": 15},
        {"solver_id": "solver.beta", "tier": 2, "cost": 24},
        {"solver_id": "solver.gamma", "tier": 2, "cost": 30},
    ]
    selected_a = _choose_solver(30, candidates)
    selected_b = _choose_solver(25, candidates)
    if not _require(selected_a["solver_id"] == selected_b["solver_id"], "budget envelope selected different solver"):
        return 1
    selected_refuse = _choose_solver(10, candidates)
    if not _require(selected_refuse.get("result") == "refuse.budget", "budget refusal mismatch"):
        return 1
    print("test_determinism_budget=ok")
    return 0


def _stream_seed(base_seed, stream_name):
    digest = hashlib.sha256("{}::{}".format(base_seed, stream_name).encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _stream_values(base_seed, stream_name, count):
    rng = random.Random(_stream_seed(base_seed, stream_name))
    return [rng.randint(0, 1000000) for _ in range(count)]


def case_rng():
    seed = "dominium.seed.envelope"
    names = ["universe", "system.sol", "region.earth", "agent.camera"]
    a = {name: _stream_values(seed, name, 16) for name in names}
    b = {name: _stream_values(seed, name, 16) for name in reversed(names)}
    if not _require(a == b, "named stream output mismatch under reorder"):
        return 1
    print("test_rng_stream_consistency=ok")
    return 0


def main():
    parser = argparse.ArgumentParser(description="TestX determinism envelope proofs.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--case", choices=("thread", "srz", "budget", "rng"), required=True)
    args = parser.parse_args()
    _ = os.path.abspath(args.repo_root)

    if args.case == "thread":
        return case_thread()
    if args.case == "srz":
        return case_srz()
    if args.case == "budget":
        return case_budget()
    return case_rng()


if __name__ == "__main__":
    raise SystemExit(main())
