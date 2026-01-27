import argparse
import subprocess
import sys


FAMILY_INVARIANTS = {
    "cost_invariance": [
        "SCALE0-DETERMINISM-004",
        "SCALE3-BUDGET-009",
        "SCALE3-CONSTCOST-011",
    ],
    "budget_enforcement": [
        "SCALE3-BUDGET-009",
        "SCALE3-ADMISSION-010",
    ],
    "thread_count_invariance": [
        "SCALE0-DETERMINISM-004",
        "SCALE3-CONSTCOST-011",
    ],
    "long_horizon_stress": [
        "SCALE0-DETERMINISM-004",
        "SCALE3-BUDGET-009",
        "SCALE3-CONSTCOST-011",
    ],
}


CONSTCOST_COMPARE_KEYS = [
    "constcost.event_hash",
    "constcost.active_hash",
    "expand_failures",
    "events.total",
    "events.expand",
    "events.refusal",
    "events.defer",
    "budget.tick",
    "tier2",
    "refinement",
    "expand",
    "snapshot",
    "deferred",
    "refusals_active",
    "refusals_refine",
    "refusals_macro",
    "refusals_planning",
    "refusals_snapshot",
    "refusals_collapse",
    "refusals_defer_limit",
]


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


def test_cost_invariance(tools_path):
    cmd_small = [
        tools_path,
        "scale",
        "constcost",
        "3",
        "--active",
        "1",
        "--ticks",
        "4096",
        "--workers",
        "1",
    ]
    cmd_large = [
        tools_path,
        "scale",
        "constcost",
        "32",
        "--active",
        "1",
        "--ticks",
        "4096",
        "--workers",
        "1",
    ]
    code_s, out_s, err_s = run_cmd(cmd_small)
    code_l, out_l, err_l = run_cmd(cmd_large)
    expect_ok(code_s, cmd_small, out_s, err_s)
    expect_ok(code_l, cmd_large, out_l, err_l)
    data_s = parse_kv(out_s)
    data_l = parse_kv(out_l)
    check_invariants("cost_invariance", data_s)
    check_invariants("cost_invariance", data_l)
    compare_keys("constcost cost invariance", data_s, data_l, CONSTCOST_COMPARE_KEYS)
    if data_s.get("expand_failures") != "0":
        sys.stderr.write("FAIL: expansion failures in small world\n")
        raise SystemExit(1)
    if data_l.get("expand_failures") != "0":
        sys.stderr.write("FAIL: expansion failures in large world\n")
        raise SystemExit(1)


def test_budget_enforcement(tools_path):
    cases = [
        ("budget", "REFUSE_COLLAPSE_BUDGET"),
        ("active", "REFUSE_ACTIVE_DOMAIN_LIMIT"),
        ("refinement", "REFUSE_REFINEMENT_BUDGET"),
        ("macro", "REFUSE_MACRO_EVENT_BUDGET"),
        ("planning", "REFUSE_AGENT_PLANNING_BUDGET"),
        ("snapshot", "REFUSE_SNAPSHOT_BUDGET"),
        ("tier2", "REFUSE_DOMAIN_FORBIDDEN"),
        ("unsupported", "REFUSE_CAPABILITY_MISSING"),
    ]
    for case_name, expected_refusal in cases:
        cmd = [tools_path, "scale", "refusal", case_name, "--workers", "1"]
        code, out, err = run_cmd(cmd)
        expect_ok(code, cmd, out, err)
        data = parse_kv(out)
        check_invariants("budget_enforcement", data)
        if data.get("refusal") != expected_refusal:
            sys.stderr.write(
                "FAIL: refusal token mismatch for {}: {} != {}\n".format(
                    case_name, data.get("refusal"), expected_refusal
                )
            )
            raise SystemExit(1)
        if data.get("refusal_code") in (None, "0"):
            sys.stderr.write("FAIL: refusal code missing for {}\n".format(case_name))
            raise SystemExit(1)
        if data.get("defer") not in (None, "DEFER_NONE"):
            sys.stderr.write("FAIL: unexpected defer for {}\n".format(case_name))
            raise SystemExit(1)


def test_thread_count_invariance(tools_path):
    cmd_1 = [
        tools_path,
        "scale",
        "constcost",
        "32",
        "--active",
        "2",
        "--ticks",
        "8192",
        "--workers",
        "1",
    ]
    cmd_4 = [
        tools_path,
        "scale",
        "constcost",
        "32",
        "--active",
        "2",
        "--ticks",
        "8192",
        "--workers",
        "4",
    ]
    code_1, out_1, err_1 = run_cmd(cmd_1)
    code_4, out_4, err_4 = run_cmd(cmd_4)
    expect_ok(code_1, cmd_1, out_1, err_1)
    expect_ok(code_4, cmd_4, out_4, err_4)
    data_1 = parse_kv(out_1)
    data_4 = parse_kv(out_4)
    check_invariants("thread_count_invariance", data_1)
    check_invariants("thread_count_invariance", data_4)
    compare_keys("constcost thread invariance", data_1, data_4, CONSTCOST_COMPARE_KEYS)


def test_long_horizon_stress(tools_path):
    cmd = [
        tools_path,
        "scale",
        "stress",
        "32",
        "--ticks",
        "262144",
        "--workers",
        "1",
    ]
    code, out, err = run_cmd(cmd)
    expect_ok(code, cmd, out, err)
    data = parse_kv(out)
    check_invariants("long_horizon_stress", data)
    if data.get("deferred_overflow") not in (None, "0"):
        sys.stderr.write("FAIL: deferred overflow detected\n")
        raise SystemExit(1)
    if data.get("refusals_defer_limit") not in (None, "0"):
        sys.stderr.write("FAIL: defer queue limit refusals detected\n")
        raise SystemExit(1)
    macro_exec = int(data.get("macro_exec_events", "0"))
    if macro_exec <= 0:
        sys.stderr.write("FAIL: expected macro execution events\n")
        raise SystemExit(1)
    domains = int(data.get("domains", "0"))
    queue_count = int(data.get("queue_count", "0"))
    if domains > 0 and queue_count > domains * 2:
        sys.stderr.write("FAIL: macro queue exceeded policy limit\n")
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="SCALE-3 budget and constant-cost tests.")
    parser.add_argument("--tools", required=True)
    parser.add_argument("--family", required=True, choices=sorted(FAMILY_INVARIANTS.keys()))
    args = parser.parse_args()

    if args.family == "cost_invariance":
        test_cost_invariance(args.tools)
    elif args.family == "budget_enforcement":
        test_budget_enforcement(args.tools)
    elif args.family == "thread_count_invariance":
        test_thread_count_invariance(args.tools)
    elif args.family == "long_horizon_stress":
        test_long_horizon_stress(args.tools)

    print("SCALE-3 tests OK for {}".format(args.family))
    return 0


if __name__ == "__main__":
    sys.exit(main())
