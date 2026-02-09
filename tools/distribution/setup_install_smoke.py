#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import tempfile


def _run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")


def _write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic setup smoke runner.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    cli = os.path.join(repo_root, "tools", "setup", "setup_cli.py")
    if not os.path.isfile(cli):
        print(json.dumps({"result": "error", "message": "setup_cli.py missing"}))
        return 1

    probe_cwd = tempfile.mkdtemp(prefix="setup_smoke_cwd_")

    help_run = _run(["python", cli, "--help"], probe_cwd)
    if help_run.returncode != 0:
        print(help_run.stdout)
        print(help_run.stderr)
        return 1

    work = tempfile.mkdtemp(prefix="setup_smoke_")
    manifest = os.path.join(work, "artifact_root", "setup", "manifests", "product.dsumanifest")
    _write_json(manifest + ".json", {"fixture": True})
    with open(manifest, "wb") as handle:
        handle.write(b"DSUMSMOKE")

    invocation = os.path.join(work, "install.invocation.json")
    export_run = _run([
        "python", cli,
        "--deterministic", "1",
        "export-invocation",
        "--manifest", manifest,
        "--op", "install",
        "--scope", "portable",
        "--install-root", os.path.join(work, "install"),
        "--out", invocation,
    ], probe_cwd)
    if export_run.returncode != 0:
        print(export_run.stdout)
        print(export_run.stderr)
        return 1

    plan = os.path.join(work, "install.plan.json")
    plan_run = _run([
        "python", cli,
        "--deterministic", "1",
        "plan",
        "--manifest", manifest,
        "--invocation", invocation,
        "--out", plan,
    ], probe_cwd)
    if plan_run.returncode != 0:
        print(plan_run.stdout)
        print(plan_run.stderr)
        return 1

    print(json.dumps({
        "result": "ok",
        "help_exit": help_run.returncode,
        "export_exit": export_run.returncode,
        "plan_exit": plan_run.returncode,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
