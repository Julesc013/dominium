import argparse
import csv
import json
import os
import sys

from playtest_lib import parse_replay, parse_event_line, event_domain


def main():
    parser = argparse.ArgumentParser(description="Render replay timeline (macro vs micro).")
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", choices=["json", "text", "csv"], default="text")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    path = os.path.abspath(args.input)
    try:
        replay = parse_replay(path)
    except Exception as exc:
        sys.stderr.write("replay_timeline: {}\n".format(exc))
        return 1

    events = replay["events"]
    limit = args.limit if args.limit and args.limit > 0 else len(events)
    rows = []
    for line in events[:limit]:
        parsed = parse_event_line(line)
        rows.append(
            {
                "seq": parsed["seq"] or "",
                "domain": event_domain(parsed["name"], parsed["detail_map"]),
                "event": parsed["name"],
                "detail": parsed["detail"],
            }
        )

    if args.format == "json":
        print(json.dumps({"input": path, "rows": rows}, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    if args.format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["seq", "domain", "event", "detail"])
        for row in rows:
            writer.writerow([row["seq"], row["domain"], row["event"], row["detail"]])
        return 0

    print("replay_timeline=ok input={}".format(path))
    for row in rows:
        print("seq={} domain={} event={} detail={}".format(row["seq"], row["domain"], row["event"], row["detail"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
