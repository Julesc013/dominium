import argparse
import subprocess
import sys


FAMILY_INVARIANTS = {
    "two_node_determinism": [
        "SCALE0-DETERMINISM-004",
        "MMO0-UNIVERSE-012",
        "MMO0-LOG-015",
        "MMO0-TIME-016",
    ],
    "join_resync": [
        "MMO0-RESYNC-017",
        "MMO0-COMPAT-018",
        "SCALE0-DETERMINISM-004",
    ],
    "abuse_resistance": [
        "SCALE3-BUDGET-009",
        "SCALE3-ADMISSION-010",
        "SCALE0-DETERMINISM-004",
    ],
    "legacy_compatibility": [
        "MMO0-COMPAT-018",
        "MMO0-RESYNC-017",
        "SCALE0-DETERMINISM-004",
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


def compare_keys(label, data_a, data_b, keys):
    for key in keys:
        if key not in data_a or key not in data_b:
            sys.stderr.write("FAIL: {} missing key '{}'\n".format(label, key))
            raise SystemExit(1)
        if data_a[key] != data_b[key]:
            sys.stderr.write(
                "FAIL: {} key '{}' mismatch: {} != {}\n".format(label, key, data_a[key], data_b[key])
            )
            raise SystemExit(1)


def test_two_node_determinism(tools_path):
    cmd_1 = [tools_path, "mmo", "two-node", "--workers", "1"]
    cmd_4 = [tools_path, "mmo", "two-node", "--workers", "4"]
    code_1, out_1, err_1 = run_cmd(cmd_1)
    code_4, out_4, err_4 = run_cmd(cmd_4)
    expect_ok(code_1, cmd_1, out_1, err_1)
    expect_ok(code_4, cmd_4, out_4, err_4)
    data_1 = parse_kv(out_1)
    data_4 = parse_kv(out_4)
    check_invariants("two_node_determinism", data_1)
    check_invariants("two_node_determinism", data_4)
    if data_1.get("two_node.hash_match") != "1" or data_4.get("two_node.hash_match") != "1":
        sys.stderr.write("FAIL: two-node hash mismatch\n")
        raise SystemExit(1)
    compare_keys(
        "two-node determinism",
        data_1,
        data_4,
        ["two_node.hash_a", "two_node.hash_b", "two_node.owner_hash_a", "two_node.owner_hash_b"],
    )


def test_join_resync(tools_path):
    cmd_1 = [tools_path, "mmo", "join-resync", "--workers", "1"]
    cmd_4 = [tools_path, "mmo", "join-resync", "--workers", "4"]
    code_1, out_1, err_1 = run_cmd(cmd_1)
    code_4, out_4, err_4 = run_cmd(cmd_4)
    expect_ok(code_1, cmd_1, out_1, err_1)
    expect_ok(code_4, cmd_4, out_4, err_4)
    data_1 = parse_kv(out_1)
    data_4 = parse_kv(out_4)
    check_invariants("join_resync", data_1)
    check_invariants("join_resync", data_4)
    if data_1.get("resync.hash_match") != "1" or data_4.get("resync.hash_match") != "1":
        sys.stderr.write("FAIL: resync hash mismatch\n")
        raise SystemExit(1)
    if data_1.get("resync.status") not in ("0", None) or data_4.get("resync.status") not in ("0", None):
        sys.stderr.write("FAIL: resync reported refusal\n")
        raise SystemExit(1)
    compare_keys("join-resync determinism", data_1, data_4, ["join.world_hash", "resync.world_hash"])


def test_abuse_resistance(tools_path):
    cmd = [tools_path, "mmo", "abuse", "--workers", "1"]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("abuse_resistance", data)
    rate_limit = int(data.get("abuse.refusal_rate_limit", "0"))
    if rate_limit <= 0:
        sys.stderr.write("FAIL: expected rate-limit refusals\n")
        raise SystemExit(1)


def test_legacy_compatibility(tools_path):
    cmd = [tools_path, "mmo", "legacy", "--workers", "1"]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("legacy_compatibility", data)
    refusal_cap = int(data.get("legacy.refusal_capability", "0"))
    if refusal_cap <= 0:
        sys.stderr.write("FAIL: expected capability refusals for legacy client\n")
        raise SystemExit(1)
    if data.get("legacy.resync_refusal") in (None, "REFUSE_NONE"):
        sys.stderr.write("FAIL: expected explicit resync refusal for legacy client\n")
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="MMO-1 deterministic runtime tests.")
    parser.add_argument("--tools", required=True)
    parser.add_argument("--family", required=True, choices=sorted(FAMILY_INVARIANTS.keys()))
    args = parser.parse_args()

    if args.family == "two_node_determinism":
        test_two_node_determinism(args.tools)
    elif args.family == "join_resync":
        test_join_resync(args.tools)
    elif args.family == "abuse_resistance":
        test_abuse_resistance(args.tools)
    elif args.family == "legacy_compatibility":
        test_legacy_compatibility(args.tools)

    print("MMO-1 tests OK for {}".format(args.family))
    return 0


if __name__ == "__main__":
    sys.exit(main())

