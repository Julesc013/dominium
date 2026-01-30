import argparse
import json
import os
import sys


REPLAY_HEADER = "DOMINIUM_REPLAY_V1"


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return [line.rstrip("\n\r") for line in handle]


def parse_kv_tokens(text):
    tokens = {}
    for token in text.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if key:
            tokens[key] = value
    return tokens


def parse_pos(value):
    if not value:
        return None
    parts = value.split(",")
    if len(parts) != 3:
        return value
    try:
        return [float(p) for p in parts]
    except ValueError:
        return value


def parse_interaction_object(line):
    raw = line.strip()
    if raw.startswith("interaction_object"):
        raw = raw[len("interaction_object"):].strip()
    tokens = parse_kv_tokens(raw)
    obj = {}
    if "id" in tokens:
        try:
            obj["id"] = int(tokens["id"])
        except ValueError:
            obj["id"] = tokens["id"]
    if "type" in tokens:
        obj["type_id"] = tokens["type"]
    if "pos" in tokens:
        obj["pos"] = parse_pos(tokens["pos"])
    if "signal" in tokens:
        try:
            obj["signal"] = int(tokens["signal"])
        except ValueError:
            obj["signal"] = tokens["signal"]
    if "tick" in tokens:
        try:
            obj["signal_tick"] = int(tokens["tick"])
        except ValueError:
            obj["signal_tick"] = tokens["tick"]
    if "provenance" in tokens:
        obj["provenance_id"] = tokens["provenance"]
    return obj


def parse_signal_link(line):
    raw = line.strip()
    if raw.startswith("signal_link"):
        raw = raw[len("signal_link"):].strip()
    elif raw.startswith("signal_preview"):
        raw = raw[len("signal_preview"):].strip()
    tokens = parse_kv_tokens(raw)
    link = {}
    if "from" in tokens:
        try:
            link["from"] = int(tokens["from"])
        except ValueError:
            link["from"] = tokens["from"]
    if "to" in tokens:
        try:
            link["to"] = int(tokens["to"])
        except ValueError:
            link["to"] = tokens["to"]
    if "mode" in tokens:
        link["mode"] = tokens["mode"]
    if "threshold" in tokens:
        try:
            link["threshold"] = int(tokens["threshold"])
        except ValueError:
            link["threshold"] = tokens["threshold"]
    return link


def parse_save(path):
    lines = read_lines(path)
    data = {
        "objects": [],
        "links": [],
        "preview": None,
        "next_tick": None,
    }
    in_interactions = False
    in_signals = False
    for line in lines:
        if line == "interactions_begin":
            in_interactions = True
            continue
        if line == "interactions_end":
            in_interactions = False
            continue
        if line == "signals_begin":
            in_signals = True
            continue
        if line == "signals_end":
            in_signals = False
            continue
        if in_interactions and line.startswith("interaction_object"):
            data["objects"].append(parse_interaction_object(line))
            continue
        if not in_signals:
            continue
        if line.startswith("signal_next_tick="):
            value = line.split("=", 1)[1]
            try:
                data["next_tick"] = int(value)
            except ValueError:
                data["next_tick"] = value
        elif line.startswith("signal_preview"):
            data["preview"] = parse_signal_link(line)
        elif line.startswith("signal_link"):
            data["links"].append(parse_signal_link(line))
    return data


def extract_event_name(line):
    markers = ["client.signal.", "client.interaction.signal"]
    for marker in markers:
        idx = line.find(marker)
        if idx == -1:
            continue
        end = idx + len(marker)
        while end < len(line) and (line[end].isalnum() or line[end] in "._-"):
            end += 1
        return line[idx:end]
    return None


def parse_replay(path):
    lines = read_lines(path)
    events = []
    for line in lines:
        if not line or line == REPLAY_HEADER:
            continue
        name = extract_event_name(line)
        if name:
            events.append({"name": name, "line": line})
    counts = {}
    for event in events:
        counts[event["name"]] = counts.get(event["name"], 0) + 1
    return {"events": events, "counts": counts}


def diff_replays(left_path, right_path):
    left = parse_replay(left_path)
    right = parse_replay(right_path)
    left_counts = left["counts"]
    right_counts = right["counts"]
    keys = sorted(set(left_counts.keys()) | set(right_counts.keys()))
    count_diff = []
    for key in keys:
        if left_counts.get(key, 0) != right_counts.get(key, 0):
            count_diff.append({
                "event": key,
                "left": left_counts.get(key, 0),
                "right": right_counts.get(key, 0),
            })
    left_seq = [event["name"] for event in left["events"]]
    right_seq = [event["name"] for event in right["events"]]
    return {
        "match": not count_diff and left_seq == right_seq,
        "count_mismatch": count_diff,
        "sequence_match": left_seq == right_seq,
        "left_event_count": len(left_seq),
        "right_event_count": len(right_seq),
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect signal artifacts.")
    parser.add_argument("--save", default=None, help="Save file to inspect.")
    parser.add_argument("--replay", default=None, help="Replay file to inspect.")
    parser.add_argument("--diff", nargs=2, metavar=("LEFT", "RIGHT"),
                        help="Compare two replay files for signal parity.")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    if not args.save and not args.replay and not args.diff:
        parser.error("at least one of --save, --replay, or --diff is required")

    output = {"ok": True}

    if args.save:
        output["save"] = {
            "path": os.path.abspath(args.save),
            "signals": parse_save(args.save),
        }

    if args.replay:
        output["replay"] = {
            "path": os.path.abspath(args.replay),
            "signals": parse_replay(args.replay),
        }

    if args.diff:
        left_path, right_path = args.diff
        diff = diff_replays(left_path, right_path)
        output["diff"] = {
            "left": os.path.abspath(left_path),
            "right": os.path.abspath(right_path),
            "match": diff["match"],
            "count_mismatch": diff["count_mismatch"],
            "sequence_match": diff["sequence_match"],
            "left_event_count": diff["left_event_count"],
            "right_event_count": diff["right_event_count"],
        }
        if not diff["match"]:
            output["ok"] = False

    if args.format == "json":
        print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        if args.save:
            signals = output["save"]["signals"]
            print("signals_links={} objects={}".format(
                len(signals.get("links") or []),
                len(signals.get("objects") or []),
            ))
        if args.replay:
            signals = output["replay"]["signals"]
            print("signal_events={}".format(len(signals.get("events") or [])))
        if args.diff:
            match = output["diff"]["match"]
            print("signal_replay_match={}".format("yes" if match else "no"))
    return 0 if output["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
