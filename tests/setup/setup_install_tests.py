import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


def _repo_rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _write_text(path: str, text: str) -> None:
    _ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _write_bytes(path: str, data: bytes) -> None:
    _ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "wb") as handle:
        handle.write(data)


def _make_artifact_root(tmp: str, with_packs: bool) -> str:
    root = os.path.join(tmp, "artifact_root")
    _ensure_dir(os.path.join(root, "setup", "manifests"))
    _ensure_dir(os.path.join(root, "payloads", "runtime", "bin"))
    _ensure_dir(os.path.join(root, "payloads", "launcher", "bin"))
    _ensure_dir(os.path.join(root, "payloads", "tools", "tools"))
    if with_packs:
        _ensure_dir(os.path.join(root, "payloads", "packs", "base", "repo", "mods", "base_demo"))

    _write_bytes(os.path.join(root, "setup", "manifests", "product.dsumanifest"), b"DSUMTEST")
    _write_text(os.path.join(root, "payloads", "runtime", "bin", "dominium_game"), "runtime\n")
    _write_text(os.path.join(root, "payloads", "launcher", "bin", "dominium-launcher"), "launcher\n")
    _write_text(os.path.join(root, "payloads", "tools", "tools", "README.txt"), "tools\n")
    if with_packs:
        _write_text(os.path.join(root, "payloads", "packs", "base", "repo", "mods", "base_demo", "pack.txt"), "pack\n")
    return root


def _run_setup(repo_root: str, args: list, env: dict, allow_fail: bool = False):
    script = os.path.join(repo_root, "tools", "setup", "setup_cli.py")
    cmd = [sys.executable, script] + args
    proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not allow_fail and proc.returncode != 0:
        raise RuntimeError("setup failed: rc=%d\nstdout=%s\nstderr=%s" % (
            proc.returncode,
            proc.stdout.decode("utf-8", errors="ignore"),
            proc.stderr.decode("utf-8", errors="ignore"),
        ))
    out = proc.stdout.decode("utf-8", errors="ignore").strip()
    payload = {}
    if out:
        payload = json.loads(out)
    return proc.returncode, payload


def _assert_ops_log(path: str) -> None:
    if not os.path.isfile(path):
        raise RuntimeError("missing ops log: %s" % path)
    with open(path, "r", encoding="utf-8") as handle:
        lines = [json.loads(line) for line in handle if line.strip()]
    states = {line.get("state") for line in lines}
    for required in ("PLAN", "STAGE", "COMMIT"):
        if required not in states:
            raise RuntimeError("ops log missing state %s in %s" % (required, path))


