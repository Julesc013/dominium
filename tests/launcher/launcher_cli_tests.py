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
from src.lib.instance import (
    deterministic_fingerprint as instance_deterministic_fingerprint,
    normalize_instance_manifest,
)
from src.lib.save import (
    deterministic_fingerprint as save_deterministic_fingerprint,
    normalize_save_manifest,
)
from tools.lib.content_store import (
    build_install_ref,
    build_pack_lock_payload,
    build_profile_bundle_payload,
    embed_json_artifact,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _write_json(path: str, payload: dict) -> None:
    _ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _write_pack(root: str, pack_id: str) -> None:
    pack_root = os.path.join(root, "packs", pack_id)
    _ensure_dir(pack_root)
    with open(os.path.join(pack_root, "pack.toml"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write('pack_id = "{}"\n'.format(pack_id))
        handle.write('pack_version = "1.0.0"\n')
    with open(os.path.join(pack_root, "content.txt"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("content\n")


def _build_contract_bundle_payload(install_manifest: dict, bundle_id: str) -> tuple[dict, str]:
    payload = {
        "schema_id": "dominium.schema.universe_contract_bundle",
        "schema_version": "1.0.0",
        "bundle_id": bundle_id,
        "contracts": [
            {
                "contract_category_id": "contract.logic.eval",
                "version": 1,
            }
        ],
        "extensions": {
            "semantic_contract_registry_hash": str(install_manifest.get("semantic_contract_registry_hash", "")).strip(),
        },
    }
    return payload, canonical_sha256(payload)


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


def _build_lockfile_payload(
    capability_id: str,
    pack_id: str,
    missing_mode: str,
    engine_contract_bundle_hash: str = "",
    semantic_contract_registry_hash: str = "",
) -> dict:
    return {
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
        "engine_contract_bundle_hash": str(engine_contract_bundle_hash or "").strip(),
        "semantic_contract_registry_hash": str(semantic_contract_registry_hash or "").strip(),
        "extensions": {}
    }


def _write_lockfile(path: str, capability_id: str, pack_id: str, missing_mode: str) -> dict:
    payload = _build_lockfile_payload(capability_id, pack_id, missing_mode)
    _write_json(path, payload)
    return payload


def _write_instance_manifest(root: str,
                             instance_id: str,
                             install_manifest_path: str,
                             required_product_builds: dict | None = None,
                             allow_read_only_fallback: bool = False,
                             instance_kind: str = "instance.client",
                             save_refs: list[str] | None = None,
                             last_opened_save_id: str = "",
                             missing_mode: str = "degraded",
                             pack_id: str = "org.dominium.pack.core",
                             engine_contract_bundle_hash: str = "",
                             semantic_contract_registry_hash: str = "") -> str:
    path = os.path.join(root, "instance.manifest.json")
    install_manifest = json.load(open(install_manifest_path, "r", encoding="utf-8"))
    lockfile_payload = _build_lockfile_payload(
        "CAP_CORE",
        pack_id,
        missing_mode,
        engine_contract_bundle_hash=engine_contract_bundle_hash,
        semantic_contract_registry_hash=semantic_contract_registry_hash,
    )
    pack_lock_payload, pack_lock_hash = build_pack_lock_payload(
        instance_id=instance_id,
        pack_ids=[pack_id],
        mod_policy_id="mod.policy.default",
        overlay_conflict_policy_id="overlay.conflict.default",
        source_payload=lockfile_payload,
    )
    profile_bundle_payload, profile_bundle_hash = build_profile_bundle_payload(
        instance_id=instance_id,
        profile_ids=["org.dominium.profile.casual"],
        mod_policy_id="mod.policy.default",
        overlay_conflict_policy_id="overlay.conflict.default",
    )
    embed_json_artifact(root, "locks", pack_lock_payload, expected_hash=pack_lock_hash)
    embed_json_artifact(root, "profiles", profile_bundle_payload, expected_hash=profile_bundle_hash)
    _write_json(os.path.join(root, "lockfiles", "capabilities.lock"), pack_lock_payload)
    normalized_save_refs = sorted({str(item).strip() for item in list(save_refs or []) if str(item).strip()})
    if last_opened_save_id and last_opened_save_id not in normalized_save_refs:
        normalized_save_refs.append(last_opened_save_id)
    payload = {
        "instance_id": instance_id,
        "instance_kind": instance_kind,
        "install_id": install_manifest.get("install_id"),
        "mode": "portable",
        "install_ref": build_install_ref(root, install_manifest_path, install_manifest),
        "embedded_builds": {},
        "pack_lock_hash": pack_lock_hash,
        "profile_bundle_hash": profile_bundle_hash,
        "mod_policy_id": "mod.policy.default",
        "overlay_conflict_policy_id": "overlay.conflict.default",
        "default_session_template_id": "session.template.default",
        "seed_policy": "prompt",
        "required_product_builds": required_product_builds or {},
        "required_contract_ranges": {},
        "instance_settings": {
            "renderer_mode": None,
            "ui_mode_default": "cli",
            "allow_read_only_fallback": allow_read_only_fallback,
            "tick_budget_policy_id": "tick.budget.default",
            "compute_profile_id": "compute.profile.default",
            "data_root": ".",
            "active_profiles": ["org.dominium.profile.casual"],
            "active_modpacks": [],
            "sandbox_policy_ref": "sandbox.default",
            "update_channel": "stable",
            "extensions": {},
            "deterministic_fingerprint": "",
        },
        "save_refs": normalized_save_refs,
        "store_root": {},
        "embedded_artifacts": [
            {
                "category": "locks",
                "artifact_hash": pack_lock_hash,
                "artifact_type": "json",
                "artifact_path": "embedded_artifacts/locks/%s" % pack_lock_hash,
                "artifact_id": pack_lock_payload.get("pack_lock_id"),
            },
            {
                "category": "profiles",
                "artifact_hash": profile_bundle_hash,
                "artifact_type": "json",
                "artifact_path": "embedded_artifacts/profiles/%s" % profile_bundle_hash,
                "artifact_id": profile_bundle_payload.get("profile_bundle_id"),
            },
        ],
        "data_root": ".",
        "active_profiles": ["org.dominium.profile.casual"],
        "active_modpacks": [],
        "capability_lockfile": "lockfiles/capabilities.lock",
        "sandbox_policy_ref": "sandbox.default",
        "update_channel": "stable",
        "created_at": "2000-01-01T00:00:00Z",
        "last_used_at": "2000-01-01T00:00:00Z",
        "extensions": {},
        "deterministic_fingerprint": "",
    }
    payload["instance_settings"]["deterministic_fingerprint"] = instance_deterministic_fingerprint(payload["instance_settings"])
    if last_opened_save_id:
        payload["extensions"]["instance.last_opened_save_id"] = last_opened_save_id
    payload = normalize_instance_manifest(payload)
    payload["deterministic_fingerprint"] = instance_deterministic_fingerprint(payload)
    _write_json(path, payload)
    return path


def _write_save_manifest(
    install_root: str,
    save_id: str,
    *,
    pack_lock_hash: str,
    contract_bundle_payload: dict,
    created_by_build_id: str,
    semantic_contract_registry_hash: str = "",
    allow_read_only_open: bool = False,
    save_format_version: str = "1.0.0",
) -> str:
    save_root = os.path.join(install_root, "saves", save_id)
    _ensure_dir(os.path.join(save_root, "state.snapshots"))
    _ensure_dir(os.path.join(save_root, "patches"))
    _write_json(os.path.join(save_root, "universe_contract_bundle.json"), contract_bundle_payload)
    _write_json(os.path.join(save_root, "state.snapshots", "snapshot.000.json"), {"tick": 0})
    _write_json(os.path.join(save_root, "patches", "overlay.000.json"), {"patch": 0})
    payload = {
        "save_id": save_id,
        "save_format_version": save_format_version,
        "universe_identity_hash": canonical_sha256({"save_id": save_id, "universe": "test"}),
        "universe_contract_bundle_hash": canonical_sha256(contract_bundle_payload),
        "semantic_contract_registry_hash": str(semantic_contract_registry_hash or "").strip(),
        "generator_version_id": "generator.test",
        "realism_profile_id": "realism.profile.default",
        "pack_lock_hash": pack_lock_hash,
        "overlay_manifest_hash": canonical_sha256({"save_id": save_id, "overlay": "default"}),
        "mod_policy_id": "mod.policy.default",
        "created_by_build_id": created_by_build_id,
        "migration_chain": [],
        "allow_read_only_open": bool(allow_read_only_open),
        "contract_bundle_ref": "universe_contract_bundle.json",
        "state_snapshots_ref": "state.snapshots",
        "patches_ref": "patches",
        "extensions": {},
        "deterministic_fingerprint": "",
    }
    payload = normalize_save_manifest(payload)
    payload["deterministic_fingerprint"] = save_deterministic_fingerprint(payload)
    path = os.path.join(save_root, "save.manifest.json")
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
        install_manifest_path = os.path.join(install_a, "install.manifest.json")
        _write_instance_manifest(instance_a, str(uuid.uuid4()), install_manifest_path)
        _write_instance_manifest(instance_b, str(uuid.uuid4()), install_manifest_path)
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
        manifest_path = _write_instance_manifest(instance_root, str(uuid.uuid4()), os.path.join(install_root, "install.manifest.json"))
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
        manifest_path2 = _write_instance_manifest(instance_root2, str(uuid.uuid4()), os.path.join(install_root, "install.manifest.json"))
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
        instance_manifest = _write_instance_manifest(
            instance_root,
            str(uuid.uuid4()),
            install_manifest,
            missing_mode="degraded",
            pack_id="org.dominium.pack.missing",
        )

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
            install_manifest,
            required_product_builds={"game": "build.mismatch"},
        )

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


def _test_start_validates_packs(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="launcher_start_")
    try:
        install_root = os.path.join(work, "install")
        instance_root = os.path.join(work, "instance")
        _ensure_dir(install_root)
        _ensure_dir(instance_root)
        install_id = str(uuid.uuid4())
        install_manifest = _write_install_manifest(repo_root, install_root, install_id)
        install_payload = json.load(open(install_manifest, "r", encoding="utf-8"))
        contract_bundle_payload, _contract_bundle_hash = _build_contract_bundle_payload(
            install_payload,
            "bundle.contract.start",
        )
        instance_manifest = _write_instance_manifest(
            instance_root,
            str(uuid.uuid4()),
            install_manifest,
            save_refs=["save.alpha"],
            last_opened_save_id="save.alpha",
            missing_mode="degraded",
            pack_id="org.dominium.pack.missing",
        )
        instance_payload = json.load(open(instance_manifest, "r", encoding="utf-8"))
        _write_save_manifest(
            install_root,
            "save.alpha",
            pack_lock_hash=str(instance_payload.get("pack_lock_hash", "")).strip(),
            contract_bundle_payload=contract_bundle_payload,
            created_by_build_id=str((install_payload.get("product_builds") or {}).get("game", "")).strip(),
            semantic_contract_registry_hash=str(install_payload.get("semantic_contract_registry_hash", "")).strip(),
        )

        rc, payload = _run_launcher(
            repo_root,
            [
                "--deterministic",
                "start",
                "--instance",
                instance_manifest,
                "--install-manifest",
                install_manifest,
                "--save",
                "save.alpha",
                "--run-mode",
                "play",
                "--confirm",
            ],
            allow_fail=False,
        )
        report = payload.get("compat_report") or {}
        if rc != 0 or payload.get("result") != "ok":
            raise RuntimeError("start failed")
        if report.get("compatibility_mode") != "degraded":
            raise RuntimeError("expected degraded start due to missing required pack")
        if payload.get("save_id") != "save.alpha":
            raise RuntimeError("selected save id was not preserved")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_save_open_refuses_contract_mismatch(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="launcher_save_refuse_")
    try:
        install_root = os.path.join(work, "install")
        instance_root = os.path.join(work, "instance")
        _ensure_dir(install_root)
        _ensure_dir(instance_root)
        install_id = str(uuid.uuid4())
        install_manifest = _write_install_manifest(repo_root, install_root, install_id)
        _write_pack(install_root, "org.dominium.pack.core")
        install_payload = json.load(open(install_manifest, "r", encoding="utf-8"))
        instance_contract_payload, instance_contract_hash = _build_contract_bundle_payload(
            install_payload,
            "bundle.contract.instance",
        )
        save_contract_payload, _save_contract_hash = _build_contract_bundle_payload(
            install_payload,
            "bundle.contract.save",
        )
        instance_manifest = _write_instance_manifest(
            instance_root,
            str(uuid.uuid4()),
            install_manifest,
            save_refs=["save.alpha"],
            last_opened_save_id="save.alpha",
            pack_id="org.dominium.pack.core",
            engine_contract_bundle_hash=instance_contract_hash,
            semantic_contract_registry_hash=str(install_payload.get("semantic_contract_registry_hash", "")).strip(),
        )
        del instance_contract_payload
        instance_payload = json.load(open(instance_manifest, "r", encoding="utf-8"))
        _write_save_manifest(
            install_root,
            "save.alpha",
            pack_lock_hash=str(instance_payload.get("pack_lock_hash", "")).strip(),
            contract_bundle_payload=save_contract_payload,
            created_by_build_id=str((install_payload.get("product_builds") or {}).get("game", "")).strip(),
            semantic_contract_registry_hash=str(install_payload.get("semantic_contract_registry_hash", "")).strip(),
            allow_read_only_open=False,
        )

        rc, payload = _run_launcher(
            repo_root,
            [
                "--deterministic",
                "preflight",
                "--install-manifest",
                install_manifest,
                "--instance-manifest",
                instance_manifest,
                "--save",
                "save.alpha",
                "--run-mode",
                "play",
            ],
            allow_fail=True,
        )
        report = payload.get("compat_report") or {}
        if rc == 0:
            raise RuntimeError("expected refusal for contract mismatch")
        if report.get("compatibility_mode") != "refuse":
            raise RuntimeError("expected refuse mode for contract mismatch")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_save_open_read_only_when_allowed(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="launcher_save_read_only_")
    try:
        install_root = os.path.join(work, "install")
        instance_root = os.path.join(work, "instance")
        _ensure_dir(install_root)
        _ensure_dir(instance_root)
        install_id = str(uuid.uuid4())
        install_manifest = _write_install_manifest(repo_root, install_root, install_id)
        _write_pack(install_root, "org.dominium.pack.core")
        install_payload = json.load(open(install_manifest, "r", encoding="utf-8"))
        instance_contract_payload, instance_contract_hash = _build_contract_bundle_payload(
            install_payload,
            "bundle.contract.instance.read_only",
        )
        save_contract_payload, _save_contract_hash = _build_contract_bundle_payload(
            install_payload,
            "bundle.contract.save.read_only",
        )
        instance_manifest = _write_instance_manifest(
            instance_root,
            str(uuid.uuid4()),
            install_manifest,
            allow_read_only_fallback=True,
            save_refs=["save.alpha"],
            last_opened_save_id="save.alpha",
            pack_id="org.dominium.pack.core",
            engine_contract_bundle_hash=instance_contract_hash,
            semantic_contract_registry_hash=str(install_payload.get("semantic_contract_registry_hash", "")).strip(),
        )
        del instance_contract_payload
        instance_payload = json.load(open(instance_manifest, "r", encoding="utf-8"))
        _write_save_manifest(
            install_root,
            "save.alpha",
            pack_lock_hash=str(instance_payload.get("pack_lock_hash", "")).strip(),
            contract_bundle_payload=save_contract_payload,
            created_by_build_id=str((install_payload.get("product_builds") or {}).get("game", "")).strip(),
            semantic_contract_registry_hash=str(install_payload.get("semantic_contract_registry_hash", "")).strip(),
            allow_read_only_open=True,
        )

        rc, payload = _run_launcher(
            repo_root,
            [
                "--deterministic",
                "preflight",
                "--install-manifest",
                install_manifest,
                "--instance-manifest",
                instance_manifest,
                "--save",
                "save.alpha",
                "--run-mode",
                "play",
            ],
            allow_fail=False,
        )
        report = payload.get("compat_report") or {}
        extensions = report.get("extensions") or {}
        if rc != 0 or report.get("compatibility_mode") != "inspect-only":
            raise RuntimeError("expected inspect-only mode for save read-only fallback")
        if not extensions.get("degrade_logged"):
            raise RuntimeError("expected save degrade to be logged")
        if "save_engine_contract_mismatch" not in (extensions.get("degrade_reasons") or []):
            raise RuntimeError("expected save contract mismatch degrade reason")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _test_instance_degrade_mode_logged(repo_root: str) -> None:
    work = tempfile.mkdtemp(prefix="launcher_degrade_log_")
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
            install_manifest,
            allow_read_only_fallback=True,
            instance_kind="instance.server",
        )

        rc, payload = _run_launcher(
            repo_root,
            [
                "--deterministic",
                "preflight",
                "--install-manifest",
                install_manifest,
                "--instance-manifest",
                instance_manifest,
                "--run-mode",
                "play",
            ],
            allow_fail=False,
        )
        report = payload.get("compat_report") or {}
        extensions = report.get("extensions") or {}
        if rc != 0 or report.get("compatibility_mode") != "inspect-only":
            raise RuntimeError("expected inspect-only degrade for instance kind mismatch")
        if not extensions.get("degrade_logged"):
            raise RuntimeError("expected degrade_logged marker")
        if "instance_kind_mismatch" not in (extensions.get("degrade_reasons") or []):
            raise RuntimeError("expected instance_kind_mismatch degrade reason")
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
    _test_start_validates_packs(repo_root)
    _test_save_open_refuses_contract_mismatch(repo_root)
    _test_save_open_read_only_when_allowed(repo_root)
    _test_instance_degrade_mode_logged(repo_root)
    _test_bundle_import_refusal(repo_root)
    print("launcher cli tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
