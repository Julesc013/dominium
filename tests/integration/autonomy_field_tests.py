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


def main():
    parser = argparse.ArgumentParser(description="Autonomy T24 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "autonomy")

    fixtures = [
        "baseline.autonomy",
        "plan_fail.autonomy",
        "delegation_revoked.autonomy",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "autonomy tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "autonomy fixtures missing")

    for fixture in fixtures:
        fixture_path = os.path.join(fixture_root, fixture)
        ok = ok and require(os.path.isfile(fixture_path), "missing fixture {}".format(fixture_path))
        if not ok:
            return 1
        success, _output = run_cmd(
            [
                tool_path,
                "validate",
                "--fixture",
                fixture_path,
            ],
            expect_contains=[
                "DOMINIUM_AUTONOMY_VALIDATE_V1",
                "provider_chain=goals->delegations->budgets->plans->events",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "baseline.autonomy")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--goal",
            "autonomy.goal.sample",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_AUTONOMY_INSPECT_V1",
            "entity=goal",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "goal_id",
            "objective_id",
            "priority_q16",
            "expiry_tick",
            "flags",
        ):
            ok = ok and require(key in data, "goal inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--delegation",
            "autonomy.delegation.alpha",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_AUTONOMY_INSPECT_V1",
            "entity=delegation",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "delegation_id",
            "delegate_agent_id",
            "allowed_process_count",
            "flags",
        ):
            ok = ok and require(key in data, "delegation inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--budget_id",
            "autonomy.budget.alpha",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_AUTONOMY_INSPECT_V1",
            "entity=budget",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "budget_id",
            "energy_budget_q48",
            "planning_budget",
            "planning_used",
            "flags",
        ):
            ok = ok and require(key in data, "budget inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--plan",
            "autonomy.plan.alpha",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_AUTONOMY_INSPECT_V1",
            "entity=plan",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "plan_id",
            "status",
            "success_score_q16",
            "flags",
        ):
            ok = ok and require(key in data, "plan inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--event",
            "autonomy.event.plan",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_AUTONOMY_INSPECT_V1",
            "entity=event",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "event_id",
            "process_type",
            "event_tick",
            "flags",
        ):
            ok = ok and require(key in data, "event inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "autonomy.region.core",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_AUTONOMY_INSPECT_V1",
            "entity=region",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "goal_count",
            "delegation_count",
            "budget_count",
            "plan_count",
            "event_count",
            "priority_avg_q16",
            "success_avg_q16",
            "budget_utilization_avg_q16",
            "event_type_count_0",
        ):
            ok = ok and require(key in data, "region inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "autonomy.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_AUTONOMY_RESOLVE_V1",
            "provider_chain=goals->delegations->budgets->plans->events",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "goal_count",
            "delegation_count",
            "budget_count",
            "plan_count",
            "event_count",
            "event_applied_count",
            "priority_avg_q16",
            "success_avg_q16",
            "budget_utilization_avg_q16",
            "flags",
            "ok",
            "resolve_hash",
        ):
            ok = ok and require(key in data, "resolve missing {}".format(key))
        resolve_hash = data.get("resolve_hash")

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "autonomy.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_AUTONOMY_RESOLVE_V1"],
    )
    ok = ok and success
    if success and resolve_hash is not None:
        repeat_hash = parse_kv(output).get("resolve_hash")
        ok = ok and require(repeat_hash == resolve_hash, "determinism hash mismatch")

    fail_fixture = os.path.join(fixture_root, "plan_fail.autonomy")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            fail_fixture,
            "--region",
            "autonomy.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_AUTONOMY_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & 4, "plan failed flag not set")

    revoke_fixture = os.path.join(fixture_root, "delegation_revoked.autonomy")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            revoke_fixture,
            "--region",
            "autonomy.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_AUTONOMY_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & 16, "delegation revoked flag not set")

    success, output = run_cmd(
        [
            tool_path,
            "collapse",
            "--fixture",
            base_fixture,
            "--region",
            "autonomy.region.core",
        ],
        expect_contains=["DOMINIUM_AUTONOMY_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