def _test_minimal_install(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="setup_minimal_")
    try:
        artifact_root = _make_artifact_root(work, with_packs=False)
        manifest = os.path.join(artifact_root, "setup", "manifests", "product.dsumanifest")
        install_root = os.path.join(work, "install")
        data_root = os.path.join(work, "data")
        env = dict(os.environ, SETUP_NETWORK_AVAILABLE="1")

        rc, payload = _run_setup(repo_root, [
            "--deterministic", "1",
            "install",
            "--manifest", manifest,
            "--install-root", install_root,
            "--data-root", data_root,
        ], env)
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("minimal install failed")

        if not os.path.isfile(os.path.join(install_root, "install.manifest.json")):
            raise RuntimeError("install.manifest.json missing")
        if not os.path.isfile(os.path.join(install_root, "compat_report.json")):
            raise RuntimeError("compat_report.json missing")
        _assert_ops_log(os.path.join(install_root, "ops", "ops.log"))
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_maximal_install(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="setup_maximal_")
    try:
        artifact_root = _make_artifact_root(work, with_packs=True)
        manifest = os.path.join(artifact_root, "setup", "manifests", "product.dsumanifest")
        install_root = os.path.join(work, "install")
        data_root = os.path.join(work, "data")
        env = dict(os.environ, SETUP_NETWORK_AVAILABLE="1")
        rc, payload = _run_setup(repo_root, [
            "--deterministic", "1",
            "install",
            "--manifest", manifest,
            "--install-root", install_root,
            "--data-root", data_root,
        ], env)
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("maximal install failed")
        packs_path = os.path.join(data_root, "packs", "base", "repo", "mods", "base_demo", "pack.txt")
        if not os.path.isfile(packs_path):
            raise RuntimeError("bundled packs not staged to data_root")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_offline_install(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="setup_offline_")
    try:
        artifact_root = _make_artifact_root(work, with_packs=False)
        manifest = os.path.join(artifact_root, "setup", "manifests", "product.dsumanifest")
        install_root = os.path.join(work, "install")
        data_root = os.path.join(work, "data")
        env = dict(os.environ, SETUP_NETWORK_AVAILABLE="0")
        rc, payload = _run_setup(repo_root, [
            "--deterministic", "1",
            "--network-mode", "online",
            "install",
            "--manifest", manifest,
            "--install-root", install_root,
            "--data-root", data_root,
        ], env)
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("offline install failed")
        status = payload.get("details", {}).get("network_status")
        if status != "offline":
            raise RuntimeError("offline status missing in output")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_failure_rollback(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="setup_fail_")
    try:
        artifact_root = _make_artifact_root(work, with_packs=False)
        manifest = os.path.join(artifact_root, "setup", "manifests", "product.dsumanifest")
        install_root = os.path.join(work, "install")
        data_root = os.path.join(work, "data")
        env = dict(os.environ, SETUP_NETWORK_AVAILABLE="1")
        rc, _payload = _run_setup(repo_root, [
            "--deterministic", "1",
            "install",
            "--manifest", manifest,
            "--install-root", install_root,
            "--data-root", data_root,
            "--simulate-failure", "stage",
        ], env, allow_fail=True)
        if rc == 0:
            raise RuntimeError("expected failure did not occur")
        if os.path.isdir(install_root):
            raise RuntimeError("install_root should not exist after rollback")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_repair_uninstall_rollback(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="setup_repair_")
    try:
        artifact_root = _make_artifact_root(work, with_packs=False)
        manifest = os.path.join(artifact_root, "setup", "manifests", "product.dsumanifest")
        install_root = os.path.join(work, "install")
        data_root = os.path.join(work, "data")
        env = dict(os.environ, SETUP_NETWORK_AVAILABLE="1")

        rc, _payload = _run_setup(repo_root, [
            "--deterministic", "1",
            "install",
            "--manifest", manifest,
            "--install-root", install_root,
            "--data-root", data_root,
        ], env)
        if rc != 0:
            raise RuntimeError("install failed")

        target_bin = os.path.join(install_root, "bin", "dominium_game")
        _write_text(target_bin, "corrupt\n")

        rc, _payload = _run_setup(repo_root, [
            "--deterministic", "1",
            "repair",
            "--manifest", manifest,
            "--install-root", install_root,
        ], env)
        if rc != 0:
            raise RuntimeError("repair failed")
        _assert_ops_log(os.path.join(install_root, "ops", "ops.log"))

        with open(target_bin, "r", encoding="utf-8") as handle:
            content = handle.read()
        if content.strip() == "corrupt":
            raise RuntimeError("repair did not restore payload")

        # Rollback should restore the previous (corrupted) snapshot.
        rc, _payload = _run_setup(repo_root, [
            "--deterministic", "1",
            "rollback",
            "--install-root", install_root,
        ], env)
        if rc != 0:
            raise RuntimeError("rollback failed")

        # Uninstall preserves data_root by default.
        _write_text(os.path.join(data_root, "user.txt"), "keep\n")
        rc, _payload = _run_setup(repo_root, [
            "uninstall",
            "--install-root", install_root,
            "--data-root", data_root,
        ], env)
        if rc != 0:
            raise RuntimeError("uninstall failed")
        if os.path.isdir(install_root):
            raise RuntimeError("install_root not removed")
        if not os.path.isfile(os.path.join(data_root, "user.txt")):
            raise RuntimeError("data_root was not preserved")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Setup install/repair/uninstall tests.")
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    _test_minimal_install(repo_root)
    _test_maximal_install(repo_root)
    _test_offline_install(repo_root)
    _test_failure_rollback(repo_root)
    _test_repair_uninstall_rollback(repo_root)
    print("setup install tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
