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
    parser = argparse.ArgumentParser(description="Institution T19 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "institution")

    fixtures = [
        "baseline.institution",
        "overlap_conflict.institution",
        "legitimacy_low.institution",
        "enforcement_gap.institution",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "institution tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "institution fixtures missing")

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
                "DOMINIUM_INSTITUTION_VALIDATE_V1",
                "provider_chain=entities->scopes->capabilities->rules->enforcement",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "baseline.institution")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--entity",
            "institution.entity.core",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_INSTITUTION_INSPECT_V1",
            "entity=entity",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "institution_id",
            "scope_id",
            "authority_count",
            "enforcement_capacity_q48",
            "resource_budget_q48",
            "legitimacy_level_q16",
            "legitimacy_ref_id",
            "knowledge_base_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "entity inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--scope",
            "institution.scope.core",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_INSTITUTION_INSPECT_V1",
            "entity=scope",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "scope_id",
            "spatial_domain_id",
            "subject_domain_count",
            "overlap_policy_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "scope inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--capability",
            "institution.capability.audit",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_INSTITUTION_INSPECT_V1",
            "entity=capability",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "capability_id",
            "institution_id",
            "scope_id",
            "authority_type_id",
            "process_family_id",
            "capacity_limit_q48",
            "license_required_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "capability inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--rule",
            "institution.rule.safety",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_INSTITUTION_INSPECT_V1",
            "entity=rule",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "rule_id",
            "institution_id",
            "scope_id",
            "process_family_id",
            "subject_domain_id",
            "authority_type_id",
            "action",
            "license_required_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "rule inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--enforcement",
            "institution.enforcement.audit",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_INSTITUTION_INSPECT_V1",
            "entity=enforcement",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "enforcement_id",
            "institution_id",
            "rule_id",
            "process_family_id",
            "agent_id",
            "action",
            "event_tick",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "enforcement inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "institution.region.primary",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_INSTITUTION_INSPECT_V1",
            "entity=region",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "entity_count",
            "scope_count",
            "capability_count",
            "rule_count",
            "enforcement_count",
            "enforcement_capacity_avg_q48",
            "resource_budget_avg_q48",
            "legitimacy_avg_q16",
            "enforcement_permit_count",
            "enforcement_deny_count",
            "enforcement_penalize_count",
            "enforcement_license_count",
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
            "institution.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_INSTITUTION_RESOLVE_V1",
            "provider_chain=entities->scopes->capabilities->rules->enforcement",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "entity_count",
            "scope_count",
            "capability_count",
            "rule_count",
            "enforcement_count",
            "enforcement_applied_count",
            "enforcement_capacity_avg_q48",
            "resource_budget_avg_q48",
            "legitimacy_avg_q16",
            "enforcement_permit_count",
            "enforcement_deny_count",
            "enforcement_penalize_count",
            "enforcement_license_count",
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
            "institution.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_INSTITUTION_RESOLVE_V1"],
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
            "institution.region.primary",
        ],
        expect_contains=["DOMINIUM_INSTITUTION_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
