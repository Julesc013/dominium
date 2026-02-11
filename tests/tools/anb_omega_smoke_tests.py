import argparse
import json
import os
import subprocess
import sys


def _run(cmd, cwd, env=None):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    parser = argparse.ArgumentParser(description="ANB-OMEGA stress harness smoke tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    tool = os.path.join(repo_root, "tools", "system", "anb_omega.py")
    if not os.path.isfile(tool):
        print("missing tool {}".format(tool))
        return 1

    baseline = _run([sys.executable, tool, "baseline", "--repo-root", repo_root, "--workspace-id", "anb-omega-smoke"], cwd=repo_root)
    if baseline.returncode != 0:
        print(baseline.stdout)
        return 1

    stress_env = dict(os.environ)
    stress_env["ANB_OMEGA_SMOKE"] = "1"
    stress = _run(
        [sys.executable, tool, "stress", "--repo-root", repo_root, "--workspace-id", "anb-omega-smoke", "--quick"],
        cwd=repo_root,
        env=stress_env,
    )
    if stress.returncode not in (0, 1):
        print(stress.stdout)
        return 1

    baseline_state = os.path.join(repo_root, "docs", "audit", "system", "BASELINE_STATE.json")
    baseline_meta = os.path.join(repo_root, "docs", "audit", "system", "BASELINE_META.json")
    stress_matrix = os.path.join(repo_root, "docs", "audit", "system", "STRESS_MATRIX.json")
    omega_report = os.path.join(repo_root, "docs", "audit", "system", "ANB_OMEGA_REPORT.md")
    portability_report = os.path.join(repo_root, "docs", "audit", "system", "PORTABILITY_REPORT.md")

    required_paths = (baseline_state, baseline_meta, stress_matrix, omega_report, portability_report)
    for path in required_paths:
        if not os.path.isfile(path):
            print("missing expected artifact {}".format(path))
            return 1

    state_payload = _load_json(baseline_state)
    matrix_payload = _load_json(stress_matrix)

    if str(state_payload.get("artifact_class", "")).strip() != "CANONICAL":
        print("baseline state is not CANONICAL")
        return 1
    scenarios = matrix_payload.get("record", {}).get("scenarios", [])
    if not isinstance(scenarios, list) or not scenarios:
        print("stress matrix scenarios missing")
        return 1
    for row in scenarios:
        if not isinstance(row, dict):
            print("invalid scenario row in stress matrix")
            return 1
        if "scenario_id" not in row or "status" not in row:
            print("scenario row missing keys")
            return 1

    print("anb_omega_smoke_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
