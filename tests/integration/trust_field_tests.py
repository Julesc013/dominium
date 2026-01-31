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
    parser = argparse.ArgumentParser(description="Trust T17 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "trust")

    fixtures = [
        "audit_chain.trust",
        "endorsement_transfer.trust",
        "dispute_spike.trust",
        "legitimacy_contested.trust",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "trust tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "trust fixtures missing")

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
                "DOMINIUM_TRUST_VALIDATE_V1",
                "provider_chain=fields->events->profiles->legitimacy",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "audit_chain.trust")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--field",
            "trust.field.audit",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_TRUST_INSPECT_V1",
            "entity=field",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "trust_id",
            "subject_ref_id",
            "context_id",
            "trust_level_q16",
            "uncertainty_q16",
            "decay_rate_q16",
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
            "--event",
            "trust.event.incident",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_TRUST_INSPECT_V1",
            "entity=event",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "event_id",
            "process_type",
            "delta_level_q16",
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
            "--profile",
            "trust.profile.institution_a",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_TRUST_INSPECT_V1",
            "entity=profile",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "profile_id",
            "historical_performance_q16",
            "audit_results_q16",
            "incident_history_q16",
            "endorsements_q16",
            "disputes_q16",
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
            "--legitimacy",
            "trust.legitimacy.a",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_TRUST_INSPECT_V1",
            "entity=legitimacy",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "legitimacy_id",
            "compliance_rate_q16",
            "challenge_rate_q16",
            "symbolic_support_q16",
            "uncertainty_q16",
            "flags",
        ):
            ok = ok and require(key in data, "legitimacy inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "trust.region.primary",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_TRUST_INSPECT_V1",
            "entity=region",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "field_count",
            "event_count",
            "profile_count",
            "legitimacy_count",
            "trust_avg_q16",
            "dispute_rate_avg_q16",
            "compliance_rate_avg_q16",
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
            "trust.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_TRUST_RESOLVE_V1",
            "provider_chain=fields->events->profiles->legitimacy",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "field_count",
            "event_count",
            "event_applied_count",
            "profile_count",
            "legitimacy_count",
            "trust_avg_q16",
            "dispute_rate_avg_q16",
            "compliance_rate_avg_q16",
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
            "trust.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_TRUST_RESOLVE_V1"],
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
            "trust.region.primary",
        ],
        expect_contains=["DOMINIUM_TRUST_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
