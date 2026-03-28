import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from lib.install import deterministic_fingerprint, validate_install_manifest


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


def _make_artifact_root(tmp: str) -> str:
    root = os.path.join(tmp, "artifact_root")
    _ensure_dir(os.path.join(root, "setup", "manifests"))
    _ensure_dir(os.path.join(root, "payloads", "runtime", "bin"))
    _ensure_dir(os.path.join(root, "payloads", "launcher", "bin"))

    _write_bytes(os.path.join(root, "setup", "manifests", "product.dsumanifest"), b"DSUMTEST")
    _write_text(os.path.join(root, "payloads", "runtime", "bin", "dominium_game"), "runtime\n")
    _write_text(os.path.join(root, "payloads", "launcher", "bin", "dominium-launcher"), "launcher\n")
    return root


def _run_setup(repo_root: str, args: list[str], allow_fail: bool = False):
    script = os.path.join(repo_root, "tools", "setup", "setup_cli.py")
    cmd = [sys.executable, script] + args
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not allow_fail and proc.returncode != 0:
        raise RuntimeError(
            "setup failed rc=%d stdout=%s stderr=%s"
            % (
                proc.returncode,
                proc.stdout.decode("utf-8", errors="ignore"),
                proc.stderr.decode("utf-8", errors="ignore"),
            )
        )
    payload = {}
    out = proc.stdout.decode("utf-8", errors="ignore").strip()
    if out:
        payload = json.loads(out)
    return proc.returncode, payload


def _create_install(repo_root: str) -> tuple[str, str]:
    work = tempfile.mkdtemp(prefix="install_manifest_")
    artifact_root = _make_artifact_root(work)
    manifest = os.path.join(artifact_root, "setup", "manifests", "product.dsumanifest")
    install_root = os.path.join(work, "install")
    data_root = os.path.join(work, "data")
    rc, payload = _run_setup(
        repo_root,
        [
            "--deterministic",
            "1",
            "install",
            "--manifest",
            manifest,
            "--install-root",
            install_root,
            "--data-root",
            data_root,
        ],
    )
    if rc != 0 or payload.get("result") != "ok":
        shutil.rmtree(work, ignore_errors=True)
        raise RuntimeError("setup install failed for test fixture")
    return work, install_root


def test_install_manifest_valid(repo_root: str) -> None:
    work, install_root = _create_install(repo_root)
    try:
        manifest_path = os.path.join(install_root, "install.manifest.json")
        manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
        for field in (
            "install_id",
            "install_version",
            "product_builds",
            "semantic_contract_registry_hash",
            "supported_protocol_versions",
            "supported_contract_ranges",
            "default_mod_policy_id",
            "store_root_ref",
            "mode",
            "deterministic_fingerprint",
            "extensions",
        ):
            if field not in manifest:
                raise RuntimeError("missing install manifest field %s" % field)
        report = validate_install_manifest(repo_root=repo_root, install_manifest_path=manifest_path)
        if report.get("result") != "complete":
            raise RuntimeError("install manifest validation failed: %s" % report)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_binary_hash_matches(repo_root: str) -> None:
    work, install_root = _create_install(repo_root)
    try:
        binary_path = os.path.join(install_root, "bin", "dominium_game")
        _write_text(binary_path, "corrupt\n")
        manifest_path = os.path.join(install_root, "install.manifest.json")
        report = validate_install_manifest(repo_root=repo_root, install_manifest_path=manifest_path)
        if report.get("result") == "complete":
            raise RuntimeError("expected binary hash mismatch refusal")
        if report.get("refusal_code") != "refusal.install.hash_mismatch":
            raise RuntimeError("unexpected refusal code: %s" % report.get("refusal_code"))
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_multiple_installs_coexist(repo_root: str) -> None:
    registry_root = tempfile.mkdtemp(prefix="install_registry_")
    registry_path = os.path.join(registry_root, "install_registry.json")
    work_a, install_a = _create_install(repo_root)
    work_b, install_b = _create_install(repo_root)
    try:
        for install_root in (install_a, install_b):
            rc, payload = _run_setup(
                repo_root,
                ["install", "add", install_root, "--registry-path", registry_path],
            )
            if rc != 0 or payload.get("result") != "ok":
                raise RuntimeError("registry add failed: %s" % payload)

        rc, payload = _run_setup(
            repo_root,
            ["install", "list", "--registry-path", registry_path],
        )
        installs = payload.get("details", {}).get("installs") or []
        if rc != 0 or len(installs) != 2:
            raise RuntimeError("expected two registered installs")
        install_ids = [row.get("install_id") for row in installs]
        if install_ids != sorted(install_ids):
            raise RuntimeError("registry order is not deterministic")

        rc, payload = _run_setup(
            repo_root,
            ["install", "verify", "--registry-path", registry_path],
        )
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("registry verify failed: %s" % payload)
    finally:
        shutil.rmtree(work_a, ignore_errors=True)
        shutil.rmtree(work_b, ignore_errors=True)
        shutil.rmtree(registry_root, ignore_errors=True)


def test_cross_platform_install_hash_match(repo_root: str) -> None:
    work, install_root = _create_install(repo_root)
    try:
        manifest_path = os.path.join(install_root, "install.manifest.json")
        manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
        mutated = json.loads(json.dumps(manifest))
        for row in (mutated.get("binaries") or {}).values():
            if isinstance(row, dict):
                if row.get("binary_ref"):
                    row["binary_ref"] = str(row["binary_ref"]).replace("/", "\\")
                if row.get("descriptor_ref"):
                    row["descriptor_ref"] = str(row["descriptor_ref"]).replace("/", "\\")
        for row in (mutated.get("product_build_descriptors") or {}).values():
            if isinstance(row, dict):
                extensions = row.get("extensions") or {}
                if isinstance(extensions, dict):
                    if extensions.get("official.binary_ref"):
                        extensions["official.binary_ref"] = str(extensions["official.binary_ref"]).replace("/", "\\")
                    if extensions.get("official.descriptor_ref"):
                        extensions["official.descriptor_ref"] = str(extensions["official.descriptor_ref"]).replace("/", "\\")
        store_root_ref = mutated.get("store_root_ref") or {}
        if isinstance(store_root_ref, dict):
            if store_root_ref.get("root_path"):
                store_root_ref["root_path"] = str(store_root_ref["root_path"]).replace("/", "\\")
            if store_root_ref.get("manifest_ref"):
                store_root_ref["manifest_ref"] = str(store_root_ref["manifest_ref"]).replace("/", "\\")
        fingerprint = deterministic_fingerprint(mutated)
        if fingerprint != manifest.get("deterministic_fingerprint"):
            raise RuntimeError("install fingerprint changed across path separators")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Install manifest validation tests.")
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    test_install_manifest_valid(repo_root)
    test_binary_hash_matches(repo_root)
    test_multiple_installs_coexist(repo_root)
    test_cross_platform_install_hash_match(repo_root)
    print("install manifest tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
