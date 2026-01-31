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
    parser = argparse.ArgumentParser(description="Standards T23 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "standards")

    fixtures = [
        "baseline.standard",
        "fragmented.standard",
        "lockin_bridge.standard",
        "revocation.standard",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "standard tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "standard fixtures missing")

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
                "DOMINIUM_STANDARD_VALIDATE_V1",
                "provider_chain=definitions->versions->scopes->events->tools->edges->graphs",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "baseline.standard")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--definition",
            "standard.core.measurement",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_INSPECT_V1", "entity=definition"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("standard_id", "current_version_id", "adoption_req_count", "flags"):
            ok = ok and require(key in data, "definition inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--version",
            "standard.version.metric.v1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_INSPECT_V1", "entity=version"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("version_id", "compatibility_score_q16", "status", "flags"):
            ok = ok and require(key in data, "version inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--scope",
            "standard.scope.primary",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_INSPECT_V1", "entity=scope"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("adoption_rate_q16", "compliance_rate_q16", "lock_in_index_q16", "flags"):
            ok = ok and require(key in data, "scope inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--event",
            "standard.event.adopt",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_INSPECT_V1", "entity=event"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("process_type", "delta_adoption_q16", "event_tick", "flags"):
            ok = ok and require(key in data, "event inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--tool",
            "tool.compiler.metric",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_INSPECT_V1", "entity=tool"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("tool_id", "capacity_q48", "error_rate_q16", "flags"):
            ok = ok and require(key in data, "tool inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--edge",
            "toolchain.edge.compiler_to_cert",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_INSPECT_V1", "entity=edge"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("compatibility_score_q16" in data, "edge inspect missing compatibility_score_q16")

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--graph",
            "toolchain.graph.metric",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_INSPECT_V1", "entity=graph"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("node_count" in data, "graph inspect missing node_count")

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "standard.region.primary",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_INSPECT_V1", "entity=region"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in ("definition_count", "scope_count", "compatibility_avg_q16", "flags"):
            ok = ok and require(key in data, "region inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "standard.region.primary",
            "--tick",
            "50",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_RESOLVE_V1"],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in ("scope_count", "event_applied_count", "flags", "ok", "resolve_hash"):
            ok = ok and require(key in data, "resolve missing {}".format(key))
        resolve_hash = data.get("resolve_hash")

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "standard.region.primary",
            "--tick",
            "50",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_RESOLVE_V1"],
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
            "standard.region.primary",
        ],
        expect_contains=["DOMINIUM_STANDARD_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    flag_lockin = 1 << 4
    flag_revocation = 1 << 5

    lockin_fixture = os.path.join(fixture_root, "lockin_bridge.standard")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            lockin_fixture,
            "--region",
            "standard.region.primary",
            "--tick",
            "50",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & flag_lockin, "lock-in fixture missing lock-in flag")

    revoke_fixture = os.path.join(fixture_root, "revocation.standard")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            revoke_fixture,
            "--region",
            "standard.region.primary",
            "--tick",
            "50",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_STANDARD_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & flag_revocation, "revocation fixture missing revocation flag")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
