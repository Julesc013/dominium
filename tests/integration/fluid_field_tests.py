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
    parser = argparse.ArgumentParser(description="Fluid T13 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "fluid")

    fixtures = [
        "tank_leak.fluid",
        "pipe_breach.fluid",
        "cavern_flood.fluid",
        "gas_decompression.fluid",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "fluid tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "fluid fixtures missing")

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
                "DOMINIUM_FLUID_VALIDATE_V1",
                "provider_chain=stores->flows->pressure",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "tank_leak.fluid")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--store",
            "fluid.store.tank_a",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_FLUID_INSPECT_V1",
            "entity=store",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "store_id",
            "volume_q48",
            "max_volume_q48",
            "temperature_q48",
            "contamination_q16",
            "network_id",
            "flags",
            "meta.status",
            "meta.resolution",
            "meta.refusal_reason",
            "budget.used",
            "budget.max",
        ):
            ok = ok and require(key in data, "store inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--flow",
            "fluid.flow.a_to_b",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_FLUID_INSPECT_V1",
            "entity=flow",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "flow_id",
            "source_store_id",
            "sink_store_id",
            "max_rate_q48",
            "efficiency_q16",
            "flags",
            "meta.status",
            "budget.used",
        ):
            ok = ok and require(key in data, "flow inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--pressure",
            "fluid.pressure.tank_a",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_FLUID_INSPECT_V1",
            "entity=pressure",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "pressure_id",
            "store_id",
            "amount_q48",
            "limit_q48",
            "rupture_threshold_q48",
            "release_ratio_q16",
            "flags",
        ):
            ok = ok and require(key in data, "pressure inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--property",
            "fluid.prop.water",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_FLUID_INSPECT_V1",
            "entity=property",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "property_id",
            "fluid_type",
            "density_q48",
            "viscosity_class",
            "compressibility_class",
            "flags",
        ):
            ok = ok and require(key in data, "property inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--network",
            "fluid.net.primary",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_FLUID_INSPECT_V1",
            "entity=network",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "store_count",
            "flow_count",
            "volume_total_q48",
            "capacity_total_q48",
            "pressure_total_q48",
            "contamination_avg_q16",
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
            "fluid.net.primary",
            "--tick",
            "0",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_FLUID_RESOLVE_V1",
            "provider_chain=stores->flows->pressure",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "volume_transferred_q48",
            "volume_leaked_q48",
            "volume_remaining_q48",
            "energy_required_q48",
            "pressure_count",
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
            "fluid.net.primary",
            "--tick",
            "0",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_FLUID_RESOLVE_V1"],
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
            "fluid.net.primary",
        ],
        expect_contains=["DOMINIUM_FLUID_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
