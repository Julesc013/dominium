import argparse
import subprocess
import sys


FAMILY_INVARIANTS = {
    "collapse_expand_equivalence": [
        "SCALE0-CONSERVE-002",
        "SCALE0-COMMIT-003",
        "SCALE0-DETERMINISM-004",
    ],
    "interest_pattern_invariance": [
        "SCALE0-INTEREST-006",
        "SCALE0-CONSERVE-002",
        "SCALE0-COMMIT-003",
    ],
    "thread_count_invariance": [
        "SCALE0-DETERMINISM-004",
        "SCALE0-REPLAY-008",
    ],
    "refusal_behavior": [
        "SCALE0-CONSERVE-002",
        "SCALE0-REPLAY-008",
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


def test_equivalence(tools_path):
    domains = ["resources", "network", "agents"]
    for domain in domains:
        cmd = [tools_path, "scale", "collapse-expand", domain, "--workers", "1"]
        code, out, err = run_cmd(cmd)
        expect_ok(code, cmd, out, err)
        data = parse_kv(out)
        check_invariants("collapse_expand_equivalence", data)
        if data.get("hash_match") != "1":
            sys.stderr.write("FAIL: hash mismatch for {}\n".format(domain))
            raise SystemExit(1)
        if data.get("collapse_refusal") not in (None, "REFUSE_NONE"):
            sys.stderr.write("FAIL: collapse refusal for {}\n".format(domain))
            raise SystemExit(1)
        if data.get("expand_refusal") not in (None, "REFUSE_NONE"):
            sys.stderr.write("FAIL: expand refusal for {}\n".format(domain))
            raise SystemExit(1)


def test_interest(tools_path):
    cmd_a = [tools_path, "scale", "interest", "A", "--workers", "1"]
    cmd_b = [tools_path, "scale", "interest", "B", "--workers", "1"]
    code_a, out_a, err_a = run_cmd(cmd_a)
    code_b, out_b, err_b = run_cmd(cmd_b)
    expect_ok(code_a, cmd_a, out_a, err_a)
    expect_ok(code_b, cmd_b, out_b, err_b)
    data_a = parse_kv(out_a)
    data_b = parse_kv(out_b)
    check_invariants("interest_pattern_invariance", data_a)
    check_invariants("interest_pattern_invariance", data_b)
    if data_a.get("global_hash") != data_b.get("global_hash"):
        sys.stderr.write("FAIL: global hash mismatch across interest patterns\n")
        raise SystemExit(1)


def test_thread_count(tools_path):
    cmd_1 = [tools_path, "scale", "collapse-expand", "resources", "--workers", "1"]
    cmd_4 = [tools_path, "scale", "collapse-expand", "resources", "--workers", "4"]
    code_1, out_1, err_1 = run_cmd(cmd_1)
    code_4, out_4, err_4 = run_cmd(cmd_4)
    expect_ok(code_1, cmd_1, out_1, err_1)
    expect_ok(code_4, cmd_4, out_4, err_4)
    data_1 = parse_kv(out_1)
    data_4 = parse_kv(out_4)
    check_invariants("thread_count_invariance", data_1)
    check_invariants("thread_count_invariance", data_4)
    if data_1.get("capsule_hash") != data_4.get("capsule_hash"):
        sys.stderr.write("FAIL: capsule hash mismatch across worker counts\n")
        raise SystemExit(1)
    if data_1.get("hash_before") != data_4.get("hash_before"):
        sys.stderr.write("FAIL: domain hash mismatch across worker counts\n")
        raise SystemExit(1)


def test_refusals(tools_path):
    cases = [
        ("budget", "REFUSE_COLLAPSE_BUDGET", "706"),
        ("tier2", "REFUSE_DOMAIN_FORBIDDEN", "4"),
        ("unsupported", "REFUSE_CAPABILITY_MISSING", "3"),
    ]
    for case_name, refusal_token, refusal_code in cases:
        cmd = [tools_path, "scale", "refusal", case_name, "--workers", "1"]
        code, out, err = run_cmd(cmd)
        expect_ok(code, cmd, out, err)
        data = parse_kv(out)
        check_invariants("refusal_behavior", data)
        if data.get("refusal") != refusal_token:
            sys.stderr.write("FAIL: refusal token mismatch for {}\n".format(case_name))
            raise SystemExit(1)
        if data.get("refusal_code") != refusal_code:
            sys.stderr.write("FAIL: refusal code mismatch for {}\n".format(case_name))
            raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="SCALE-1 collapse/expand tests.")
    parser.add_argument("--tools", required=True)
    parser.add_argument("--family", required=True, choices=sorted(FAMILY_INVARIANTS.keys()))
    args = parser.parse_args()

    if args.family == "collapse_expand_equivalence":
        test_equivalence(args.tools)
    elif args.family == "interest_pattern_invariance":
        test_interest(args.tools)
    elif args.family == "thread_count_invariance":
        test_thread_count(args.tools)
    elif args.family == "refusal_behavior":
        test_refusals(args.tools)

    print("SCALE-1 tests OK for {}".format(args.family))
    return 0


if __name__ == "__main__":
    sys.exit(main())
