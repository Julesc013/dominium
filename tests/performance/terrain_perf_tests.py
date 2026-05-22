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
    parser = argparse.ArgumentParser(description="Terrain T1 perf/scaling tests.")
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

    baseline_cost = None
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
            expect_contains=["DOMINIUM_TERRAIN_WALK_V1"],
        )
        ok = ok and success
        data = parse_kv(output)
        cost_max = int(data.get("cost_step_max", "0"))
        ok = ok and require(cost_max > 0, "cost_step_max missing or zero for {}".format(fixture))
        if baseline_cost is None:
            baseline_cost = cost_max
        else:
            ok = ok and require(cost_max == baseline_cost, "cost drift across fixtures")

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
            "--inactive",
            "64",
        ],
        expect_contains=["DOMINIUM_TERRAIN_WALK_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        inactive_cost = int(data.get("cost_step_max", "0"))
        ok = ok and require(inactive_cost == baseline_cost, "inactive domains changed cost")

    success, output = run_cmd(
        [
            tool_path,
            "render",
            "--fixture",
            earth_fixture,
            "--center",
            "0,0,0",
            "--radius",
            "128",
            "--sample-dim",
            "4",
        ],
        expect_contains=["DOMINIUM_TERRAIN_RENDER_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        visible = int(data.get("visible_chunks", "0"))
        touched = int(data.get("touched_chunks", "0"))
        ok = ok and require(visible > 0, "no visible chunks")
        ok = ok and require(visible == touched, "renderer touched non-visible chunks")

    success, output = run_cmd(
        [
            tool_path,
            "collapse",
            "--fixture",
            earth_fixture,
            "--nav",
            nav_path,
            "--budget",
            "120",
        ],
        expect_contains=["DOMINIUM_TERRAIN_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") == "1", "collapse did not create capsule")
        ok = ok and require(data.get("capsule_count_final") == "0", "expand did not clear capsule")
        inside = data.get("inside_resolution")
        outside = data.get("outside_resolution")
        ok = ok and require(inside is not None and outside is not None, "missing resolution data")
        ok = ok and require(inside == "3", "inside not analytic after collapse")
        ok = ok and require(outside != inside, "outside resolution should differ")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
