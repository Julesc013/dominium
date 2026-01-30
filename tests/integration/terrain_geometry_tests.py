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


def count_nav_steps(path):
    count = 0
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("latlon=") or line.startswith("pos="):
                count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Terrain geometry T1 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "terrain")
    nav_path = os.path.join(fixture_root, "terrain_nav.txt")

    fixtures = [
        "earth_like.terrain",
        "asteroid_small.terrain",
        "superflat_slab.terrain",
        "oblique_spheroid.terrain",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "terrain tool missing")
    ok = ok and require(os.path.isfile(nav_path), "nav fixture missing")

    expected_steps = count_nav_steps(nav_path)
    ok = ok and require(expected_steps > 0, "nav fixture empty")

    walk_hashes = {}
    for fixture in fixtures:
        fixture_path = os.path.join(fixture_root, fixture)
        ok = ok and require(os.path.isfile(fixture_path), "missing fixture {}".format(fixture_path))
        if not ok:
            return 1
        success, output = run_cmd(
            [
                tool_path,
                "walk",
                "--fixture",
                fixture_path,
                "--nav",
                nav_path,
                "--budget",
                "120",
            ],
            expect_contains=["DOMINIUM_TERRAIN_WALK_V1", "provider_chain=procedural_base"],
        )
        ok = ok and success
        data = parse_kv(output)
        ok = ok and require("walk_hash" in data, "walk_hash missing")
        ok = ok and require("steps" in data, "steps missing")
        if "steps" in data:
            ok = ok and require(int(data["steps"]) == expected_steps, "step count mismatch")
        if "walk_hash" in data:
            walk_hashes[fixture] = data["walk_hash"]

    earth_fixture = os.path.join(fixture_root, "earth_like.terrain")
    success, output = run_cmd(
        [
            tool_path,
            "walk",
            "--fixture",
            earth_fixture,
            "--nav",
            nav_path,
            "--budget",
            "120",
        ],
        expect_contains=["DOMINIUM_TERRAIN_WALK_V1"],
    )
    ok = ok and success
    if success:
        repeat_hash = parse_kv(output).get("walk_hash")
        ok = ok and require(repeat_hash == walk_hashes.get("earth_like.terrain"), "determinism hash mismatch")

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            earth_fixture,
            "--nav",
            nav_path,
            "--index",
            "0",
            "--budget",
            "120",
        ],
        expect_contains=["DOMINIUM_TERRAIN_INSPECT_V1", "provider_chain=procedural_base"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "phi_q16",
            "material_primary",
            "roughness_q16",
            "slope_q16",
            "travel_cost_q16",
        ):
            ok = ok and require(key in data, "inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            earth_fixture,
            "--nav",
            nav_path,
            "--index",
            "0",
            "--budget",
            "0",
        ],
        expect_contains=["DOMINIUM_TERRAIN_INSPECT_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        unknown = data.get("fields_unknown") == "1" or data.get("phi_unknown") == "1"
        ok = ok and require(unknown, "expected unknown fields under zero budget")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
