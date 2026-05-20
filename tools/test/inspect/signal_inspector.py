#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return [line.rstrip("\r\n") for line in handle]


def digest(lines):
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def inspect_save(path):
    lines = read_lines(path)
    return {
        "kind": "signal_save",
        "line_count": len(lines),
        "link_count": sum(1 for line in lines if line.startswith("signal_link")),
        "has_signals": "signals_begin" in lines and "signals_end" in lines,
        "sha256": digest(lines),
    }


def inspect_replay(path):
    lines = read_lines(path)
    return {
        "kind": "signal_replay",
        "line_count": len(lines),
        "event_count": sum(1 for line in lines if "client.signal." in line),
        "sha256": digest(lines),
    }


def inspect_diff(left, right):
    left_lines = read_lines(left)
    right_lines = read_lines(right)
    return {
        "kind": "signal_diff",
        "match": digest(left_lines) == digest(right_lines),
        "left_sha256": digest(left_lines),
        "right_sha256": digest(right_lines),
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect deterministic signal test artifacts.")
    parser.add_argument("--save")
    parser.add_argument("--replay")
    parser.add_argument("--diff", nargs=2)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    if args.diff:
        payload = inspect_diff(args.diff[0], args.diff[1])
    elif args.save:
        payload = inspect_save(args.save)
    elif args.replay:
        payload = inspect_replay(args.replay)
    else:
        parser.error("one of --save, --replay, or --diff is required")

    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        for key in sorted(payload):
            print("{}={}".format(key, payload[key]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
