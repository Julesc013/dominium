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
    parser = argparse.ArgumentParser(description="Structure T7 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "structure")

    fixtures = [
        "earth_like.structure",
        "asteroid_small.structure",
        "superflat_slab.structure",
        "oblique_spheroid.structure",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "structure tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "structure fixtures missing")

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
                "DOMINIUM_STRUCTURE_VALIDATE_V1",
                "provider_chain=terrain->geology->structure",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "earth_like.structure")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--pos",
            "0,0,479",
            "--tick",
            "0",
            "--budget",
            "600",
        ],
        expect_contains=[
            "DOMINIUM_STRUCTURE_INSPECT_V1",
            "provider_chain=terrain->geology->structure",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "structure_present",
            "structure_id",
            "support_capacity_q16",
            "applied_stress_q16",
            "stress_ratio_q16",
            "integrity_q16",
            "anchor_required_mask",
            "anchor_supported_mask",
            "flags",
            "fields_unknown",
            "collapsed",
            "unstable",
            "meta.status",
            "meta.resolution",
            "meta.confidence",
            "meta.refusal_reason",
            "meta.cost_units",
            "budget.used",
            "budget.max",
        ):
            ok = ok and require(key in data, "inspect missing {}".format(key))
        ok = ok and require(data.get("structure_present") == "1", "expected structure_present=1")

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--pos",
            "0,0,479",
            "--tick",
            "0",
            "--budget",
            "0",
        ],
        expect_contains=["DOMINIUM_STRUCTURE_INSPECT_V1"],
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
            base_fixture,
            "--origin",
            "0,0,0",
            "--dir",
            "0,0,1",
            "--length",
            "64",
            "--steps",
            "16",
            "--start",
            "0",
            "--step_ticks",
            "10",
            "--budget",
            "600",
        ],
        expect_contains=[
            "DOMINIUM_STRUCTURE_CORE_SAMPLE_V1",
            "provider_chain=terrain->geology->structure",
        ],
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
            base_fixture,
            "--origin",
            "0,0,0",
            "--dir",
            "0,0,1",
            "--length",
            "64",
            "--steps",
            "16",
            "--start",
            "0",
            "--step_ticks",
            "10",
            "--budget",
            "600",
        ],
        expect_contains=["DOMINIUM_STRUCTURE_CORE_SAMPLE_V1"],
    )
    ok = ok and success
    if success and sample_hash is not None:
        repeat_hash = parse_kv(output).get("sample_hash")
        ok = ok and require(repeat_hash == sample_hash, "determinism hash mismatch")

    other_fixture = os.path.join(fixture_root, "oblique_spheroid.structure")
    success, output = run_cmd(
        [
            tool_path,
            "diff",
            "--fixture-a",
            base_fixture,
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
            "600",
        ],
        expect_contains=["DOMINIUM_STRUCTURE_DIFF_V1"],
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
            base_fixture,
            "--pos",
            "0,0,479",
            "--tick",
            "0",
            "--budget",
            "600",
        ],
        expect_contains=["DOMINIUM_STRUCTURE_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    success, output = run_cmd(
        [
            tool_path,
            "failure",
            "--fixture",
            base_fixture,
            "--pos",
            "0,0,479",
            "--tick",
            "0",
        ],
        expect_contains=["DOMINIUM_STRUCTURE_FAILURE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("overlay_kind" in data, "failure missing overlay_kind")
        ok = ok and require("delta_phi_q16" in data, "failure missing delta_phi_q16")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
