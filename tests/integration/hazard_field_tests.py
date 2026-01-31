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
    parser = argparse.ArgumentParser(description="Hazard T15 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "hazard")

    fixtures = [
        "containment_breach.hazard",
        "pressure_leak.hazard",
        "radiation_zone.hazard",
        "info_spill.hazard",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "hazard tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "hazard fixtures missing")

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
                "DOMINIUM_HAZARD_VALIDATE_V1",
                "provider_chain=types->fields->exposures",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "containment_breach.hazard")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--type",
            "hazard.type.fire",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_HAZARD_INSPECT_V1",
            "entity=type",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "type_id",
            "hazard_class",
            "default_intensity_q16",
            "default_exposure_rate_q16",
            "default_decay_rate_q16",
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
            "hazard.field.fire_valve",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_HAZARD_INSPECT_V1",
            "entity=field",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "hazard_id",
            "hazard_type_id",
            "intensity_q16",
            "exposure_rate_q16",
            "decay_rate_q16",
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
            "hazard.exposure.sensor_a",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_HAZARD_INSPECT_V1",
            "entity=exposure",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "exposure_id",
            "hazard_type_id",
            "exposure_limit_q48",
            "sensitivity_q16",
            "uncertainty_q16",
            "region_id",
            "exposure_accumulated_q48",
            "flags",
        ):
            ok = ok and require(key in data, "exposure inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "hazard.region.primary",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_HAZARD_INSPECT_V1",
            "entity=region",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "field_count",
            "exposure_count",
            "hazard_energy_total_q48",
            "exposure_total_q48",
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
            "hazard.region.primary",
            "--tick",
            "0",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_HAZARD_RESOLVE_V1",
            "provider_chain=types->fields->exposures",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "field_count",
            "exposure_count",
            "hazard_energy_total_q48",
            "exposure_total_q48",
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
            "hazard.region.primary",
            "--tick",
            "0",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HAZARD_RESOLVE_V1"],
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
            "hazard.region.primary",
        ],
        expect_contains=["DOMINIUM_HAZARD_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
