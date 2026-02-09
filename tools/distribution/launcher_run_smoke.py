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
    parser = argparse.ArgumentParser(description="Deterministic launcher smoke runner.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    cli = os.path.join(repo_root, "tools", "launcher", "launcher_cli.py")
    if not os.path.isfile(cli):
        print(json.dumps({"result": "error", "message": "launcher_cli.py missing"}))
        return 1

    probe_cwd = tempfile.mkdtemp(prefix="launcher_smoke_cwd_")

    help_run = _run(["python", cli, "--help"], probe_cwd)
    if help_run.returncode != 0:
        print(help_run.stdout)
        print(help_run.stderr)
        return 1

    work = tempfile.mkdtemp(prefix="launcher_smoke_")
    install_manifest = os.path.join(work, "install.manifest.json")
    instance_manifest = os.path.join(work, "instance.manifest.json")
    lockfile = os.path.join(work, "capability.lock.json")

    _write_json(install_manifest, {
        "install_id": "smoke-install",
        "install_root": work.replace("\\", "/"),
        "supported_capabilities": ["capability.runtime.client"],
        "binaries": {},
        "extensions": {}
    })
    _write_json(lockfile, {
        "resolutions": [
            {"capability_id": "capability.runtime.client", "provider_pack_id": "org.dominium.core.client"}
        ],
        "pack_refs": [
            {"pack_id": "org.dominium.core.client"}
        ]
    })
    _write_json(instance_manifest, {
        "instance_id": "smoke-instance",
        "install_id": "smoke-install",
        "data_root": "data",
        "active_profiles": [],
        "capability_lockfile": os.path.basename(lockfile),
        "extensions": {}
    })
    os.makedirs(os.path.join(work, "packs", "org.dominium.core.client"), exist_ok=True)

    preflight_run = _run([
        "python", cli,
        "--deterministic",
        "preflight",
        "--install-manifest", install_manifest,
        "--instance-manifest", instance_manifest,
    ], probe_cwd)
    if preflight_run.returncode != 0:
        print(preflight_run.stdout)
        print(preflight_run.stderr)
        return 1

    run_probe = _run([
        "python", cli,
        "--deterministic",
        "run",
        "--install-manifest", install_manifest,
        "--instance-manifest", instance_manifest,
        "--confirm",
        "--run-mode", "play",
    ], probe_cwd)
    if run_probe.returncode != 0:
        print(run_probe.stdout)
        print(run_probe.stderr)
        return 1

    print(json.dumps({
        "result": "ok",
        "help_exit": help_run.returncode,
        "preflight_exit": preflight_run.returncode,
        "run_exit": run_probe.returncode,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
