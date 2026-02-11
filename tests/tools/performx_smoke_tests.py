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


def _performx(repo_root, args, env=None):
    cmd = [sys.executable, os.path.join(repo_root, "tools", "performx", "performx.py")]
    cmd.extend(args)
    cmd.extend(["--repo-root", repo_root])
    return _run(cmd, cwd=repo_root, env=env)


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    parser = argparse.ArgumentParser(description="PerformX smoke test.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    result = _performx(repo_root, ["run"])
    if result.returncode != 0:
        print(result.stdout)
        return 1

    try:
        payload = json.loads(result.stdout or "{}")
    except ValueError:
        print(result.stdout)
        return 1

    if payload.get("result") != "complete":
        print(result.stdout)
        return 1

    artifacts = (
        "docs/audit/performance/PERFORMX_RESULTS.json",
        "docs/audit/performance/PERFORMX_REGRESSIONS.json",
        "docs/audit/performance/RUN_META.json",
    )
    for rel in artifacts:
        path = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            print("missing artifact {}".format(rel))
            return 1
        loaded = _load_json(path)
        if not isinstance(loaded, dict):
            print("invalid json {}".format(rel))
            return 1

    results_payload = _load_json(os.path.join(repo_root, "docs", "audit", "performance", "PERFORMX_RESULTS.json"))
    regressions_payload = _load_json(os.path.join(repo_root, "docs", "audit", "performance", "PERFORMX_REGRESSIONS.json"))
    if str(results_payload.get("artifact_class", "")).strip() != "CANONICAL":
        print("unexpected artifact_class for results")
        return 1
    if str(regressions_payload.get("artifact_class", "")).strip() != "CANONICAL":
        print("unexpected artifact_class for regressions")
        return 1

    print("performx_smoke=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

