import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.compat import build_product_build_metadata, build_product_descriptor
from src.lib.install import build_product_build_descriptor, deterministic_fingerprint
from tools.xstack.compatx.canonical_json import canonical_sha256


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _write_json(path: str, payload: dict) -> None:
    _ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _run_launcher(repo_root: str, args: list, allow_fail: bool = False):
    script = os.path.join(repo_root, "tools", "launcher", "launcher_cli.py")
    cmd = [sys.executable, script] + args
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not allow_fail and proc.returncode != 0:
        raise RuntimeError("launcher failed rc=%d stdout=%s stderr=%s" % (
            proc.returncode,
            proc.stdout.decode("utf-8", errors="ignore"),
            proc.stderr.decode("utf-8", errors="ignore"),
        ))
    payload = {}
    out = proc.stdout.decode("utf-8", errors="ignore").strip()
    if out:
        payload = json.loads(out)
    return proc.returncode, payload


def _run_share(repo_root: str, args: list, allow_fail: bool = False):
    script = os.path.join(repo_root, "tools", "share", "share_cli.py")
    cmd = [sys.executable, script] + args
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not allow_fail and proc.returncode != 0:
        raise RuntimeError("share failed rc=%d stdout=%s stderr=%s" % (
            proc.returncode,
            proc.stdout.decode("utf-8", errors="ignore"),
            proc.stderr.decode("utf-8", errors="ignore"),
        ))
    payload = {}
    out = proc.stdout.decode("utf-8", errors="ignore").strip()
    if out:
        payload = json.loads(out)
    return proc.returncode, payload


