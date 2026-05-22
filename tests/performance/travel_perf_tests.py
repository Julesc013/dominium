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
    parser = argparse.ArgumentParser(description="Travel T8 perf/scaling tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "travel")

    fixtures = [
        "earth_like.travel",
        "asteroid_small.travel",
        "superflat_slab.travel",
        "oblique_spheroid.travel",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "travel tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "travel fixtures missing")

    baseline_cost = None
    for fixture in fixtures:
        fixture_path = os.path.join(fixture_root, fixture)
        ok = ok and require(os.path.isfile(fixture_path), "missing fixture {}".format(fixture_path))
        if not ok:
            return 1
        success, output = run_cmd(
            [
                tool_path,
                "core-sample",
                "--fixture",
                fixture_path,
                "--origin",
                "0,0,0",
                "--dir",
                "1,0,0",
                "--length",
                "64",
                "--steps",
                "16",
                "--start",
                "0",
                "--step_ticks",
                "10",
                "--mode",
                "travel.mode.walk",
                "--budget",
                "40",
            ],
            expect_contains=["DOMINIUM_TRAVEL_CORE_SAMPLE_V1"],
        )
        ok = ok and success
        data = parse_kv(output)
        cost_max = int(data.get("cost_step_max", "0"))
        ok = ok and require(cost_max > 0, "cost_step_max missing or zero for {}".format(fixture))
        if baseline_cost is None:
            baseline_cost = cost_max
        else:
            ok = ok and require(cost_max == baseline_cost, "cost drift across fixtures")

    base_fixture = os.path.join(fixture_root, "earth_like.travel")
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
            "--start",
            "0",
            "--step_ticks",
            "10",
            "--mode",
            "travel.mode.walk",
            "--budget",
            "40",
            "--inactive",
            "64",
        ],
        expect_contains=["DOMINIUM_TRAVEL_CORE_SAMPLE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        inactive_cost = int(data.get("cost_step_max", "0"))
        ok = ok and require(inactive_cost == baseline_cost, "inactive domains changed cost")

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
            "8",
            "--start",
            "0",
            "--step_ticks",
            "10",
            "--mode",
            "travel.mode.walk",
            "--budget",
            "40",
            "--collapsed",
            "1",
        ],
        expect_contains=["DOMINIUM_TRAVEL_CORE_SAMPLE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count") != "0", "collapsed tile not recorded")
        unknown_steps = int(data.get("unknown_steps", "0"))
        ok = ok and require(unknown_steps > 0, "expected unknown steps under collapse")

    success, output = run_cmd(
        [
            tool_path,
            "render",
            "--fixture",
            base_fixture,
            "--center",
            "0,0,0",
            "--radius",
            "64",
            "--dim",
            "8",
            "--tick",
            "0",
            "--mode",
            "travel.mode.walk",
            "--budget",
            "40",
        ],
        expect_contains=["DOMINIUM_TRAVEL_RENDER_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("visible_cells") == data.get("touched_cells"), "render touched invisible cells")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
