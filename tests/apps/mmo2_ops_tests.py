import argparse
import subprocess
import sys


FAMILY_INVARIANTS = {
    "checkpoint_model": [
        "MMO2-CHECKPOINT-001",
        "MMO2-LOG-006",
        "MMO2-LIFECYCLE-003",
    ],
    "crash_recovery": [
        "MMO2-RECOVERY-002",
        "MMO2-CHECKPOINT-001",
    ],
    "rolling_updates": [
        "MMO2-LIFECYCLE-003",
        "MMO2-ROLLING-004",
    ],
    "cross_shard_log": [
        "MMO0-LOG-015",
        "MMO2-LOG-006",
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


def as_int(data, key, default="0"):
    try:
        return int(data.get(key, default))
    except ValueError:
        return int(default)


def test_checkpoint_model(tools_path):
    cmd = [tools_path, "mmo", "ops-checkpoint", "--workers", "1"]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("checkpoint_model", data)
    tick = as_int(data, "checkpoint.tick")
    lifecycle_count = as_int(data, "lifecycle_count")
    checkpoint_id = as_int(data, "checkpoint.id")
    if tick <= 0 or lifecycle_count <= 0 or checkpoint_id == 0:
        sys.stderr.write("FAIL: checkpoint summary looks invalid\n")
        raise SystemExit(1)


def test_crash_recovery(tools_path):
    cmd_1 = [tools_path, "mmo", "ops-recover", "--workers", "1"]
    cmd_4 = [tools_path, "mmo", "ops-recover", "--workers", "4"]
    code_1, out_1, err_1 = run_cmd(cmd_1)
    code_4, out_4, err_4 = run_cmd(cmd_4)
    expect_ok(code_1, cmd_1, out_1, err_1)
    expect_ok(code_4, cmd_4, out_4, err_4)
    data_1 = parse_kv(out_1)
    data_4 = parse_kv(out_4)
    check_invariants("crash_recovery", data_1)
    check_invariants("crash_recovery", data_4)

    if data_1.get("refusal") not in (None, "REFUSE_NONE"):
        sys.stderr.write("FAIL: recovery reported refusal (workers=1)\n")
        raise SystemExit(1)
    if data_4.get("refusal") not in (None, "REFUSE_NONE"):
        sys.stderr.write("FAIL: recovery reported refusal (workers=4)\n")
        raise SystemExit(1)

    after_1 = data_1.get("recover.after_hash")
    shadow_1 = data_1.get("recover.shadow_hash")
    after_4 = data_4.get("recover.after_hash")
    shadow_4 = data_4.get("recover.shadow_hash")
    if not after_1 or after_1 != shadow_1:
        sys.stderr.write("FAIL: recovery mismatch against shadow (workers=1)\n")
        raise SystemExit(1)
    if not after_4 or after_4 != shadow_4:
        sys.stderr.write("FAIL: recovery mismatch against shadow (workers=4)\n")
        raise SystemExit(1)
    if after_1 != after_4:
        sys.stderr.write("FAIL: recovery hash differs across worker counts\n")
        raise SystemExit(1)


def test_rolling_updates(tools_path):
    cmd = [tools_path, "mmo", "ops-shards", "--workers", "1"]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("rolling_updates", data)
    refusal_gap = as_int(data, "ops.refusal_cap_gap")
    owner_after = as_int(data, "owner_after")
    if refusal_gap <= 0 or owner_after != 2:
        sys.stderr.write("FAIL: expected capability gap refusal and owner transfer\n")
        raise SystemExit(1)


def test_cross_shard_log(tools_path):
    cmd = [tools_path, "mmo", "ops-log", "--workers", "1"]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("cross_shard_log", data)
    before = as_int(data, "log.count_before")
    after = as_int(data, "log.count_after")
    owner_after = as_int(data, "owner_after")
    if before <= 0 or after != 0 or owner_after != 2:
        sys.stderr.write("FAIL: log inspection scenario did not behave as expected\n")
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="MMO-2 ops determinism tests.")
    parser.add_argument("--tools", required=True)
    parser.add_argument("--family", required=True, choices=sorted(FAMILY_INVARIANTS.keys()))
    args = parser.parse_args()

    if args.family == "checkpoint_model":
        test_checkpoint_model(args.tools)
    elif args.family == "crash_recovery":
        test_crash_recovery(args.tools)
    elif args.family == "rolling_updates":
        test_rolling_updates(args.tools)
    elif args.family == "cross_shard_log":
        test_cross_shard_log(args.tools)

    print("MMO-2 ops tests OK for {}".format(args.family))
    return 0


if __name__ == "__main__":
    sys.exit(main())

