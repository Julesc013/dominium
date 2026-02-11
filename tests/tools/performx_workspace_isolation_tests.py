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


def _performx(repo_root, output_root, workspace_id):
    env = dict(os.environ)
    env["DOM_WS_ID"] = workspace_id
    cmd = [
        sys.executable,
        os.path.join(repo_root, "tools", "performx", "performx.py"),
        "run",
        "--repo-root",
        repo_root,
        "--output-root",
        output_root,
    ]
    return _run(cmd, cwd=repo_root, env=env)


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    parser = argparse.ArgumentParser(description="PerformX workspace isolation test.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="performx-ws-") as temp_dir:
        out_a = os.path.join(temp_dir, "ws_a")
        out_b = os.path.join(temp_dir, "ws_b")
        first = _performx(repo_root, out_a, "ws-alpha")
        if first.returncode != 0:
            print(first.stdout)
            return 1
        second = _performx(repo_root, out_b, "ws-beta")
        if second.returncode != 0:
            print(second.stdout)
            return 1

        run_meta_a = _load_json(os.path.join(out_a, "RUN_META.json"))
        run_meta_b = _load_json(os.path.join(out_b, "RUN_META.json"))
        ws_a = str(run_meta_a.get("workspace_id", "")).strip()
        ws_b = str(run_meta_b.get("workspace_id", "")).strip()
        if not ws_a or not ws_b:
            print("workspace ids missing in run metadata")
            return 1
        if ws_a == ws_b:
            print("workspace ids should differ between isolated runs")
            return 1

        results_a = os.path.join(out_a, "PERFORMX_RESULTS.json")
        results_b = os.path.join(out_b, "PERFORMX_RESULTS.json")
        if not os.path.isfile(results_a) or not os.path.isfile(results_b):
            print("workspace output artifacts missing")
            return 1

    print("performx_workspace_isolation=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

