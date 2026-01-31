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
    parser = argparse.ArgumentParser(description="Animal T6 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "animal")

    fixtures = [
        "planet_like.animal",
        "oblate_world.animal",
        "superflat_slab.animal",
        "asteroid_tiny.animal",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "animal tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "animal fixtures missing")

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
            expect_contains=["DOMINIUM_ANIMAL_VALIDATE_V1", "provider_chain=terrain->climate->weather->geology->vegetation->animal"],
        )
        ok = ok and success

    planet_fixture = os.path.join(fixture_root, "planet_like.animal")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            planet_fixture,
            "--pos",
            "0,0,511",
            "--tick",
            "0",
            "--budget",
            "600",
        ],
        expect_contains=["DOMINIUM_ANIMAL_INSPECT_V1", "provider_chain=terrain->climate->weather->geology->vegetation->animal"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "suitability_q16",
            "biome_id",
            "vegetation_coverage_q16",
            "vegetation_consumed_q16",
            "agent_present",
            "species_id",
            "energy_q16",
            "health_q16",
            "age_ticks",
            "need",
            "death_reason",
            "fields_unknown",
        ):
            ok = ok and require(key in data, "inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            planet_fixture,
            "--pos",
            "0,0,511",
            "--tick",
            "0",
            "--budget",
            "0",
        ],
        expect_contains=["DOMINIUM_ANIMAL_INSPECT_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("fields_unknown") == "1", "expected unknown fields under zero budget")

    success, output = run_cmd(
        [
            tool_path,
            "core-sample",
            "--fixture",
            planet_fixture,
            "--origin",
            "0,0,511",
            "--dir",
            "0,0,1",
            "--length",
            "128",
            "--steps",
            "16",
            "--start",
            "0",
            "--step_ticks",
            "10",
            "--budget",
            "600",
        ],
        expect_contains=["DOMINIUM_ANIMAL_CORE_SAMPLE_V1", "provider_chain=terrain->climate->weather->geology->vegetation->animal"],
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
            "0,0,511",
            "--dir",
            "0,0,1",
            "--length",
            "128",
            "--steps",
            "16",
            "--start",
            "0",
            "--step_ticks",
            "10",
            "--budget",
            "600",
        ],
        expect_contains=["DOMINIUM_ANIMAL_CORE_SAMPLE_V1"],
    )
    ok = ok and success
    if success and sample_hash is not None:
        repeat_hash = parse_kv(output).get("sample_hash")
        ok = ok and require(repeat_hash == sample_hash, "determinism hash mismatch")

    other_fixture = os.path.join(fixture_root, "oblate_world.animal")
    success, output = run_cmd(
        [
            tool_path,
            "diff",
            "--fixture-a",
            planet_fixture,
            "--fixture-b",
            other_fixture,
            "--origin",
            "0,0,511",
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
            "600",
        ],
        expect_contains=["DOMINIUM_ANIMAL_DIFF_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("hash_a" in data, "diff missing hash_a")
        ok = ok and require("hash_b" in data, "diff missing hash_b")
        ok = ok and require("equal" in data, "diff missing equal flag")

    success, output = run_cmd(
        [
            tool_path,
            "collapse",
            "--fixture",
            planet_fixture,
            "--pos",
            "0,0,511",
            "--tick",
            "0",
            "--budget",
            "600",
        ],
        expect_contains=["DOMINIUM_ANIMAL_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
