import argparse
import json
import os
import sys

from playtest_lib import parse_replay, hash_events, parse_event_line


def normalize_variants(variants):
    entries = []
    for v in variants:
        entries.append((v.get("scope", ""), v.get("system_id", ""), v.get("variant_id", "")))
    return sorted(entries)


def diff_events(left_events, right_events):
    if len(left_events) != len(right_events):
        return {"count_left": len(left_events), "count_right": len(right_events), "first_diff": None}
    for idx, (lval, rval) in enumerate(zip(left_events, right_events)):
        if lval != rval:
            return {"count_left": len(left_events), "count_right": len(right_events), "first_diff": idx}
    return None


def extract_refusal_events(events):
    extracted = []
    for idx, line in enumerate(events):
        parsed = parse_event_line(line)
        name = (parsed.get("name") or "").lower()
        detail_map = parsed.get("detail_map") or {}
        if "refusal" in name or "refuse" in name or "refusal_code" in detail_map:
            extracted.append({
                "index": idx,
                "seq": parsed.get("seq"),
                "event": parsed.get("name"),
                "refusal_code": detail_map.get("refusal_code") or detail_map.get("code"),
                "detail": parsed.get("detail"),
            })
    return extracted


def diff_refusals(left_refusals, right_refusals):
    if len(left_refusals) != len(right_refusals):
        return {"count_left": len(left_refusals), "count_right": len(right_refusals), "first_diff": None}
    for idx, (lval, rval) in enumerate(zip(left_refusals, right_refusals)):
        if lval != rval:
            return {"count_left": len(left_refusals), "count_right": len(right_refusals), "first_diff": idx}
    return None


def diff_meta(left_meta, right_meta):
    diffs = {}
    for key in ("scenario_id", "scenario_version", "lockfile_id", "lockfile_hash"):
        if left_meta.get(key, "") != right_meta.get(key, ""):
            diffs[key] = {"left": left_meta.get(key, ""), "right": right_meta.get(key, "")}
    left_vars = sorted(left_meta.get("scenario_variants", []))
    right_vars = sorted(right_meta.get("scenario_variants", []))
    if left_vars != right_vars:
        diffs["scenario_variants"] = {"left": left_vars, "right": right_vars}
    return diffs or None


def main():
    parser = argparse.ArgumentParser(description="Diff two replay files.")
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--compare", choices=["all", "events", "meta", "variants"], default="all")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--fail-on-diff", action="store_true")
    args = parser.parse_args()

    left_path = os.path.abspath(args.left)
    right_path = os.path.abspath(args.right)
    try:
        left = parse_replay(left_path)
        right = parse_replay(right_path)
    except Exception as exc:
        sys.stderr.write("replay_diff: {}\n".format(exc))
        return 1

    diffs = {}
    if args.compare in ("all", "meta"):
        meta_diff = diff_meta(left["meta"], right["meta"])
        if meta_diff:
            diffs["meta"] = meta_diff
    if args.compare in ("all", "variants"):
        left_vars = normalize_variants(left["variants"])
        right_vars = normalize_variants(right["variants"])
        if left_vars != right_vars:
            diffs["variants"] = {"left": left_vars, "right": right_vars}
    if args.compare in ("all", "events"):
        event_diff = diff_events(left["events"], right["events"])
        if event_diff:
            diffs["events"] = event_diff
        left_refusals = extract_refusal_events(left["events"])
        right_refusals = extract_refusal_events(right["events"])
        refusal_diff = diff_refusals(left_refusals, right_refusals)
        if refusal_diff:
            diffs["refusals"] = refusal_diff

    payload = {
        "ok": not diffs,
        "left": {"path": left_path, "event_hash": hash_events(left["events"])},
        "right": {"path": right_path, "event_hash": hash_events(right["events"])},
        "diff": diffs,
        "compare": args.compare,
    }

    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("replay_diff=ok" if payload["ok"] else "replay_diff=diff")
        print("left={}".format(left_path))
        print("right={}".format(right_path))
        print("left_hash={}".format(payload["left"]["event_hash"]))
        print("right_hash={}".format(payload["right"]["event_hash"]))
        if diffs:
            print("diffs={}".format(len(diffs)))
            for key, value in diffs.items():
                print("diff_{}={}".format(key, value))
        else:
            print("diffs=0")

    if args.fail_on_diff and diffs:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
