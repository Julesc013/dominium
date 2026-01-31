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
    parser = argparse.ArgumentParser(description="Risk T16 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "risk")

    fixtures = [
        "fire_insurance.risk",
        "floodplain.risk",
        "thermal_outage.risk",
        "data_breach.risk",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "risk tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "risk fixtures missing")

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
                "DOMINIUM_RISK_VALIDATE_V1",
                "provider_chain=types->fields->exposures->profiles->liability->insurance",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "fire_insurance.risk")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--type",
            "risk.type.fire",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_RISK_INSPECT_V1",
            "entity=type",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "type_id",
            "risk_class",
            "default_exposure_rate_q16",
            "default_impact_mean_q48",
            "default_impact_spread_q16",
            "default_uncertainty_q16",
            "flags",
            "meta.status",
            "budget.used",
        ):
            ok = ok and require(key in data, "type inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--field",
            "risk.field.primary",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_RISK_INSPECT_V1",
            "entity=field",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "risk_id",
            "risk_type_id",
            "exposure_rate_q16",
            "impact_mean_q48",
            "impact_spread_q16",
            "uncertainty_q16",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "field inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--exposure",
            "risk.exposure.actor_a",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_RISK_INSPECT_V1",
            "entity=exposure",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "exposure_id",
            "exposure_limit_q48",
            "exposure_accumulated_q48",
            "sensitivity_q16",
            "uncertainty_q16",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "exposure inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--profile",
            "risk.profile.site_a",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_RISK_INSPECT_V1",
            "entity=profile",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "profile_id",
            "exposure_total_q48",
            "impact_mean_q48",
            "impact_spread_q16",
            "uncertainty_q16",
            "flags",
        ):
            ok = ok and require(key in data, "profile inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--event",
            "risk.event.incident",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_RISK_INSPECT_V1",
            "entity=event",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "event_id",
            "risk_type_id",
            "loss_amount_q48",
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
            "--policy",
            "risk.policy.standard",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_RISK_INSPECT_V1",
            "entity=policy",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "policy_id",
            "coverage_ratio_q16",
            "payout_limit_q48",
            "deductible_q48",
            "flags",
        ):
            ok = ok and require(key in data, "policy inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--claim",
            "risk.claim.1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_RISK_INSPECT_V1",
            "entity=claim",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "claim_id",
            "claim_amount_q48",
            "approved_amount_q48",
            "flags",
        ):
            ok = ok and require(key in data, "claim inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "risk.region.primary",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_RISK_INSPECT_V1",
            "entity=region",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "field_count",
            "exposure_count",
            "profile_count",
            "exposure_total_q48",
            "impact_mean_total_q48",
            "flags",
        ):
            ok = ok and require(key in data, "region inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "risk.region.primary",
            "--tick",
            "0",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_RISK_RESOLVE_V1",
            "provider_chain=types->fields->exposures->profiles->liability->insurance",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "field_count",
            "exposure_count",
            "profile_count",
            "claim_count",
            "exposure_total_q48",
            "impact_mean_total_q48",
            "claim_paid_total_q48",
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
            "risk.region.primary",
            "--tick",
            "0",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_RISK_RESOLVE_V1"],
    )
    ok = ok and success
    if success and resolve_hash is not None:
        repeat_hash = parse_kv(output).get("resolve_hash")
        ok = ok and require(repeat_hash == resolve_hash, "determinism hash mismatch")

    success, output = run_cmd(
        [
            tool_path,
            "collapse",
            "--fixture",
            base_fixture,
            "--region",
            "risk.region.primary",
        ],
        expect_contains=["DOMINIUM_RISK_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
