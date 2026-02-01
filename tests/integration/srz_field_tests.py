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
    parser = argparse.ArgumentParser(description="SRZ-0 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "srz")

    fixtures = [
        "baseline.srz",
        "malicious_hash.srz",
        "epistemic_leak.srz",
        "escalate.srz",
        "deescalate.srz",
        "shuffled.srz",
        "dense_server.srz",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "srz tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "srz fixtures missing")

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
                "DOMINIUM_SRZ_VALIDATE_V1",
                "provider_chain=zones->assignments->policies->logs->hashchain->deltas",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "baseline.srz")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--zone",
            "srz.zone.alpha",
            "--budget",
            "300",
        ],
        expect_contains=[
            "DOMINIUM_SRZ_INSPECT_V1",
            "entity=zone",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("srz_id", "domain_count", "mode", "verification_policy", "flags"):
            ok = ok and require(key in data, "zone inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--assignment",
            "srz.assignment.alpha",
            "--budget",
            "300",
        ],
        expect_contains=[
            "DOMINIUM_SRZ_INSPECT_V1",
            "entity=assignment",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("assignment_id", "executor_id", "capability_baseline_id", "flags"):
            ok = ok and require(key in data, "assignment inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--policy",
            "srz.policy.strict",
            "--budget",
            "300",
        ],
        expect_contains=[
            "DOMINIUM_SRZ_INSPECT_V1",
            "entity=policy",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("policy_id", "verification_policy", "spot_check_rate_q16", "flags"):
            ok = ok and require(key in data, "policy inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--log",
            "srz.log.alpha",
            "--budget",
            "300",
        ],
        expect_contains=[
            "DOMINIUM_SRZ_INSPECT_V1",
            "entity=log",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("log_id", "chain_id", "process_count", "flags"):
            ok = ok and require(key in data, "log inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "srz.region.core",
            "--budget",
            "300",
        ],
        expect_contains=[
            "DOMINIUM_SRZ_INSPECT_V1",
            "entity=region",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("zone_count", "assignment_count", "log_count", "verification_ok_count"):
            ok = ok and require(key in data, "region inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "srz.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "300",
        ],
        expect_contains=[
            "DOMINIUM_SRZ_RESOLVE_V1",
            "provider_chain=zones->assignments->policies->logs->hashchain->deltas",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in ("log_count", "verification_ok_count", "flags", "ok", "resolve_hash"):
            ok = ok and require(key in data, "resolve missing {}".format(key))
        resolve_hash = data.get("resolve_hash")

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "srz.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "300",
        ],
        expect_contains=["DOMINIUM_SRZ_RESOLVE_V1"],
    )
    ok = ok and success
    if success and resolve_hash is not None:
        repeat_hash = parse_kv(output).get("resolve_hash")
        ok = ok and require(repeat_hash == resolve_hash, "determinism hash mismatch")

    malicious_fixture = os.path.join(fixture_root, "malicious_hash.srz")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            malicious_fixture,
            "--region",
            "srz.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "300",
        ],
        expect_contains=["DOMINIUM_SRZ_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & 4, "verification failed flag not set")

    epistemic_fixture = os.path.join(fixture_root, "epistemic_leak.srz")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            epistemic_fixture,
            "--region",
            "srz.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "300",
        ],
        expect_contains=["DOMINIUM_SRZ_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & 8, "epistemic refusal flag not set")

    escalate_fixture = os.path.join(fixture_root, "escalate.srz")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            escalate_fixture,
            "--region",
            "srz.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "300",
        ],
        expect_contains=["DOMINIUM_SRZ_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & 16, "escalation flag not set")

    deescalate_fixture = os.path.join(fixture_root, "deescalate.srz")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            deescalate_fixture,
            "--region",
            "srz.region.core",
            "--tick",
            "5",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_SRZ_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & 32, "deescalation flag not set")

    success, output = run_cmd(
        [
            tool_path,
            "collapse",
            "--fixture",
            base_fixture,
            "--region",
            "srz.region.core",
        ],
        expect_contains=["DOMINIUM_SRZ_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
