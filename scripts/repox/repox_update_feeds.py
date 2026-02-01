#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime


CHANNELS = ["stable", "beta", "nightly", "pinned"]


def now_timestamp(deterministic: bool) -> str:
    if deterministic or os.environ.get("REPOX_DETERMINISTIC") == "1":
        return "2000-01-01T00:00:00Z"
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def load_feed(path: str):
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        try:
            return json.load(handle)
        except ValueError:
            return None


def write_feed(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def normalize_feed(channel: str, payload: dict, generated_at: str) -> dict:
    entries = payload.get("entries") if isinstance(payload, dict) else None
    rollbacks = payload.get("rollbacks") if isinstance(payload, dict) else None
    return {
        "schema_version": 1,
        "channel": channel,
        "generated_at": generated_at,
        "entries": entries if isinstance(entries, list) else [],
        "rollbacks": rollbacks if isinstance(rollbacks, list) else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RepoX update feed normalizer.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--channel", action="append", default=[])
    parser.add_argument("--deterministic", action="store_true")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    channels = args.channel or CHANNELS
    generated_at = now_timestamp(args.deterministic)

    for channel in channels:
        feed_path = os.path.join(repo_root, "updates", "{}.json".format(channel))
        payload = load_feed(feed_path) or {}
        normalized = normalize_feed(channel, payload, generated_at)
        write_feed(feed_path, normalized)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
