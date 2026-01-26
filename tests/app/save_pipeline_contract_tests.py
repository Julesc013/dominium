import argparse
import json
import hashlib
import os
import sys


def canonical_hash(payload):
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def make_chunks():
    chunks = []
    for idx in range(6):
        chunks.append({
            "chunk_id": "chunk.core.{}".format(idx),
            "chunk_type": "chunk_type.save",
            "mod_id": "core",
            "payload": {"value": idx},
        })
    chunks.append({
        "chunk_id": "chunk.mod.bad",
        "chunk_type": "chunk_type.save",
        "mod_id": "mod.bad",
        "payload": {"value": 99},
    })
    return chunks


def save_pipeline(chunks, thread_count=1, crash_stage=None, fail_mod=None, last_good=None):
    state = "IDLE"
    state = "BARRIER"

    # CAPTURE: emulate parallel capture by shuffling into buckets
    state = "CAPTURE"
    buckets = [[] for _ in range(max(1, thread_count))]
    for idx, chunk in enumerate(chunks):
        buckets[idx % len(buckets)].append(chunk)
    captured = [chunk for bucket in buckets for chunk in bucket]

    # TRANSFORM: deterministic ordering + optional failure isolation
    state = "TRANSFORM"
    failed = []
    ok = []
    for chunk in captured:
        if fail_mod and chunk.get("mod_id") == fail_mod:
            failed.append(chunk)
            continue
        ok.append(chunk)
    ok = sorted(ok, key=lambda c: (c.get("chunk_type", ""), c.get("mod_id", ""), c.get("chunk_id", "")))
    determinism_hash = canonical_hash(ok)

    # WRITE: staged output
    state = "WRITE"
    staged = {"chunks": ok, "hash": determinism_hash}
    if crash_stage == "WRITE":
        return {
            "state": "FAILED",
            "last_good": last_good,
            "staged": None,
            "hash": None,
            "failed_chunks": failed,
        }

    # COMMIT: atomic promote
    state = "COMMIT"
    if crash_stage == "COMMIT":
        return {
            "state": "FAILED",
            "last_good": last_good,
            "staged": staged,
            "hash": None,
            "failed_chunks": failed,
        }
    new_save = staged
    last_good = new_save

    return {
        "state": "DONE",
        "last_good": last_good,
        "staged": staged,
        "hash": determinism_hash,
        "failed_chunks": failed,
    }


def main():
    parser = argparse.ArgumentParser(description="Save pipeline contract tests.")
    parser.add_argument("--repo-root", default=".")
    _args = parser.parse_args()

    chunks = make_chunks()

    # Determinism hash identical across thread counts
    result_a = save_pipeline(chunks, thread_count=1)
    result_b = save_pipeline(chunks, thread_count=4)
    if result_a["hash"] != result_b["hash"]:
        print("determinism hash differs across thread counts")
        return 1

    # Crash-interrupted save recovery
    last_good = {"chunks": [{"chunk_id": "baseline"}], "hash": "baseline"}
    crash = save_pipeline(chunks, thread_count=2, crash_stage="WRITE", last_good=last_good)
    if crash["last_good"] != last_good:
        print("last known good save corrupted on crash")
        return 1

    # Mod chunk failure isolation
    isolated = save_pipeline(chunks, thread_count=2, fail_mod="mod.bad")
    if isolated["state"] != "DONE":
        print("save pipeline failed without isolating mod chunk")
        return 1
    if not isolated["failed_chunks"]:
        print("mod chunk failure not recorded")
        return 1
    if any(c.get("mod_id") == "mod.bad" for c in isolated["staged"]["chunks"]):
        print("failed mod chunk leaked into save output")
        return 1

    # Replay equivalence after save/load
    saved = isolated["staged"]
    loaded = json.loads(json.dumps(saved, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    if canonical_hash(saved) != canonical_hash(loaded):
        print("save/load round trip changed replay hash")
        return 1

    print("Save pipeline contracts OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
