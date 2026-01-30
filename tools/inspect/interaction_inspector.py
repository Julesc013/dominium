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
    if "provenance" in tokens:
        obj["provenance_id"] = tokens["provenance"]
    return obj


def parse_save(path):
    lines = read_lines(path)
    data = {
        "policy": None,
        "next_id": None,
        "selected_type": None,
        "tool": None,
        "objects": [],
    }
    in_interactions = False
    for line in lines:
        if line == "interactions_begin":
            in_interactions = True
            continue
        if line == "interactions_end":
            in_interactions = False
            continue
        if line.startswith("policy.interaction="):
            data["policy"] = line.split("=", 1)[1]
            continue
        if not in_interactions:
            continue
        if line.startswith("interaction_next_id="):
            value = line.split("=", 1)[1]
            try:
                data["next_id"] = int(value)
            except ValueError:
                data["next_id"] = value
        elif line.startswith("interaction_selected_type="):
            data["selected_type"] = line.split("=", 1)[1]
        elif line.startswith("interaction_tool="):
            data["tool"] = line.split("=", 1)[1]
        elif line.startswith("interaction_object"):
            data["objects"].append(parse_interaction_object(line))
    return data


def extract_event_name(line):
    marker = "client.interaction."
    idx = line.find(marker)
    if idx == -1:
        return None
    end = idx + len(marker)
    while end < len(line) and (line[end].isalnum() or line[end] in "._-"):
        end += 1
    return line[idx:end]


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
    parser = argparse.ArgumentParser(description="Inspect interaction artifacts.")
    parser.add_argument("--save", default=None, help="Save file to inspect.")
    parser.add_argument("--replay", default=None, help="Replay file to inspect.")
    parser.add_argument("--diff", nargs=2, metavar=("LEFT", "RIGHT"),
                        help="Compare two replay files for interaction parity.")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    if not args.save and not args.replay and not args.diff:
        parser.error("at least one of --save, --replay, or --diff is required")

    output = {"ok": True}

    if args.save:
        output["save"] = {
            "path": os.path.abspath(args.save),
            "interaction": parse_save(args.save),
        }

    if args.replay:
        output["replay"] = {
            "path": os.path.abspath(args.replay),
            "interaction": parse_replay(args.replay),
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
            interaction = output["save"]["interaction"]
            print("save_interactions={} objects={}".format(
                interaction.get("selected_type") or "none",
                len(interaction.get("objects") or []),
            ))
        if args.replay:
            interaction = output["replay"]["interaction"]
            print("replay_events={}".format(len(interaction.get("events") or [])))
        if args.diff:
            match = output["diff"]["match"]
            print("replay_match={}".format("yes" if match else "no"))
    return 0 if output["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