def _write_install_manifest(repo_root: str, root: str, install_id: str) -> str:
    path = os.path.join(root, "install.manifest.json")
    _ensure_dir(os.path.join(root, "bin"))
    registry_payload = json.load(open(os.path.join(repo_root, "data", "registries", "semantic_contract_registry.json"), "r", encoding="utf-8"))
    _write_json(os.path.join(root, "semantic_contract_registry.json"), registry_payload)
    game_bin = os.path.join(root, "bin", "dominium_game")
    with open(game_bin, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("runtime\n")
    game_descriptor = build_product_descriptor(repo_root, product_id="game", product_version="0.1.0")
    descriptor_path = os.path.join(root, "bin", "dominium_game.descriptor.json")
    _write_json(descriptor_path, game_descriptor)
    build_meta = build_product_build_metadata(repo_root, "game")
    product_build_descriptor = build_product_build_descriptor(
        product_id="game",
        build_id=str(build_meta.get("build_id", "")).strip(),
        binary_hash=hashlib.sha256(open(game_bin, "rb").read()).hexdigest(),
        endpoint_descriptor_hash=canonical_sha256(game_descriptor),
        binary_ref="bin/dominium_game",
        descriptor_ref="bin/dominium_game.descriptor.json",
        product_version="0.1.0",
    )
    payload = {
        "install_id": install_id,
        "install_version": "0.1.0",
        "install_root": ".",
        "product_builds": {
            "game": str(build_meta.get("build_id", "")).strip(),
        },
        "product_build_ids": {
            "game": str(build_meta.get("build_id", "")).strip(),
        },
        "semantic_contract_registry_hash": canonical_sha256(
            registry_payload
        ),
        "supported_protocol_versions": {
            str(row.get("protocol_id")): row
            for row in list(game_descriptor.get("protocol_versions_supported") or [])
        },
        "supported_contract_ranges": {
            str(row.get("contract_category_id")): row
            for row in list(game_descriptor.get("semantic_contract_versions_supported") or [])
        },
        "default_mod_policy_id": "mod.policy.default",
        "store_root_ref": {
            "store_id": "store.default",
            "root_path": "store",
            "manifest_ref": "store.root.json",
        },
        "mode": "portable",
        "binaries": {
            "game": {
                "product_id": "game",
                "product_version": "0.1.0",
                "build_id": str(build_meta.get("build_id", "")).strip(),
                "binary_ref": "bin/dominium_game",
                "descriptor_ref": "bin/dominium_game.descriptor.json",
                "binary_hash": product_build_descriptor["binary_hash"],
                "endpoint_descriptor_hash": product_build_descriptor["endpoint_descriptor_hash"],
                "extensions": {},
            }
        },
        "product_build_descriptors": {
            "game": product_build_descriptor,
        },
        "supported_capabilities": ["CAP_CORE"],
        "protocol_versions": {
            "network": "v1",
            "save": "v1",
            "mod": "v1",
            "replay": "v1"
        },
        "build_identity": 1,
        "trust_tier": "official",
        "created_at": "2000-01-01T00:00:00Z",
        "extensions": {
            "official.semantic_contract_registry_ref": "semantic_contract_registry.json",
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    _write_json(path, payload)
    return path


def _write_lockfile(path: str, capability_id: str, pack_id: str, missing_mode: str) -> None:
    payload = {
        "lock_id": "lock.test",
        "lock_format_version": 1,
        "generated_by": "launcher.tests",
        "resolution_rules": [],
        "missing_mode": missing_mode,
        "resolutions": [
            {
                "capability_id": capability_id,
                "provider_pack_id": pack_id
            }
        ],
        "extensions": {}
    }
    _write_json(path, payload)


def _write_instance_manifest(root: str, instance_id: str, install_id: str, required_product_builds: dict | None = None) -> str:
    path = os.path.join(root, "instance.manifest.json")
    payload = {
        "instance_id": instance_id,
        "install_id": install_id,
        "required_product_builds": required_product_builds or {},
        "data_root": ".",
        "active_profiles": ["org.dominium.profile.casual"],
        "active_modpacks": [],
        "capability_lockfile": "lockfiles/capabilities.lock",
        "sandbox_policy_ref": "sandbox.default",
        "update_channel": "stable",
        "created_at": "2000-01-01T00:00:00Z",
        "last_used_at": "2000-01-01T00:00:00Z",
        "extensions": {}
    }
    _write_json(path, payload)
    return path


def _test_enumeration(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="launcher_enum_")
    try:
        install_a = os.path.join(work, "install_a")
        install_b = os.path.join(work, "install_b")
        _ensure_dir(install_a)
        _ensure_dir(install_b)
        _write_install_manifest(repo_root, install_a, str(uuid.uuid4()))
        _write_install_manifest(repo_root, install_b, str(uuid.uuid4()))
        rc, payload = _run_launcher(repo_root, ["--deterministic", "installs", "list", "--search", work])
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("install enumeration failed")
        installs = payload.get("installs") or []
        if len(installs) < 2:
            raise RuntimeError("expected multiple installs")

        instance_a = os.path.join(work, "instance_a")
        instance_b = os.path.join(work, "instance_b")
        _ensure_dir(instance_a)
        _ensure_dir(instance_b)
        install_id = installs[0].get("install_id")
        _write_instance_manifest(instance_a, str(uuid.uuid4()), install_id)
        _write_instance_manifest(instance_b, str(uuid.uuid4()), install_id)
        rc, payload = _run_launcher(repo_root, ["--deterministic", "instances", "list", "--search", work])
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("instance enumeration failed")
        instances = payload.get("instances") or []
        if len(instances) < 2:
            raise RuntimeError("expected multiple instances")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_delete_confirmation(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="launcher_delete_")
    try:
        install_root = os.path.join(work, "install")
        instance_root = os.path.join(work, "instance")
        _ensure_dir(install_root)
        _ensure_dir(instance_root)
        install_id = str(uuid.uuid4())
        _write_install_manifest(repo_root, install_root, install_id)
        manifest_path = _write_instance_manifest(instance_root, str(uuid.uuid4()), install_id)
        lock_path = os.path.join(instance_root, "lockfiles", "capabilities.lock")
        _write_lockfile(lock_path, "CAP_CORE", "org.dominium.pack.core", "degraded")
        _write_json(os.path.join(instance_root, "user.json"), {"keep": True})

        rc, payload = _run_launcher(repo_root, ["instances", "delete", "--instance-manifest", manifest_path], allow_fail=True)
        if rc == 0 or payload.get("result") != "refused":
            raise RuntimeError("delete without confirm should refuse")

        rc, payload = _run_launcher(repo_root, ["instances", "delete",
                                                "--instance-manifest", manifest_path,
                                                "--confirm"], allow_fail=False)
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("delete with confirm failed")
        if os.path.exists(manifest_path):
            raise RuntimeError("instance manifest should be removed")
        if not os.path.isfile(os.path.join(instance_root, "user.json")):
            raise RuntimeError("data should remain without delete-data")

        instance_root2 = os.path.join(work, "instance2")
        _ensure_dir(instance_root2)
        manifest_path2 = _write_instance_manifest(instance_root2, str(uuid.uuid4()), install_id)
        _write_lockfile(os.path.join(instance_root2, "lockfiles", "capabilities.lock"),
                        "CAP_CORE", "org.dominium.pack.core", "degraded")
        _write_json(os.path.join(instance_root2, "user.json"), {"keep": True})
        rc, payload = _run_launcher(repo_root, ["instances", "delete",
                                                "--instance-manifest", manifest_path2,
                                                "--confirm", "--delete-data"], allow_fail=False)
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("delete with data removal failed")
        if os.path.exists(instance_root2):
            raise RuntimeError("data root should be removed with delete-data")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_preflight_and_run(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="launcher_preflight_")
    try:
        install_root = os.path.join(work, "install")
        instance_root = os.path.join(work, "instance")
        _ensure_dir(install_root)
        _ensure_dir(instance_root)
        install_id = str(uuid.uuid4())
        install_manifest = _write_install_manifest(repo_root, install_root, install_id)
        instance_manifest = _write_instance_manifest(instance_root, str(uuid.uuid4()), install_id)
        lock_path = os.path.join(instance_root, "lockfiles", "capabilities.lock")
        _write_lockfile(lock_path, "CAP_CORE", "org.dominium.pack.missing", "degraded")

        rc, payload = _run_launcher(repo_root, ["--deterministic", "preflight",
                                                "--install-manifest", install_manifest,
                                                "--instance-manifest", instance_manifest])
        report = payload.get("compat_report") or {}
        if rc != 0 or report.get("compatibility_mode") != "degraded":
            raise RuntimeError("expected degraded preflight")

        rc, payload = _run_launcher(repo_root, ["run",
                                                "--install-manifest", install_manifest,
                                                "--instance-manifest", instance_manifest],
                                    allow_fail=True)
        if rc == 0:
            raise RuntimeError("run should require confirmation in degraded mode")

        rc, payload = _run_launcher(repo_root, ["run",
                                                "--install-manifest", install_manifest,
                                                "--instance-manifest", instance_manifest,
                                                "--confirm"], allow_fail=False)
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("confirmed run failed")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_instance_build_selection(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="launcher_build_select_")
    try:
        install_root = os.path.join(work, "install")
        instance_root = os.path.join(work, "instance")
        _ensure_dir(install_root)
        _ensure_dir(instance_root)
        install_id = str(uuid.uuid4())
        install_manifest = _write_install_manifest(repo_root, install_root, install_id)
        instance_manifest = _write_instance_manifest(
            instance_root,
            str(uuid.uuid4()),
            install_id,
            required_product_builds={"game": "build.mismatch"},
        )
        lock_path = os.path.join(instance_root, "lockfiles", "capabilities.lock")
        _write_lockfile(lock_path, "CAP_CORE", "org.dominium.pack.core", "degraded")

        rc, payload = _run_launcher(
            repo_root,
            [
                "--deterministic",
                "preflight",
                "--install-manifest",
                install_manifest,
                "--instance-manifest",
                instance_manifest,
            ],
            allow_fail=True,
        )
        report = payload.get("compat_report") or {}
        if rc == 0:
            raise RuntimeError("expected build-selection refusal")
        if report.get("compatibility_mode") != "refuse":
            raise RuntimeError("expected refused build selection preflight")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_bundle_import_refusal(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="launcher_bundle_")
    try:
        artifact = os.path.join(work, "replay.bin")
        lockfile = os.path.join(work, "capability.lock")
        _write_json(lockfile, {
            "lock_id": "lock.test",
            "lock_format_version": 1,
            "generated_by": "launcher.tests",
            "resolution_rules": [],
            "missing_mode": "degraded",
            "resolutions": [],
            "extensions": {}
        })
        with open(artifact, "wb") as handle:
            handle.write(b"replay")
        bundle_root = os.path.join(work, "bundle")
        _run_share(repo_root, [
            "export",
            "--bundle-type", "replay",
            "--artifact", artifact,
            "--lockfile", lockfile,
            "--pack-ref", "org.dominium.pack.missing",
            "--out", bundle_root
        ])
        rc, payload = _run_launcher(repo_root, [
            "bundles", "import",
            "--bundle", bundle_root,
            "--require-full",
            "--confirm"
        ], allow_fail=True)
        if rc == 0:
            raise RuntimeError("expected refusal for missing packs with require-full")
        if payload.get("result") != "refused":
            raise RuntimeError("expected refused bundle import")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Launcher CLI tests.")
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    _test_enumeration(repo_root)
    _test_delete_confirmation(repo_root)
    _test_preflight_and_run(repo_root)
    _test_instance_build_selection(repo_root)
    _test_bundle_import_refusal(repo_root)
    print("launcher cli tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
