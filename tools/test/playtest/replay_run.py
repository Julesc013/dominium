import argparse
import json
import os
import sys

from playtest_lib import parse_replay, hash_events


def main():
    parser = argparse.ArgumentParser(description="Run a replay headlessly (event hash only).")
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()

    path = os.path.abspath(args.input)
    try:
        replay = parse_replay(path)
    except Exception as exc:
        sys.stderr.write("replay_run: {}\n".format(exc))
        return 1

    event_hash = hash_events(replay["events"])
    payload = {
        "ok": True,
        "input": path,
        "events": len(replay["events"]),
        "event_hash": event_hash,
        "threads": max(1, int(args.threads)),
        "scenario_id": replay["meta"].get("scenario_id", ""),
        "scenario_version": replay["meta"].get("scenario_version", ""),
        "scenario_variants": replay["meta"].get("scenario_variants", []),
        "lockfile_id": replay["meta"].get("lockfile_id", ""),
        "lockfile_hash": replay["meta"].get("lockfile_hash", ""),
    }

    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("replay_run=ok")
    print("input={}".format(path))
    print("events={}".format(payload["events"]))
    print("event_hash={}".format(event_hash))
    print("threads={}".format(payload["threads"]))
    if payload["scenario_id"]:
        print("scenario_id={}".format(payload["scenario_id"]))
    if payload["scenario_version"]:
        print("scenario_version={}".format(payload["scenario_version"]))
    if payload["scenario_variants"]:
        print("scenario_variants={}".format(",".join(payload["scenario_variants"])))
    if payload["lockfile_id"]:
        print("lockfile_id={}".format(payload["lockfile_id"]))
    if payload["lockfile_hash"]:
        print("lockfile_hash={}".format(payload["lockfile_hash"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
