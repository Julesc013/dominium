import argparse
import subprocess
import sys


FAMILY_INVARIANTS = {
    "long_time_stability": [
        "SCALE0-CONSERVE-002",
        "SCALE0-DETERMINISM-004",
        "SCALE0-REPLAY-008",
    ],
    "compaction_equivalence": [
        "SCALE0-DETERMINISM-004",
        "SCALE0-REPLAY-008",
        "SCALE0-CONSERVE-002",
    ],
    "replay_equivalence": [
        "SCALE0-REPLAY-008",
        "SCALE0-DETERMINISM-004",
        "SCALE0-CONSERVE-002",
    ],
    "interest_transition_safety": [
        "SCALE0-CONSERVE-002",
        "SCALE0-DETERMINISM-004",
        "SCALE0-INTEREST-006",
    ],
}


def run_cmd(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def parse_kv(text):
    data = {}
    for line in text.splitlines():
        for token in line.strip().split():
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def expect_ok(code, cmd, out, err):
    if code == 0:
        return
    sys.stderr.write("FAIL: command failed: {}\n".format(" ".join(cmd)))
    sys.stderr.write(out)
    sys.stderr.write(err)
    raise SystemExit(1)


def check_invariants(family, data):
    invariants = data.get("invariants", "")
    missing = [inv for inv in FAMILY_INVARIANTS[family] if inv not in invariants]
    if missing:
        sys.stderr.write("FAIL: missing invariant ids: {}\n".format(", ".join(missing)))
        raise SystemExit(1)


def test_long_time_stability(tools_path):
    cmd = [
        tools_path,
        "scale",
        "macro-long",
        "365000",
        "--interval",
        "512",
        "--compact",
        "1",
        "--workers",
        "1",
    ]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("long_time_stability", data)
    if data.get("invariants_ok") != "1":
        sys.stderr.write("FAIL: invariants not preserved\n")
        raise SystemExit(1)
    queue_count = int(data.get("queue_count", "0"))
    schedule_count = int(data.get("schedule_count", "0"))
    if schedule_count != 3:
        sys.stderr.write("FAIL: expected 3 schedules, got {}\n".format(schedule_count))
        raise SystemExit(1)
    if queue_count > schedule_count:
        sys.stderr.write("FAIL: macro queue unbounded: {} > {}\n".format(queue_count, schedule_count))
        raise SystemExit(1)
    if data.get("expand_failures") not in (None, "0"):
        sys.stderr.write("FAIL: expansion failures present\n")
        raise SystemExit(1)


def test_compaction_equivalence(tools_path):
    cmd = [
        tools_path,
        "scale",
        "macro-compare",
        "200000",
        "--interval",
        "512",
        "--workers",
        "1",
    ]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("compaction_equivalence", data)
    if data.get("macro_hash_match") != "1":
        sys.stderr.write("FAIL: macro state mismatch across compaction modes\n")
        raise SystemExit(1)
    if data.get("micro_hash_match") != "1":
        sys.stderr.write("FAIL: expansion mismatch across compaction modes\n")
        raise SystemExit(1)


def test_replay_equivalence(tools_path):
    cmd = [
        tools_path,
        "scale",
        "macro-replay",
        "120000",
        "--interval",
        "512",
        "--workers",
        "1",
    ]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("replay_equivalence", data)
    if data.get("replay_hash_match") != "1":
        sys.stderr.write("FAIL: replay hash mismatch\n")
        raise SystemExit(1)
    if data.get("invariants_ok") != "1":
        sys.stderr.write("FAIL: replay invariants violated\n")
        raise SystemExit(1)


def test_interest_transition_safety(tools_path):
    cmd = [
        tools_path,
        "scale",
        "macro-transition",
        "80000",
        "--interval",
        "512",
        "--workers",
        "1",
    ]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("interest_transition_safety", data)
    if data.get("drift_count") not in (None, "0"):
        sys.stderr.write("FAIL: drift detected across macro transitions\n")
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="SCALE-2 macro-time tests.")
    parser.add_argument("--tools", required=True)
    parser.add_argument("--family", required=True, choices=sorted(FAMILY_INVARIANTS.keys()))
    args = parser.parse_args()

    if args.family == "long_time_stability":
        test_long_time_stability(args.tools)
    elif args.family == "compaction_equivalence":
        test_compaction_equivalence(args.tools)
    elif args.family == "replay_equivalence":
        test_replay_equivalence(args.tools)
    elif args.family == "interest_transition_safety":
        test_interest_transition_safety(args.tools)

    print("SCALE-2 tests OK for {}".format(args.family))
    return 0


if __name__ == "__main__":
    sys.exit(main())
