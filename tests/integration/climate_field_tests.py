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
    parser = argparse.ArgumentParser(description="Climate T3 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "climate")

    fixtures = [
        "planet_like.climate",
        "oblate_world.climate",
        "superflat_slab.climate",
        "asteroid_tiny.climate",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "climate tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "climate fixtures missing")

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
            expect_contains=["DOMINIUM_CLIMATE_VALIDATE_V1", "provider_chain=procedural_base"],
        )
        ok = ok and success

    planet_fixture = os.path.join(fixture_root, "planet_like.climate")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            planet_fixture,
            "--pos",
            "0,0,0",
            "--budget",
            "120",
        ],
        expect_contains=["DOMINIUM_CLIMATE_INSPECT_V1", "provider_chain=procedural_base"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "temperature_mean_q16",
            "temperature_range_q16",
            "precipitation_mean_q16",
            "precipitation_range_q16",
            "seasonality_q16",
            "wind_prevailing",
            "biome_id",
            "biome_confidence_q16",
        ):
            ok = ok and require(key in data, "inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            planet_fixture,
            "--pos",
            "0,0,0",
            "--budget",
            "0",
        ],
        expect_contains=["DOMINIUM_CLIMATE_INSPECT_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        unknown = data.get("fields_unknown") == "1"
        ok = ok and require(unknown, "expected unknown fields under zero budget")

    success, output = run_cmd(
        [
            tool_path,
            "core-sample",
            "--fixture",
            planet_fixture,
            "--origin",
            "0,0,0",
            "--dir",
            "0,0,1",
            "--length",
            "128",
            "--steps",
            "16",
            "--budget",
            "120",
        ],
        expect_contains=["DOMINIUM_CLIMATE_CORE_SAMPLE_V1", "provider_chain=procedural_base"],
    )
    ok = ok and success
    sample_hash = None
    if success:
        data = parse_kv(output)
        ok = ok and require("unknown_steps" in data, "core-sample missing unknown_steps")
        ok = ok and require("sample_hash" in data, "core-sample missing sample_hash")
        sample_hash = data.get("sample_hash")

    success, output = run_cmd(
        [
            tool_path,
            "core-sample",
            "--fixture",
            planet_fixture,
            "--origin",
            "0,0,0",
            "--dir",
            "0,0,1",
            "--length",
            "128",
            "--steps",
            "16",
            "--budget",
            "120",
        ],
        expect_contains=["DOMINIUM_CLIMATE_CORE_SAMPLE_V1"],
    )
    ok = ok and success
    if success and sample_hash is not None:
        repeat_hash = parse_kv(output).get("sample_hash")
        ok = ok and require(repeat_hash == sample_hash, "determinism hash mismatch")

    success, output = run_cmd(
        [
            tool_path,
            "map",
            "--fixture",
            planet_fixture,
            "--center-latlon",
            "0,0",
            "--span",
            "0.1",
            "--dim",
            "6",
            "--budget",
            "40",
        ],
        expect_contains=["DOMINIUM_CLIMATE_MAP_V1", "provider_chain=procedural_base"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("map_hash" in data, "map missing hash")
        ok = ok and require(int(data.get("cells", "0")) > 0, "map missing cells")

    success, output = run_cmd(
        [
            tool_path,
            "slice",
            "--fixture",
            planet_fixture,
            "--field",
            "temp_mean",
            "--center",
            "0,0,0",
            "--radius",
            "32",
            "--dim",
            "6",
            "--budget",
            "40",
        ],
        expect_contains=["DOMINIUM_CLIMATE_SLICE_V1", "provider_chain=procedural_base"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("slice_hash" in data, "slice missing hash")
        ok = ok and require("min_q16" in data, "slice missing min")
        ok = ok and require("max_q16" in data, "slice missing max")

    other_fixture = os.path.join(fixture_root, "oblate_world.climate")
    success, output = run_cmd(
        [
            tool_path,
            "diff",
            "--fixture-a",
            planet_fixture,
            "--fixture-b",
            other_fixture,
            "--origin",
            "0,0,0",
            "--dir",
            "0,0,1",
            "--length",
            "64",
            "--steps",
            "8",
            "--budget",
            "40",
        ],
        expect_contains=["DOMINIUM_CLIMATE_DIFF_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("equal") == "0", "expected diff between fixtures")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
