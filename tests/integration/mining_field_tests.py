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
    parser = argparse.ArgumentParser(description="Mining T9 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "mining")

    fixtures = [
        "earth_like.mining",
        "asteroid_small.mining",
        "superflat_slab.mining",
        "oblique_spheroid.mining",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "mining tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "mining fixtures missing")

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
                "DOMINIUM_MINING_VALIDATE_V1",
                "provider_chain=terrain->geology->mining",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "earth_like.mining")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--pos",
            "0,0,0",
            "--budget",
            "400",
        ],
        expect_contains=[
            "DOMINIUM_MINING_INSPECT_V1",
            "provider_chain=terrain->geology->mining",
        ],
    )
    ok = ok and success
    phi_before = None
    density_before = None
    if success:
        data = parse_kv(output)
        for key in (
            "phi_q16",
            "support_capacity_q16",
            "flags",
            "overlay_count",
            "chunk_count",
            "resource_count",
            "meta.status",
            "meta.resolution",
            "meta.confidence",
            "meta.refusal_reason",
            "meta.cost_units",
            "budget.used",
            "budget.max",
        ):
            ok = ok and require(key in data, "inspect missing {}".format(key))
        phi_before = int(data.get("phi_q16", "0"))
        density_before = int(data.get("resource.0.density_q16", "0"))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--pos",
            "0,0,0",
            "--budget",
            "400",
            "--cuts",
            "1",
            "--cut_radius",
            "4",
            "--tick",
            "10",
        ],
        expect_contains=["DOMINIUM_MINING_INSPECT_V1"],
    )
    ok = ok and success
    if success and phi_before is not None:
        phi_after = int(parse_kv(output).get("phi_q16", "0"))
        ok = ok and require(phi_after > phi_before, "expected cut to raise phi")

    success, output = run_cmd(
        [
            tool_path,
            "extract",
            "--fixture",
            base_fixture,
            "--pos",
            "0,0,0",
            "--radius",
            "3",
            "--tick",
            "20",
            "--budget",
            "400",
            "--repeat",
            "2",
        ],
        expect_contains=["DOMINIUM_MINING_EXTRACT_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        flags = int(data.get("flags", "0"))
        ok = ok and require("resource_chunks" in data, "extract missing resource_chunks")
        ok = ok and require("tailings_chunks" in data, "extract missing tailings_chunks")
        ok = ok and require(flags & 4, "expected depleted flag after repeat extraction")

    if density_before is not None:
        success, output = run_cmd(
            [
                tool_path,
                "inspect",
                "--fixture",
                base_fixture,
                "--pos",
                "0,0,0",
                "--budget",
                "400",
                "--cuts",
                "0",
            ],
            expect_contains=["DOMINIUM_MINING_INSPECT_V1"],
        )
        ok = ok and success
        if success:
            density_after = int(parse_kv(output).get("resource.0.density_q16", "0"))
            ok = ok and require(density_after == density_before, "expected baseline density unchanged without extraction")

    success, output = run_cmd(
        [
            tool_path,
            "support-check",
            "--fixture",
            base_fixture,
            "--pos",
            "0,0,0",
            "--radius",
            "8",
            "--tick",
            "40",
        ],
        expect_contains=["DOMINIUM_MINING_SUPPORT_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("collapse_risk" in data, "support-check missing collapse_risk")

    success, output = run_cmd(
        [
            tool_path,
            "collapse",
            "--fixture",
            base_fixture,
            "--pos",
            "0,0,0",
            "--radius",
            "8",
            "--tick",
            "50",
        ],
        expect_contains=["DOMINIUM_MINING_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(int(data.get("overlay_count", "0")) > 0, "collapse did not add overlay")

    success, output = run_cmd(
        [
            tool_path,
            "core-sample",
            "--fixture",
            base_fixture,
            "--origin",
            "0,0,0",
            "--dir",
            "1,0,0",
            "--length",
            "64",
            "--steps",
            "16",
            "--budget",
            "400",
        ],
        expect_contains=["DOMINIUM_MINING_CORE_SAMPLE_V1"],
    )
    ok = ok and success
    sample_hash = None
    if success:
        sample_hash = parse_kv(output).get("sample_hash")

    success, output = run_cmd(
        [
            tool_path,
            "core-sample",
            "--fixture",
            base_fixture,
            "--origin",
            "0,0,0",
            "--dir",
            "1,0,0",
            "--length",
            "64",
            "--steps",
            "16",
            "--budget",
            "400",
        ],
        expect_contains=["DOMINIUM_MINING_CORE_SAMPLE_V1"],
    )
    ok = ok and success
    if success and sample_hash is not None:
        repeat_hash = parse_kv(output).get("sample_hash")
        ok = ok and require(repeat_hash == sample_hash, "determinism hash mismatch")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
