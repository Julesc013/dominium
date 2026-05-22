import argparse
import os
import subprocess
import sys


def run_cmd(cmd, expect_code=0, expect_contains=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = result.stdout or ""
    if expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False, output
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                return False, output
    return True, output


def parse_kv(output):
    data = {}
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def resolve_fixture(tool_path, fixture_path, extra_args=None):
    cmd = [
        tool_path,
        "resolve",
        "--fixture",
        fixture_path,
        "--region",
        "srz.region.core",
        "--tick",
        "5",
        "--delta",
        "1",
        "--budget",
        "300",
    ]
    if extra_args:
        cmd.extend(extra_args)
    return run_cmd(cmd, expect_contains=["DOMINIUM_SRZ_RESOLVE_V1"])


def main():
    parser = argparse.ArgumentParser(description="SRZ-0 perf/scaling tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "srz")

    fixtures = [
        "baseline.srz",
        "dense_server.srz",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "srz tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "srz fixtures missing")

    baseline_cost = None
    for fixture in fixtures:
        fixture_path = os.path.join(fixture_root, fixture)
        ok = ok and require(os.path.isfile(fixture_path), "missing fixture {}".format(fixture_path))
        if not ok:
            return 1
        success, output = resolve_fixture(tool_path, fixture_path)
        ok = ok and success
        if success:
            data = parse_kv(output)
            cost = int(data.get("budget.used", "0"))
            ok = ok and require(cost > 0, "budget.used missing or zero for {}".format(fixture))
            if baseline_cost is None:
                baseline_cost = cost
            else:
                ok = ok and require(cost == baseline_cost, "cost drift across SRZ fixtures")

    base_fixture = os.path.join(fixture_root, "baseline.srz")
    success, output = resolve_fixture(tool_path, base_fixture, ["--inactive", "64"])
    ok = ok and success
    if success and baseline_cost is not None:
        data = parse_kv(output)
        inactive_cost = int(data.get("budget.used", "0"))
        ok = ok and require(inactive_cost == baseline_cost, "inactive domains changed cost")

    success, output = resolve_fixture(tool_path, base_fixture, ["--simulate_sparse", "10000"])
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("sim_sparse") == "10000", "simulate_sparse not reported")

    dense_fixture = os.path.join(fixture_root, "dense_server.srz")
    success, output = resolve_fixture(tool_path, dense_fixture, ["--simulate_dense", "10000"])
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("sim_dense") == "10000", "simulate_dense not reported")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
