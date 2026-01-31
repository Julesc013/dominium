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
    parser = argparse.ArgumentParser(description="Network T14 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "network")

    fixtures = [
        "embedded_device.network",
        "city_grid.network",
        "planetary_backbone.network",
        "interplanetary_link.network",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "network tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "network fixtures missing")

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
                "DOMINIUM_NETWORK_VALIDATE_V1",
                "provider_chain=nodes->links->data",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "embedded_device.network")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--node",
            "net.node.router",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_NETWORK_INSPECT_V1",
            "entity=node",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "node_id",
            "node_type",
            "compute_capacity_q48",
            "storage_capacity_q48",
            "energy_per_unit_q48",
            "heat_per_unit_q48",
            "network_id",
            "flags",
            "meta.status",
            "budget.used",
        ):
            ok = ok and require(key in data, "node inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--link",
            "net.link.router_compute",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_NETWORK_INSPECT_V1",
            "entity=link",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "link_id",
            "node_a_id",
            "node_b_id",
            "capacity_id",
            "bandwidth_limit_q48",
            "latency_class",
            "error_rate_q16",
            "congestion_policy",
            "flags",
            "meta.status",
        ):
            ok = ok and require(key in data, "link inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--capacity",
            "net.cap.fast",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_NETWORK_INSPECT_V1",
            "entity=capacity",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "capacity_id",
            "bandwidth_limit_q48",
            "latency_class",
            "error_rate_q16",
            "congestion_policy",
            "flags",
        ):
            ok = ok and require(key in data, "capacity inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--data",
            "net.data.boot",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_NETWORK_INSPECT_V1",
            "entity=data",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "data_id",
            "data_type",
            "data_size_q48",
            "data_uncertainty_q16",
            "source_node_id",
            "sink_node_id",
            "network_id",
            "flags",
        ):
            ok = ok and require(key in data, "data inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--network",
            "net.primary",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_NETWORK_INSPECT_V1",
            "entity=network",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "node_count",
            "link_count",
            "data_count",
            "data_total_q48",
            "queued_count",
            "dropped_count",
            "flags",
        ):
            ok = ok and require(key in data, "network inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--network",
            "net.primary",
            "--tick",
            "0",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_NETWORK_RESOLVE_V1",
            "provider_chain=nodes->links->data",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "delivered_count",
            "dropped_count",
            "queued_count",
            "energy_cost_q48",
            "heat_generated_q48",
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
            "--network",
            "net.primary",
            "--tick",
            "0",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_NETWORK_RESOLVE_V1"],
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
            "--network",
            "net.primary",
        ],
        expect_contains=["DOMINIUM_NETWORK_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
