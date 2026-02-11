import argparse
import json
import os
import subprocess
import sys
import tempfile


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


def _write_json(path, payload):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _performx(repo_root, output_root, baseline_path):
    cmd = [
        sys.executable,
        os.path.join(repo_root, "tools", "performx", "performx.py"),
        "run",
        "--repo-root",
        repo_root,
        "--output-root",
        output_root,
        "--baseline-path",
        baseline_path,
    ]
    return _run(cmd, cwd=repo_root)


def main():
    parser = argparse.ArgumentParser(description="PerformX regression detection test.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="performx-regression-") as temp_dir:
        output_root = os.path.join(temp_dir, "audit")
        baseline_path = os.path.join(temp_dir, "baseline.json")
        baseline_payload = {
            "artifact_class": "CANONICAL",
            "schema_id": "dominium.schema.governance.performance_result",
            "schema_version": "1.0.0",
            "record": {
                "baseline_id": "performx.baseline",
                "results": [
                    {
                        "envelope_id": "envelope.ensemble.basic",
                        "metrics": [
                            {
                                "metric_id": "wall_time_ms",
                                "normalized_value": 1.0,
                                "raw_value": 1.0,
                                "unit": "ms",
                            }
                        ],
                    }
                ],
                "extensions": {},
            },
        }
        _write_json(baseline_path, baseline_payload)

        result = _performx(repo_root, output_root, baseline_path)
        if result.returncode != 2:
            print("expected critical regression return code 2")
            print(result.stdout)
            return 1

        regressions_path = os.path.join(output_root, "PERFORMX_REGRESSIONS.json")
        if not os.path.isfile(regressions_path):
            print("missing regression artifact")
            return 1
        with open(regressions_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        regressions = payload.get("record", {}).get("regressions", [])
        if not isinstance(regressions, list) or not regressions:
            print("expected at least one regression entry")
            return 1
        severities = sorted({str(item.get("severity", "")).strip() for item in regressions if isinstance(item, dict)})
        if "fail" not in severities and "warn" not in severities:
            print("missing regression severity markers")
            return 1

    print("performx_regression_detection=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

