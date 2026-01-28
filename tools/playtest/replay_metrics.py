import argparse
import json
import os
import sys

from playtest_lib import parse_replay, parse_event_line, event_domain, hash_events


def main():
    parser = argparse.ArgumentParser(description="Compute replay metrics from event stream.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    path = os.path.abspath(args.input)
    try:
        replay = parse_replay(path)
    except Exception as exc:
        sys.stderr.write("replay_metrics: {}\n".format(exc))
        return 1

    events = replay["events"]
    counts = {}
    refusal_codes = {}
    domains = {"macro": 0, "micro": 0, "meso": 0, "unknown": 0}
    refusal_total = 0
    process_total = 0
    budget_total = 0

    for line in events:
        parsed = parse_event_line(line)
        name = parsed["name"] or "unknown"
        counts[name] = counts.get(name, 0) + 1

        domain = event_domain(name, parsed["detail_map"])
        domains[domain] = domains.get(domain, 0) + 1

        if "process" in name:
            process_total += 1

        if parsed["detail_map"].get("result") == "refused" or "refusal" in name:
            refusal_total += 1
            code = parsed["detail_map"].get("code") or parsed["detail_map"].get("refusal")
            if code:
                refusal_codes[code] = refusal_codes.get(code, 0) + 1

        if "budget" in name or "budget" in parsed["detail_map"]:
            budget_total += 1

    payload = {
        "ok": True,
        "input": path,
        "events_total": len(events),
        "event_hash": hash_events(events),
        "events_by_name": counts,
        "domains": domains,
        "process_events": process_total,
        "refusal_events": refusal_total,
        "refusal_codes": refusal_codes,
        "budget_events": budget_total,
    }

    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0

    print("replay_metrics=ok")
    print("input={}".format(path))
    print("events_total={}".format(payload["events_total"]))
    print("event_hash={}".format(payload["event_hash"]))
    print("process_events={}".format(payload["process_events"]))
    print("refusal_events={}".format(payload["refusal_events"]))
    print("budget_events={}".format(payload["budget_events"]))
    for key in ("macro", "micro", "meso", "unknown"):
        print("domain_{}={}".format(key, payload["domains"].get(key, 0)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
