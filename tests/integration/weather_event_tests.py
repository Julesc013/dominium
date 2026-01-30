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
    parser = argparse.ArgumentParser(description="Weather T4 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "weather")

    fixtures = [
        "planet_like.weather",
        "oblate_world.weather",
        "superflat_slab.weather",
        "asteroid_tiny.weather",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "weather tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "weather fixtures missing")

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
            expect_contains=["DOMINIUM_WEATHER_VALIDATE_V1", "provider_chain=climate_envelope->weather_event->cache"],
        )
        ok = ok and success

    planet_fixture = os.path.join(fixture_root, "planet_like.weather")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            planet_fixture,
            "--pos",
            "0,0,0",
            "--tick",
            "0",
            "--budget",
            "40",
        ],
        expect_contains=["DOMINIUM_WEATHER_INSPECT_V1", "provider_chain=climate_envelope->weather_event->cache"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "temperature_current_q16",
            "precipitation_current_q16",
            "surface_wetness_q16",
            "wind_current",
            "active_event_count",
            "active_event_mask",
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
            "--tick",
            "0",
            "--budget",
            "0",
        ],
        expect_contains=["DOMINIUM_WEATHER_INSPECT_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("fields_unknown") == "1", "expected unknown fields under zero budget")

    success, output = run_cmd(
        [
            tool_path,
            "list",
            "--fixture",
            planet_fixture,
            "--start",
            "0",
            "--window",
            "256",
        ],
        expect_contains=["DOMINIUM_WEATHER_LIST_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("event_hash" in data, "list missing event_hash")

    success, output = run_cmd(
        [
            tool_path,
            "step",
            "--fixture",
            planet_fixture,
            "--pos",
            "0,0,0",
            "--start",
            "0",
            "--steps",
            "8",
            "--step_ticks",
            "10",
            "--budget",
            "40",
        ],
        expect_contains=["DOMINIUM_WEATHER_STEP_V1"],
    )
    ok = ok and success
    step_hash = None
    if success:
        data = parse_kv(output)
        ok = ok and require("sample_hash" in data, "step missing hash")
        step_hash = data.get("sample_hash")

    success, output = run_cmd(
        [
            tool_path,
            "step",
            "--fixture",
            planet_fixture,
            "--pos",
            "0,0,0",
            "--start",
            "0",
            "--steps",
            "8",
            "--step_ticks",
            "10",
            "--budget",
            "40",
        ],
        expect_contains=["DOMINIUM_WEATHER_STEP_V1"],
    )
    ok = ok and success
    if success and step_hash is not None:
        repeat_hash = parse_kv(output).get("sample_hash")
        ok = ok and require(repeat_hash == step_hash, "determinism hash mismatch")

    other_fixture = os.path.join(fixture_root, "oblate_world.weather")
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
            "--start",
            "0",
            "--step_ticks",
            "10",
            "--budget",
            "40",
        ],
        expect_contains=["DOMINIUM_WEATHER_DIFF_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("equal") == "0", "expected diff between fixtures")

    success, output = run_cmd(
        [
            tool_path,
            "collapse",
            "--fixture",
            planet_fixture,
            "--pos",
            "0,0,0",
            "--start",
            "0",
            "--window",
            "64",
            "--budget",
            "40",
        ],
        expect_contains=["DOMINIUM_WEATHER_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
