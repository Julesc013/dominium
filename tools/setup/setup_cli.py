#!/usr/bin/env python3
from __future__ import print_function

import argparse
import base64
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.appshell import appshell_main
from src.appshell.logging import log_emit
from src.appshell.pack_verifier_adapter import verify_pack_root as appshell_verify_pack_root
from src.appshell.paths import (
    VROOT_INSTANCES,
    VROOT_PACKS,
    vpath_candidate_roots,
    vpath_init,
)
from src.compat import (
    build_product_build_metadata,
    build_product_descriptor,
    descriptor_json_text,
    emit_product_descriptor,
)
from src.governance import (
    governance_profile_hash,
    governance_profile_path,
    load_governance_mode_registry,
    load_governance_profile,
    select_governance_mode_row,
)
from src.lib.install import (
    build_product_build_descriptor,
    default_install_registry_path,
    discover_install,
    deterministic_fingerprint as install_deterministic_fingerprint,
    load_install_registry,
    merge_contract_ranges,
    merge_protocol_ranges,
    registry_add_install,
    registry_remove_install,
    sha256_file,
    stable_install_id,
    validate_install_manifest,
    verify_install_registry,
)
from src.lib.export import (
    export_instance_bundle,
    export_pack_bundle,
    export_save_bundle,
)
from src.release import (
    DEFAULT_INSTALL_PROFILE_ID,
    DEFAULT_RELEASE_RESOLUTION_POLICY_ID,
    DEFAULT_INSTALL_TRANSACTION_LOG_REL,
    DEFAULT_RELEASE_INDEX_REL,
    DEFAULT_RELEASE_MANIFEST_REL,
    RESOLUTION_POLICY_EXACT_SUITE,
    build_default_component_install_plan,
    canonicalize_release_resolution_policy,
    component_managed_paths,
    append_install_transaction,
    infer_release_index_path,
    infer_dist_root_from_manifest_path,
    load_install_transaction_log,
    load_release_index,
    load_release_manifest,
    load_install_profile_registry,
    load_release_resolution_policy_registry,
    platform_targets_for_tag,
    resolve_release_artifact_root,
    resolve_update_plan,
    select_install_profile,
    select_release_resolution_policy,
    select_rollback_transaction,
    verify_release_manifest,
)
from src.security.trust import (
    DEFAULT_LOCAL_TRUST_ROOT_REGISTRY_REL,
    DEFAULT_TRUST_POLICY_ID,
    DEFAULT_TRUST_POLICY_REGISTRY_REL,
    effective_trust_policy_id,
    load_trust_policy_registry,
    load_trust_root_registry,
    select_trust_policy,
    write_trust_root_registry,
)
from src.lib.save import resolve_save_manifest_path
from src.lib.store import DEFAULT_GC_POLICY_ID, resolve_store_root_from_install, run_store_gc
from tools.lib.content_store import initialize_store_root


DEFAULT_CAPABILITY_BASELINE = "BASELINE_MAINLINE_CORE"
NULL_UUID = "00000000-0000-0000-0000-000000000000"
DEFAULT_INSTALL_MANIFEST = "install.manifest.json"
DEFAULT_COMPAT_REPORT = "compat_report.json"
DEFAULT_SETUP_STATE = "setup_state.json"

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_REFUSED = 3


def _emit_setup_event(category: str, message_key: str, *, severity: str = "info", params: dict | None = None) -> None:
    log_emit(
        category=str(category or "").strip() or "lib",
        severity=str(severity or "info").strip() or "info",
        message_key=str(message_key or "").strip() or "appshell.log.event",
        params=dict(params or {}),
    )


def now_timestamp(deterministic: bool) -> str:
    if deterministic or os.environ.get("SETUP_DETERMINISTIC") == "1":
        return "2000-01-01T00:00:00Z"
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_path(path: str) -> str:
    if not path:
        return ""
    return os.path.abspath(path).replace("\\", "/")


def safe_rel(path: str, base: str) -> str:
    created_data_root = False
    try:
        rel = os.path.relpath(path, base)
    except ValueError:
        return os.path.basename(path)
    if rel.startswith(".."):
        return os.path.basename(path)
    return rel.replace("\\", "/")


def ensure_dir(path: str) -> None:
    if not path:
        return
    os.makedirs(path, exist_ok=True)


def write_json(path: str, payload: dict) -> None:
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def digest64(obj: dict) -> str:
    h = hashlib.sha256()
    h.update(canonical_bytes(obj))
    return base64.b64encode(h.digest()).decode("ascii")


def refusal_payload(code_id: int, code: str, message: str,
                    details: Optional[Dict[str, str]] = None) -> Dict[str, object]:
    return {
        "code_id": code_id,
        "code": code,
        "message": message,
        "details": details or {},
        "explanation_classification": "PUBLIC",
    }


def build_compat_report(context: str,
                        install_id: Optional[str],
                        instance_id: Optional[str],
                        runtime_id: Optional[str],
                        capability_baseline: Optional[str],
                        required_capabilities: Optional[List[str]],
                        provided_capabilities: Optional[List[str]],
                        missing_capabilities: Optional[List[str]],
                        compatibility_mode: str,
                        refusal_codes: Optional[List[str]],
                        mitigation_hints: Optional[List[str]],
                        deterministic: bool,
                        refusal: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    required = sorted({v for v in (required_capabilities or []) if v})
    provided = sorted({v for v in (provided_capabilities or []) if v})
    missing = sorted({v for v in (missing_capabilities or []) if v})
    if missing_capabilities is None:
        missing = sorted(set(required) - set(provided))
    payload = {
        "context": context,
        "install_id": install_id or NULL_UUID,
        "instance_id": instance_id or NULL_UUID,
        "runtime_id": runtime_id or NULL_UUID,
        "capability_baseline": capability_baseline or DEFAULT_CAPABILITY_BASELINE,
        "required_capabilities": required,
        "provided_capabilities": provided,
        "missing_capabilities": missing,
        "compatibility_mode": compatibility_mode,
        "refusal_codes": sorted({v for v in (refusal_codes or []) if v}),
        "mitigation_hints": sorted({v for v in (mitigation_hints or []) if v}),
        "timestamp": now_timestamp(deterministic),
        "extensions": {},
    }
    if refusal:
        payload["refusal"] = refusal
    return payload


def ops_log_path(root: str) -> str:
    return os.path.join(root, "ops", "ops.log")


def append_ops_log(root: str, entry: dict) -> None:
    ensure_dir(os.path.join(root, "ops"))
    with open(ops_log_path(root), "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


class SetupTransaction:
    def __init__(self, root: str, action: str, tx_id: str, deterministic: bool):
        self.root = root
        self.action = action
        self.tx_id = tx_id
        self.deterministic = deterministic

    def log(self, state: str, result: str,
            message: Optional[str] = None,
            refusal: Optional[dict] = None,
            details: Optional[dict] = None) -> None:
        entry = {
            "transaction_id": self.tx_id,
            "action": self.action,
            "state": state,
            "timestamp": now_timestamp(self.deterministic),
            "result": result,
        }
        if message:
            entry["message"] = message
        if refusal:
            entry["refusal"] = refusal
        if details:
            entry["details"] = details
        append_ops_log(self.root, entry)


def parse_deterministic(value: Optional[str]) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return bool(value)
    s = str(value).strip().lower()
    if s in ("1", "true", "yes", "on"):
        return True
    if s in ("0", "false", "no", "off", ""):
        return False
    return True


def derive_artifact_root(manifest_path: str, override: Optional[str]) -> str:
    if override:
        return normalize_path(override)
    manifest_dir = os.path.dirname(os.path.abspath(manifest_path))
    candidate = os.path.abspath(os.path.join(manifest_dir, os.pardir, os.pardir))
    if os.path.isdir(os.path.join(candidate, "payloads")):
        return candidate
    alt = os.path.abspath(os.path.join(manifest_dir, os.pardir))
    if os.path.isdir(os.path.join(alt, "payloads")):
        return alt
    return candidate


def payload_root_from_artifact(artifact_root: str, override: Optional[str]) -> str:
    if override:
        return normalize_path(override)
    return normalize_path(os.path.join(artifact_root, "payloads"))


def normalize_invocation_path(path: Optional[str]) -> str:
    if not path:
        return ""
    return normalize_path(path)


def resolve_ops_cli() -> str:
    return os.path.join(REPO_ROOT_HINT, "tools", "ops", "ops_cli.py")


def resolve_share_cli() -> str:
    return os.path.join(REPO_ROOT_HINT, "tools", "share", "share_cli.py")


def resolve_plan_migration_cli() -> str:
    return os.path.join(REPO_ROOT_HINT, "tools", "compat", "tool_plan_migration.py")


def resolve_apply_migration_cli() -> str:
    return os.path.join(REPO_ROOT_HINT, "tools", "compat", "tool_apply_migration.py")


def resolve_import_engine_module():
    return importlib.import_module("src.lib.import")


def _setup_vpath_context(store_root: str = "", install_root: str = "") -> dict:
    raw_args: List[str] = []
    if install_root:
        raw_args.extend(["--install-root", str(install_root)])
    if store_root:
        raw_args.extend(["--store-root", str(store_root)])
    return vpath_init(
        {
            "repo_root": REPO_ROOT_HINT,
            "product_id": "setup",
            "raw_args": raw_args,
            "executable_path": os.path.join(REPO_ROOT_HINT, "dist", "bin", "dominium_setup"),
        }
    )


def resolve_instance_manifest_path(instance_id: str, explicit_path: str = "", store_root: str = "") -> str:
    if explicit_path:
        return normalize_path(explicit_path)
    token = str(instance_id or "").strip()
    if not token:
        return ""
    candidates = []
    context = _setup_vpath_context(store_root=store_root)
    if str(context.get("result", "")).strip() == "complete":
        for root in vpath_candidate_roots(VROOT_INSTANCES, context):
            candidates.append(os.path.join(root, token, "instance.manifest.json"))
    elif store_root:
        candidates.append(os.path.join(normalize_path(store_root), "instances", token, "instance.manifest.json"))
    candidates.append(os.path.join(REPO_ROOT_HINT, "instances", token, "instance.manifest.json"))
    for candidate in candidates:
        if os.path.isfile(candidate):
            return normalize_path(candidate)
    return normalize_path(candidates[0]) if candidates else ""


def resolve_pack_root(pack_id: str, explicit_root: str = "") -> str:
    if explicit_root:
        return normalize_path(explicit_root)
    token = str(pack_id or "").strip()
    if not token:
        return ""
    context = _setup_vpath_context()
    candidates = []
    if str(context.get("result", "")).strip() == "complete":
        for root in vpath_candidate_roots(VROOT_PACKS, context):
            candidates.extend(
                [
                    os.path.join(root, token),
                    os.path.join(root, token.split(".", 1)[0], token),
                    os.path.join(root, "source", token),
                    os.path.join(root, "core", token),
                ]
            )
    else:
        candidates = [
            os.path.join(REPO_ROOT_HINT, "packs", token),
            os.path.join(REPO_ROOT_HINT, "packs", token.split(".", 1)[0], token),
            os.path.join(REPO_ROOT_HINT, "packs", "source", token),
            os.path.join(REPO_ROOT_HINT, "packs", "core", token),
        ]
    for candidate in candidates:
        if os.path.isdir(candidate):
            return normalize_path(candidate)
    return normalize_path(candidates[0])


def run_script(path: str, args: List[str]) -> Tuple[int, Dict[str, object], str]:
    cmd = [sys.executable, path] + list(args or [])
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = proc.stdout.decode("utf-8", errors="ignore").strip()
    stderr = proc.stderr.decode("utf-8", errors="ignore").strip()
    payload: Dict[str, object] = {}
    if stdout:
        try:
            payload = json.loads(stdout)
        except ValueError:
            payload = {}
    return proc.returncode, payload, stderr


def build_invocation(args: argparse.Namespace, deterministic: bool) -> dict:
    invocation = {
        "schema_version": 1,
        "op": args.op,
        "scope": args.scope,
        "platform": args.platform,
        "install_root": normalize_path(args.install_root) if args.install_root else "",
        "data_root": normalize_path(args.data_root) if getattr(args, "data_root", None) else "",
        "manifest_path": normalize_path(args.manifest) if args.manifest else "",
        "ui_mode": args.ui_mode or "cli",
        "frontend_id": args.frontend_id or "",
        "state_path": normalize_invocation_path(getattr(args, "state", None)),
        "install_mode": str(getattr(args, "install_mode", "") or "").strip(),
        "store_root": normalize_invocation_path(getattr(args, "store_root", None)),
        "created_at": now_timestamp(deterministic),
        "deterministic": 1 if deterministic else 0,
        "extensions": {},
    }
    return invocation


def load_invocation(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def make_plan(invocation: dict,
              manifest_path: str,
              payload_root: str,
              deterministic: bool,
              transaction_id: str) -> dict:
    plan = {
        "schema_version": 1,
        "op": invocation.get("op", ""),
        "scope": invocation.get("scope", ""),
        "platform": invocation.get("platform", ""),
        "install_root": invocation.get("install_root", ""),
        "data_root": invocation.get("data_root", ""),
        "manifest_path": normalize_path(manifest_path),
        "payload_root": normalize_path(payload_root),
        "ui_mode": invocation.get("ui_mode", "cli"),
        "frontend_id": invocation.get("frontend_id", ""),
        "install_mode": str(invocation.get("install_mode", "")).strip(),
        "store_root": str(invocation.get("store_root", "")).strip(),
        "invocation_digest64": digest64(invocation),
        "transaction_id": transaction_id,
        "created_at": now_timestamp(deterministic),
        "extensions": {},
    }
    return plan


def ensure_file(path: str, content: bytes = b"") -> None:
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "wb") as handle:
        handle.write(content)


def copy_tree(src: str, dst: str, overwrite: bool = True) -> None:
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        rel = "" if rel == "." else rel
        target_root = os.path.join(dst, rel)
        ensure_dir(target_root)
        for name in files:
            src_path = os.path.join(root, name)
            dst_path = os.path.join(target_root, name)
            if not overwrite and os.path.exists(dst_path):
                continue
            shutil.copy2(src_path, dst_path)


def sync_tree(src: str, dst: str) -> None:
    def _sha256(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        rel = "" if rel == "." else rel
        target_root = os.path.join(dst, rel)
        ensure_dir(target_root)
        for name in files:
            src_path = os.path.join(root, name)
            dst_path = os.path.join(target_root, name)
            if not os.path.exists(dst_path):
                shutil.copy2(src_path, dst_path)
                continue
            if os.path.getsize(src_path) != os.path.getsize(dst_path):
                shutil.copy2(src_path, dst_path)
                continue
            if _sha256(src_path) != _sha256(dst_path):
                shutil.copy2(src_path, dst_path)
                continue


def detect_network_status(mode: str) -> Tuple[str, Optional[str]]:
    mode = (mode or "auto").strip().lower()
    if mode == "offline":
        return "offline", "offline mode requested"
    if mode in ("online", "auto"):
        env_flag = os.environ.get("SETUP_NETWORK_AVAILABLE", "").strip()
        if env_flag in ("0", "false", "no", "off"):
            return "offline", "network unavailable; continuing offline"
        return "online", None
    return "unknown", None


PRODUCT_BINARY_SPECS = (
    {"product_id": "engine", "version_key": "engine_version", "candidates": ("dominium_engine", "domino_engine")},
    {"product_id": "game", "version_key": "game_version", "candidates": ("dominium_game", "dominium-game")},
    {"product_id": "client", "version_key": "game_version", "candidates": ("dominium_client", "dominium-client")},
    {"product_id": "server", "version_key": "game_version", "candidates": ("dominium_server", "dominium-server")},
    {"product_id": "launcher", "version_key": "launcher_version", "candidates": ("dominium-launcher", "dominium_launcher")},
    {"product_id": "setup", "version_key": "setup_version", "candidates": ("dominium-setup", "dominium_setup", "setup_cli.py")},
)


def _semantic_contract_registry_payload() -> dict:
    path = os.path.join(REPO_ROOT_HINT, "data", "registries", "semantic_contract_registry.json")
    return load_json(path)


def _semantic_contract_registry_hash() -> str:
    return hashlib.sha256(canonical_bytes(_semantic_contract_registry_payload())).hexdigest()


def _store_root_ref_payload(install_root: str, store_root: str, store_id: str) -> dict:
    payload = {"store_id": str(store_id or "").strip() or "store.default"}
    try:
        root_rel = os.path.relpath(store_root, install_root).replace("\\", "/")
        manifest_rel = os.path.relpath(os.path.join(store_root, "store.root.json"), install_root).replace("\\", "/")
    except ValueError:
        root_rel = ""
        manifest_rel = ""
    if root_rel:
        payload["root_path"] = root_rel
    if manifest_rel:
        payload["manifest_ref"] = manifest_rel
    return payload


def _install_version_for_products(product_rows: List[dict], versions: dict) -> str:
    preferred = ("game", "client", "server", "engine", "launcher", "setup")
    by_id = {str(row.get("product_id", "")).strip(): row for row in list(product_rows or [])}
    for product_id in preferred:
        row = dict(by_id.get(product_id) or {})
        if row.get("product_version"):
            return str(row.get("product_version")).strip()
    for key in ("game_version", "engine_version", "launcher_version", "setup_version", "tools_version"):
        token = str(versions.get(key, "")).strip()
        if token:
            return token
    return "0.0.0"


def _descriptor_sidecar_path(stage_root: str, binary_relpath: str) -> str:
    root, _ext = os.path.splitext(binary_relpath)
    return os.path.join(stage_root, root + ".descriptor.json")


def _discover_install_products(stage_root: str, versions: dict) -> List[dict]:
    products = []
    seen = set()
    for spec in PRODUCT_BINARY_SPECS:
        product_id = str(spec["product_id"])
        for candidate in spec["candidates"]:
            binary_path = os.path.join(stage_root, "bin", candidate)
            if not os.path.isfile(binary_path):
                continue
            if product_id in seen:
                break
            version_key = str(spec["version_key"])
            product_version = str(versions.get(version_key, "0.0.0")).strip() or "0.0.0"
            build_meta = build_product_build_metadata(REPO_ROOT_HINT, product_id)
            descriptor = build_product_descriptor(REPO_ROOT_HINT, product_id=product_id, product_version=product_version)
            binary_relpath = os.path.relpath(binary_path, stage_root).replace("\\", "/")
            descriptor_relpath = os.path.relpath(_descriptor_sidecar_path(stage_root, binary_relpath), stage_root).replace("\\", "/")
            write_json(os.path.join(stage_root, descriptor_relpath), descriptor)
            products.append(
                {
                    "product_id": product_id,
                    "product_version": product_version,
                    "build_id": str(build_meta.get("build_id", "")).strip(),
                    "binary_relpath": binary_relpath,
                    "descriptor_relpath": descriptor_relpath,
                    "binary_hash": sha256_file(binary_path),
                    "endpoint_descriptor_hash": hashlib.sha256(canonical_bytes(descriptor)).hexdigest(),
                    "descriptor": descriptor,
                    "build_meta": build_meta,
                }
            )
            seen.add(product_id)
            break
    return sorted(products, key=lambda row: str(row.get("product_id", "")))


def install_manifest_payload(install_id: str,
                             install_root: str,
                             store_root: str,
                             mode: str,
                             created_at: str,
                             build_number: int,
                             versions: dict,
                             stage_root: str) -> dict:
    product_rows = _discover_install_products(stage_root, versions)
    product_builds = {}
    product_build_descriptors = {}
    binaries = {}
    supported_capabilities = set()
    protocol_rows = []
    contract_rows = []

    for row in product_rows:
        product_id = str(row.get("product_id", "")).strip()
        descriptor = dict(row.get("descriptor") or {})
        product_builds[product_id] = str(row.get("build_id", "")).strip()
        product_build_descriptors[product_id] = build_product_build_descriptor(
            product_id=product_id,
            build_id=str(row.get("build_id", "")).strip(),
            binary_hash=str(row.get("binary_hash", "")).strip(),
            endpoint_descriptor_hash=str(row.get("endpoint_descriptor_hash", "")).strip(),
            binary_ref=str(row.get("binary_relpath", "")).strip(),
            descriptor_ref=str(row.get("descriptor_relpath", "")).strip(),
            product_version=str(row.get("product_version", "")).strip(),
        )
        binaries[product_id] = {
            "product_id": product_id,
            "product_version": str(row.get("product_version", "")).strip(),
            "build_id": str(row.get("build_id", "")).strip(),
            "binary_ref": str(row.get("binary_relpath", "")).strip(),
            "descriptor_ref": str(row.get("descriptor_relpath", "")).strip(),
            "binary_hash": str(row.get("binary_hash", "")).strip(),
            "endpoint_descriptor_hash": str(row.get("endpoint_descriptor_hash", "")).strip(),
            "extensions": {},
        }
        supported_capabilities.update(list(descriptor.get("feature_capabilities") or []))
        protocol_rows.extend(list(descriptor.get("protocol_versions_supported") or []))
        contract_rows.extend(list(descriptor.get("semantic_contract_versions_supported") or []))

    supported_protocol_versions = merge_protocol_ranges(protocol_rows)
    supported_contract_ranges = merge_contract_ranges(contract_rows)
    protocol_versions = {
        "network": str(versions.get("protocol_network", "0")).strip() or "0",
        "save": str(versions.get("protocol_save", "0")).strip() or "0",
        "mod": str(versions.get("protocol_mod", "0")).strip() or "0",
        "replay": str(versions.get("protocol_replay", "0")).strip() or "0",
    }
    payload = {
        "install_id": install_id,
        "install_version": _install_version_for_products(product_rows, versions),
        "product_builds": dict((key, product_builds[key]) for key in sorted(product_builds.keys())),
        "product_build_ids": dict((key, product_builds[key]) for key in sorted(product_builds.keys())),
        "semantic_contract_registry_hash": _semantic_contract_registry_hash(),
        "supported_protocol_versions": dict((key, supported_protocol_versions[key]) for key in sorted(supported_protocol_versions.keys())),
        "supported_contract_ranges": dict((key, supported_contract_ranges[key]) for key in sorted(supported_contract_ranges.keys())),
        "default_mod_policy_id": "mod.policy.default",
        "store_root_ref": _store_root_ref_payload(install_root, store_root, "store.default"),
        "mode": mode,
        "install_root": ".",
        "binaries": dict((key, binaries[key]) for key in sorted(binaries.keys())),
        "product_build_descriptors": dict((key, product_build_descriptors[key]) for key in sorted(product_build_descriptors.keys())),
        "supported_capabilities": sorted(supported_capabilities),
        "protocol_versions": protocol_versions,
        "build_identity": int(build_number),
        "trust_tier": versions.get("trust_tier", "official"),
        "created_at": created_at,
        "extensions": {
            "official.semantic_contract_registry_ref": "semantic_contract_registry.json",
            "official.trust_policy_id": DEFAULT_TRUST_POLICY_ID,
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = install_deterministic_fingerprint(payload)
    return payload


def setup_state_payload(install_id: str,
                        manifest_path: str,
                        data_root: str,
                        ui_mode: str,
                        created_at: str) -> dict:
    return {
        "install_id": install_id,
        "manifest_path": normalize_path(manifest_path),
        "data_root": normalize_path(data_root),
        "ui_mode": ui_mode,
        "created_at": created_at,
        "extensions": {},
    }


def read_setup_state(install_root: str) -> Optional[dict]:
    path = os.path.join(install_root, DEFAULT_SETUP_STATE)
    if not os.path.isfile(path):
        return None
    try:
        return load_json(path)
    except Exception:
        return None


def latest_backup(index_path: str) -> Optional[dict]:
    if not os.path.isfile(index_path):
        return None
    try:
        data = load_json(index_path)
    except Exception:
        return None
    items = data.get("backups", [])
    if not items:
        return None
    return items[-1]


def append_backup(index_path: str, entry: dict) -> None:
    data = {"backups": []}
    if os.path.isfile(index_path):
        try:
            data = load_json(index_path)
        except Exception:
            data = {"backups": []}
    data.setdefault("backups", [])
    data["backups"].append(entry)
    write_json(index_path, data)


def backup_install_root(install_root: str, data_root: str, tx_id: str, deterministic: bool) -> str:
    backup_root = install_root + ".rollback." + tx_id
    if os.path.exists(backup_root):
        shutil.rmtree(backup_root, ignore_errors=True)
    ensure_dir(backup_root)
    data_root_abs = normalize_path(data_root)
    install_root_abs = normalize_path(install_root)
    skip_data = data_root_abs.startswith(install_root_abs)
    for root, dirs, files in os.walk(install_root):
        rel = os.path.relpath(root, install_root)
        rel = "" if rel == "." else rel
        target_root = os.path.join(backup_root, rel)
        if skip_data and data_root_abs.startswith(normalize_path(os.path.join(install_root, rel))):
            if normalize_path(root) == data_root_abs:
                dirs[:] = []
                files[:] = []
                continue
        ensure_dir(target_root)
        for name in files:
            src_path = os.path.join(root, name)
            dst_path = os.path.join(target_root, name)
            shutil.copy2(src_path, dst_path)
    return backup_root


def transaction_log_path(install_root: str) -> str:
    return os.path.join(normalize_path(install_root), DEFAULT_INSTALL_TRANSACTION_LOG_REL.replace("/", os.sep))


def _update_refusal(code: str, reason: str, remediation: Optional[List[str]] = None) -> dict:
    details = {"remediation": sorted({str(item).strip() for item in (remediation or []) if str(item).strip()})}
    return refusal_payload(5, code, reason, details)


def _trust_root_local_registry_path(install_root: str) -> str:
    return os.path.join(normalize_path(install_root), DEFAULT_LOCAL_TRUST_ROOT_REGISTRY_REL.replace("/", os.sep))


def _load_effective_trust_policy(
    *,
    install_root: str = "",
    install_manifest: Optional[dict] = None,
    requested_trust_policy_id: str = "",
    mod_policy_id: str = "",
) -> tuple[str, dict]:
    effective_id = effective_trust_policy_id(
        requested_trust_policy_id=str(requested_trust_policy_id or "").strip(),
        install_manifest=dict(install_manifest or {}),
        mod_policy_id=str(mod_policy_id or "").strip(),
    )
    policy_registry_root = REPO_ROOT_HINT
    if install_root:
        bundle_registry_path = os.path.join(normalize_path(install_root), DEFAULT_TRUST_POLICY_REGISTRY_REL.replace("/", os.sep))
        if os.path.isfile(bundle_registry_path):
            policy_registry_root = normalize_path(install_root)
    policy_registry = load_trust_policy_registry(repo_root=policy_registry_root)
    return effective_id, select_trust_policy(policy_registry, trust_policy_id=effective_id)


def _load_imported_trust_root_rows(bundle_path: str) -> list[dict]:
    payload = load_json(bundle_path)
    if isinstance(payload.get("trust_roots"), list):
        return [dict(row or {}) for row in list(payload.get("trust_roots") or []) if isinstance(row, dict)]
    if isinstance(dict(payload.get("record") or {}).get("trust_roots"), list):
        return [dict(row or {}) for row in list(dict(payload.get("record") or {}).get("trust_roots") or []) if isinstance(row, dict)]
    if str(payload.get("signer_id", "")).strip():
        return [dict(payload)]
    return []


def _governance_status_payload(install_root: str = "") -> dict:
    install_root_token = normalize_path(install_root) if str(install_root or "").strip() else ""
    profile_path = governance_profile_path(REPO_ROOT_HINT, install_root=install_root_token)
    profile_payload = load_governance_profile(REPO_ROOT_HINT, install_root=install_root_token)
    registry_payload = load_governance_mode_registry(REPO_ROOT_HINT)
    mode_row = select_governance_mode_row(registry_payload, str(profile_payload.get("governance_mode_id", "")).strip())
    profile_hash = governance_profile_hash(profile_payload) if profile_payload else ""
    release_index_path = os.path.join(install_root_token, DEFAULT_RELEASE_INDEX_REL.replace("/", os.sep)) if install_root_token else ""
    release_index_payload = load_release_index(release_index_path) if release_index_path and os.path.isfile(release_index_path) else {}
    release_governance_hash = str(release_index_payload.get("governance_profile_hash", "")).strip().lower()
    if install_root_token:
        profile_source = "install" if normalize_path(profile_path).startswith(install_root_token) else "repo_fallback"
    else:
        profile_source = "repo_default"
    return {
        "install_root": install_root_token,
        "governance_profile_path": normalize_path(profile_path) if profile_path else "",
        "governance_profile_hash": profile_hash,
        "governance_profile": profile_payload,
        "governance_mode": mode_row,
        "governance_profile_source": profile_source,
        "release_index_path": normalize_path(release_index_path) if release_index_path and os.path.isfile(release_index_path) else "",
        "release_index_governance_hash": release_governance_hash,
        "release_index_governance_match": bool(release_governance_hash) and release_governance_hash == profile_hash,
    }


def _discover_install_context(args: argparse.Namespace) -> dict:
    raw_args: List[str] = []
    if getattr(args, "install_root", ""):
        raw_args.extend(["--install-root", str(getattr(args, "install_root", "")).strip()])
    if getattr(args, "install_id", ""):
        raw_args.extend(["--install-id", str(getattr(args, "install_id", "")).strip()])
    if getattr(args, "registry_path", ""):
        raw_args.extend(["--install-registry-path", str(getattr(args, "registry_path", "")).strip()])
    return discover_install(
        raw_args=raw_args,
        executable_path=os.path.abspath(sys.argv[0]),
        cwd=os.getcwd(),
        env=os.environ,
    )


def _load_install_profile_for_root(install_root: str, install_profile_id: str) -> dict:
    registry = load_install_profile_registry(normalize_path(install_root))
    profile = select_install_profile(registry, install_profile_id=install_profile_id)
    if profile:
        return profile
    return select_install_profile(load_install_profile_registry(REPO_ROOT_HINT), install_profile_id=install_profile_id)


def _load_release_resolution_policy_for_root(install_root: str, resolution_policy_id: str) -> dict:
    registry = load_release_resolution_policy_registry(normalize_path(install_root))
    policy = select_release_resolution_policy(registry, policy_id=resolution_policy_id)
    if policy:
        return policy
    return select_release_resolution_policy(load_release_resolution_policy_registry(REPO_ROOT_HINT), policy_id=resolution_policy_id)


def _managed_paths_from_rows(rows: List[dict]) -> List[str]:
    out: List[str] = []
    for row in rows:
        out.extend(component_managed_paths(dict(row or {})))
    return sorted({str(path).strip().replace("\\", "/") for path in out if str(path).strip()})


def _remove_managed_paths(install_root: str, rows: List[dict]) -> None:
    for rel_path in _managed_paths_from_rows(rows):
        target = os.path.join(install_root, rel_path.replace("/", os.sep))
        if os.path.isdir(target):
            shutil.rmtree(target, ignore_errors=True)
        elif os.path.isfile(target):
            os.remove(target)


def _copy_managed_paths(source_root: str, install_root: str, rows: List[dict]) -> None:
    for rel_path in _managed_paths_from_rows(rows):
        source = os.path.join(source_root, rel_path.replace("/", os.sep))
        target = os.path.join(install_root, rel_path.replace("/", os.sep))
        if os.path.isdir(source):
            if os.path.isdir(target):
                shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(source, target)
            continue
        if not os.path.isfile(source):
            continue
        ensure_dir(os.path.dirname(target))
        setup_target = normalize_path(os.path.join(install_root, "bin", "setup"))
        if normalize_path(target) == setup_target:
            staged = target + ".new"
            shutil.copyfile(source, staged)
            os.replace(staged, target)
            continue
        shutil.copyfile(source, target)


def _merge_install_manifest_for_update(current_manifest: dict, source_manifest: dict, update_plan: dict) -> dict:
    current_payload = normalize_install_manifest(dict(current_manifest or {}))
    source_payload = normalize_install_manifest(dict(source_manifest or {}))
    merged = dict(source_payload)
    merged["install_id"] = str(current_payload.get("install_id", "")).strip() or str(source_payload.get("install_id", "")).strip()
    merged["mode"] = str(current_payload.get("mode", "")).strip() or str(source_payload.get("mode", "")).strip()
    merged["store_root_ref"] = dict(current_payload.get("store_root_ref") or source_payload.get("store_root_ref") or {})
    merged["install_root"] = "."
    merged.setdefault("extensions", {})
    merged["extensions"] = dict(source_payload.get("extensions") or {})
    merged["extensions"]["official.install_profile_id"] = str(update_plan.get("install_profile_id", "")).strip() or str(merged["extensions"].get("official.install_profile_id", "")).strip()
    merged["extensions"]["official.install_resolution_policy_id"] = (
        str(update_plan.get("resolution_policy_id", "")).strip()
        or str(merged["extensions"].get("official.install_resolution_policy_id", "")).strip()
        or DEFAULT_RELEASE_RESOLUTION_POLICY_ID
    )
    merged["extensions"]["official.trust_policy_id"] = (
        str(dict(current_payload.get("extensions") or {}).get("official.trust_policy_id", "")).strip()
        or str(merged["extensions"].get("official.trust_policy_id", "")).strip()
        or DEFAULT_TRUST_POLICY_ID
    )
    merged["extensions"]["official.selected_component_ids"] = list(dict(update_plan.get("extensions") or {}).get("target_selected_component_ids") or [])
    merged["extensions"]["official.selected_component_descriptors"] = list(dict(update_plan.get("extensions") or {}).get("target_selected_component_descriptors") or [])
    merged["deterministic_fingerprint"] = install_deterministic_fingerprint(merged)
    return merged


def write_output(payload: dict, fmt: str) -> None:
    if fmt == "text":
        msg = payload.get("message") or payload.get("result") or ""
        print(msg)
        return
    print(json.dumps(payload, indent=2))


def output_refusal(message: str, refusal: dict, fmt: str) -> None:
    refusal_row = dict(refusal or {})
    _emit_setup_event(
        "refusal",
        "appshell.refusal",
        severity="error",
        params={
            "refusal_code": str(refusal_row.get("reason_code", "")).strip(),
            "reason": str(refusal_row.get("message", "")).strip() or str(message or "").strip(),
            "remediation_hint": str(refusal_row.get("remediation_hint", "")).strip(),
        },
    )
    write_output({
        "result": "refused",
        "message": message,
        "refusal": refusal,
    }, fmt)


def output_error(message: str, fmt: str) -> None:
    write_output({
        "result": "error",
        "message": message,
    }, fmt)


def output_ok(message: str, details: dict, fmt: str) -> None:
    payload = {"result": "ok", "message": message}
    payload.update(details)
    write_output(payload, fmt)


def bridge_engine_payload(payload: dict, success_message: str) -> dict:
    result = str((payload or {}).get("result", "")).strip()
    if result == "complete":
        bridged = {
            "result": "ok",
            "message": success_message,
            "details": dict(payload or {}),
        }
        bridged["details"].setdefault("engine_result", result)
        return bridged
    if result == "refusal":
        refusal = dict((payload or {}).get("refusal") or {})
        return {
            "result": "refused",
            "message": str((payload or {}).get("message", "")).strip() or "operation refused",
            "refusal": refusal,
            "details": dict(payload or {}),
        }
    if result == "error":
        return {
            "result": "error",
            "message": str((payload or {}).get("message", "")).strip() or "operation failed",
            "details": dict(payload or {}),
        }
    return dict(payload or {})


def _compat_root(path: Optional[str]) -> str:
    token = normalize_path(path or "")
    return token


def _verify_pack_root(
    *,
    root: str,
    bundle_id: str,
    mod_policy_id: str,
    overlay_conflict_policy_id: str,
    schema_root: str,
    universe_contract_bundle_path: str,
    trust_policy_id: str,
) -> dict:
    return appshell_verify_pack_root(
        repo_root=REPO_ROOT_HINT,
        root=root,
        bundle_id=str(bundle_id or "").strip(),
        mod_policy_id=str(mod_policy_id or "").strip() or "mod_policy.lab",
        overlay_conflict_policy_id=str(overlay_conflict_policy_id or "").strip(),
        contract_bundle_path=str(universe_contract_bundle_path or "").strip(),
        trust_policy_id=str(trust_policy_id or "").strip(),
    )


def _write_verification_outputs(
    *,
    root: str,
    report: dict,
    pack_lock: dict,
    report_path: Optional[str],
    lock_path: Optional[str],
) -> dict:
    from src.packs.compat import write_pack_compatibility_outputs

    report_target = normalize_path(report_path or os.path.join(root, DEFAULT_COMPAT_REPORT))
    lock_target = normalize_path(lock_path or os.path.join(root, "pack_lock.json"))
    return write_pack_compatibility_outputs(
        report_path=report_target,
        report_payload=report,
        pack_lock_path=lock_target if pack_lock else "",
        pack_lock_payload=pack_lock if pack_lock else None,
    )


def handle_verify(args: argparse.Namespace, deterministic: bool) -> int:
    del deterministic
    release_manifest_path = normalize_path(getattr(args, "release_manifest", ""))
    if release_manifest_path:
        root = _compat_root(getattr(args, "root", "") or getattr(args, "install_root", ""))
        if not root:
            root = normalize_path(infer_dist_root_from_manifest_path(release_manifest_path))
        install_manifest = {}
        install_manifest_path = os.path.join(root, DEFAULT_INSTALL_MANIFEST)
        if os.path.isfile(install_manifest_path):
            validation = validate_install_manifest(repo_root=REPO_ROOT_HINT, install_manifest_path=install_manifest_path)
            install_manifest = dict(validation.get("install_manifest") or {})
        effective_policy_id, _policy_row = _load_effective_trust_policy(
            install_root=root,
            install_manifest=install_manifest,
            requested_trust_policy_id=str(getattr(args, "trust_policy_id", "") or "").strip(),
        )
        verification = verify_release_manifest(
            root,
            release_manifest_path,
            repo_root=REPO_ROOT_HINT,
            trust_policy_id=effective_policy_id,
        )
        details = {
            "root": root,
            "release_manifest_path": release_manifest_path,
            "release_id": str(verification.get("release_id", "")),
            "manifest_hash": str(verification.get("manifest_hash", "")),
            "verified_artifact_count": int(verification.get("verified_artifact_count", 0)),
            "trust_policy_id": effective_policy_id,
            "warnings": list(verification.get("warnings") or []),
            "errors": list(verification.get("errors") or []),
        }
        if str(verification.get("result", "")).strip() == "complete":
            output_ok("release manifest verification passed", details, args.format)
            return EXIT_OK
        error_codes = sorted(
            {
                str(dict(row or {}).get("code", "")).strip()
                for row in list(verification.get("errors") or [])
                if str(dict(row or {}).get("code", "")).strip()
            }
        )
        refusal = refusal_payload(
            5,
            "REFUSE_RELEASE_MANIFEST_INVALID",
            "release manifest verification failed",
            {
                "manifest_hash": str(verification.get("manifest_hash", "")),
                "error_codes": ",".join(error_codes),
            },
        )
        output_refusal("release manifest verification failed", refusal, args.format)
        return EXIT_REFUSED

    root = _compat_root(getattr(args, "root", "") or getattr(args, "install_root", ""))
    if not root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "verification root is required", {})
        output_refusal("missing verification root", refusal, args.format)
        return EXIT_REFUSED
    schema_root = _compat_root(getattr(args, "schema_root", "") or root)
    effective_policy_id, _policy_row = _load_effective_trust_policy(
        install_root=root,
        install_manifest={},
        requested_trust_policy_id=str(getattr(args, "trust_policy_id", "") or "").strip(),
        mod_policy_id=str(getattr(args, "mod_policy_id", "") or "").strip(),
    )
    verification = _verify_pack_root(
        root=root,
        bundle_id=getattr(args, "bundle_id", ""),
        mod_policy_id=getattr(args, "mod_policy_id", ""),
        overlay_conflict_policy_id=getattr(args, "overlay_conflict_policy_id", ""),
        schema_root=schema_root,
        universe_contract_bundle_path=getattr(args, "contract_bundle_path", ""),
        trust_policy_id=effective_policy_id,
    )
    if str(verification.get("result", "")) != "complete":
        refusal = refusal_payload(
            5,
            "REFUSE_PACK_VERIFICATION_FAILED",
            "offline verification pipeline failed",
            {"root": root},
        )
        output_refusal("pack verification failed", refusal, args.format)
        return EXIT_REFUSED
    report = dict(verification.get("report") or {})
    pack_lock = dict(verification.get("pack_lock") or {})
    outputs = {}
    if bool(getattr(args, "write_outputs", False)) or getattr(args, "out_report", None) or getattr(args, "out_lock", None):
        outputs = _write_verification_outputs(
            root=root,
            report=report,
            pack_lock=pack_lock,
            report_path=getattr(args, "out_report", None),
            lock_path=getattr(args, "out_lock", None),
        )
    details = {
        "root": root,
        "schema_root": schema_root,
        "trust_policy_id": effective_policy_id,
        "report": report,
        "pack_lock": pack_lock,
        "warnings": list(verification.get("warnings") or []),
        "errors": list(verification.get("errors") or []),
    }
    if outputs:
        details["outputs"] = outputs
    if bool(report.get("valid", False)):
        output_ok("pack verification passed", details, args.format)
        return EXIT_OK
    refusal = refusal_payload(
        5,
        "REFUSE_PACK_SET_INVALID",
        "pack set is incompatible with current contracts, policies, or registries",
        {
            "report_id": str(report.get("report_id", "")),
            "refusal_codes": ",".join(str(item) for item in list(report.get("refusal_codes") or [])),
        },
    )
    output_refusal("pack verification refused", refusal, args.format)
    return EXIT_REFUSED


def handle_list_packs(args: argparse.Namespace, deterministic: bool) -> int:
    del deterministic
    root = _compat_root(getattr(args, "root", ""))
    if not root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "verification root is required", {})
        output_refusal("missing verification root", refusal, args.format)
        return EXIT_REFUSED
    schema_root = _compat_root(getattr(args, "schema_root", "") or root)
    verification = _verify_pack_root(
        root=root,
        bundle_id=getattr(args, "bundle_id", ""),
        mod_policy_id=getattr(args, "mod_policy_id", ""),
        overlay_conflict_policy_id=getattr(args, "overlay_conflict_policy_id", ""),
        schema_root=schema_root,
        universe_contract_bundle_path=getattr(args, "contract_bundle_path", ""),
        trust_policy_id=str(getattr(args, "trust_policy_id", "") or "").strip(),
    )
    if str(verification.get("result", "")) != "complete":
        refusal = refusal_payload(5, "REFUSE_PACK_VERIFICATION_FAILED", "offline verification pipeline failed", {"root": root})
        output_refusal("pack listing failed", refusal, args.format)
        return EXIT_REFUSED
    report = dict(verification.get("report") or {})
    output_ok(
        "packs listed",
        {
            "details": {
                "root": root,
                "valid": bool(report.get("valid", False)),
                "pack_list": list(report.get("pack_list") or []),
                "refused_packs": list(report.get("refused_packs") or []),
                "conflicts": list(report.get("conflicts") or []),
            }
        },
        args.format,
    )
    return EXIT_OK


def handle_build_lock(args: argparse.Namespace, deterministic: bool) -> int:
    del deterministic
    root = _compat_root(getattr(args, "root", ""))
    if not root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "verification root is required", {})
        output_refusal("missing verification root", refusal, args.format)
        return EXIT_REFUSED
    schema_root = _compat_root(getattr(args, "schema_root", "") or root)
    verification = _verify_pack_root(
        root=root,
        bundle_id=getattr(args, "bundle_id", ""),
        mod_policy_id=getattr(args, "mod_policy_id", ""),
        overlay_conflict_policy_id=getattr(args, "overlay_conflict_policy_id", ""),
        schema_root=schema_root,
        universe_contract_bundle_path=getattr(args, "contract_bundle_path", ""),
        trust_policy_id=str(getattr(args, "trust_policy_id", "") or "").strip(),
    )
    if str(verification.get("result", "")) != "complete":
        refusal = refusal_payload(5, "REFUSE_PACK_VERIFICATION_FAILED", "offline verification pipeline failed", {"root": root})
        output_refusal("build-lock failed", refusal, args.format)
        return EXIT_REFUSED
    report = dict(verification.get("report") or {})
    pack_lock = dict(verification.get("pack_lock") or {})
    if not bool(report.get("valid", False)) or not pack_lock:
        refusal = refusal_payload(
            5,
            "REFUSE_PACK_SET_INVALID",
            "cannot build pack lock from an invalid pack set",
            {"report_id": str(report.get("report_id", ""))},
        )
        output_refusal("build-lock refused", refusal, args.format)
        return EXIT_REFUSED
    outputs = _write_verification_outputs(
        root=root,
        report=report,
        pack_lock=pack_lock,
        report_path=getattr(args, "out_report", None),
        lock_path=getattr(args, "out_lock", None),
    )
    output_ok(
        "pack lock built",
        {
            "details": {
                "root": root,
                "report": report,
                "pack_lock": pack_lock,
                "outputs": outputs,
            }
        },
        args.format,
    )
    return EXIT_OK


def handle_diagnose_pack(args: argparse.Namespace, deterministic: bool) -> int:
    del deterministic
    root = _compat_root(getattr(args, "root", ""))
    pack_id = str(getattr(args, "pack_id", "")).strip()
    if not root or not pack_id:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "verification root and pack_id are required", {})
        output_refusal("missing diagnose inputs", refusal, args.format)
        return EXIT_REFUSED
    schema_root = _compat_root(getattr(args, "schema_root", "") or root)
    verification = _verify_pack_root(
        root=root,
        bundle_id=getattr(args, "bundle_id", ""),
        mod_policy_id=getattr(args, "mod_policy_id", ""),
        overlay_conflict_policy_id=getattr(args, "overlay_conflict_policy_id", ""),
        schema_root=schema_root,
        universe_contract_bundle_path=getattr(args, "contract_bundle_path", ""),
        trust_policy_id=str(getattr(args, "trust_policy_id", "") or "").strip(),
    )
    if str(verification.get("result", "")) != "complete":
        refusal = refusal_payload(5, "REFUSE_PACK_VERIFICATION_FAILED", "offline verification pipeline failed", {"root": root})
        output_refusal("diagnose-pack failed", refusal, args.format)
        return EXIT_REFUSED
    report = dict(verification.get("report") or {})
    pack_row = {}
    for row in list(report.get("pack_list") or []):
        if str((row or {}).get("pack_id", "")).strip() == pack_id:
            pack_row = dict(row or {})
            break
    refusal_row = {}
    for row in list(report.get("refused_packs") or []):
        if str((row or {}).get("pack_id", "")).strip() == pack_id:
            refusal_row = dict(row or {})
            break
    if not pack_row and not refusal_row:
        refusal = refusal_payload(1, "REFUSE_PACK_NOT_FOUND", "pack_id not present in verification scope", {"pack_id": pack_id})
        output_refusal("pack not found", refusal, args.format)
        return EXIT_REFUSED
    output_ok(
        "pack diagnosed",
        {
            "details": {
                "root": root,
                "pack_id": pack_id,
                "pack": pack_row,
                "refusal": refusal_row,
                "report_id": str(report.get("report_id", "")),
                "valid": bool(report.get("valid", False)),
            }
        },
        args.format,
    )
    return EXIT_OK


def handle_export_invocation(args: argparse.Namespace, deterministic: bool) -> int:
    if not args.manifest:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "manifest is required", {})
        output_refusal("missing manifest", refusal, args.format)
        return EXIT_REFUSED
    if not args.out:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "output path is required", {})
        output_refusal("missing output", refusal, args.format)
        return EXIT_REFUSED
    invocation = build_invocation(args, deterministic)
    write_json(args.out, invocation)
    output_ok("invocation exported", {
        "details": {
            "invocation_path": normalize_path(args.out),
            "invocation_digest64": digest64(invocation),
        }
    }, args.format)
    return EXIT_OK


def handle_plan(args: argparse.Namespace, deterministic: bool) -> int:
    if not args.manifest:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "manifest is required", {})
        output_refusal("missing manifest", refusal, args.format)
        return EXIT_REFUSED
    if not args.out and not args.out_plan:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "plan output is required", {})
        output_refusal("missing plan output", refusal, args.format)
        return EXIT_REFUSED
    if args.invocation:
        invocation = load_invocation(args.invocation)
    elif args.request:
        invocation = load_invocation(args.request)
    else:
        invocation = build_invocation(args, deterministic)
    tx_id = args.transaction_id or str(uuid.uuid5(uuid.NAMESPACE_URL, digest64(invocation)))
    artifact_root = derive_artifact_root(args.manifest, args.artifact_root)
    payload_root = payload_root_from_artifact(artifact_root, args.payload_root)
    plan = make_plan(invocation, args.manifest, payload_root, deterministic, tx_id)
    plan_path = args.out_plan or args.out
    write_json(plan_path, plan)
    if args.format == "json":
        write_output({
            "result": "ok",
            "message": "plan created",
            "details": {
                "plan_path": normalize_path(plan_path),
                "invocation_digest64": plan["invocation_digest64"],
            },
            "plan": plan,
        }, args.format)
    else:
        write_output({
            "result": "ok",
            "message": "plan created",
            "details": {
                "plan_path": normalize_path(plan_path),
                "invocation_digest64": plan["invocation_digest64"],
            },
        }, args.format)
    return EXIT_OK


def install_from_plan(plan: dict, args: argparse.Namespace, deterministic: bool) -> Tuple[int, dict]:
    install_root = plan.get("install_root") or args.install_root or ""
    data_root = plan.get("data_root") or args.data_root or ""
    manifest_path = plan.get("manifest_path") or args.manifest or ""
    payload_root = plan.get("payload_root") or args.payload_root or ""
    ui_mode = plan.get("ui_mode") or args.ui_mode or "cli"
    install_mode = str(plan.get("install_mode") or getattr(args, "install_mode", "") or "").strip().lower()
    store_root_override = str(plan.get("store_root") or getattr(args, "store_root", "") or "").strip()

    if not install_root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "install_root is required", {})
        return EXIT_REFUSED, {"message": "missing install_root", "refusal": refusal}

    install_root = normalize_path(install_root)
    data_root = normalize_path(data_root) if data_root else normalize_path(os.path.join(install_root, "data"))
    if install_mode not in ("linked", "portable"):
        install_mode = "linked" if store_root_override else "portable"
    effective_store_root = install_root if install_mode == "portable" else normalize_path(store_root_override or os.path.join(os.path.dirname(install_root), "dominium.store"))

    if os.path.exists(install_root):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION",
                                  "install root already exists",
                                  {"install_root": os.path.basename(install_root)})
        txn = SetupTransaction(install_root, "setup.install", plan.get("transaction_id", ""), deterministic)
        txn.log("PLAN", "pending", "install refused; root exists", refusal=refusal)
        txn.log("ROLLBACK", "refused", "install refused", refusal=refusal)
        return EXIT_REFUSED, {"message": "install root exists", "refusal": refusal}

    runtime_bin = os.path.join(payload_root, "runtime", "bin")
    launcher_bin = os.path.join(payload_root, "launcher", "bin")
    tools_dir = os.path.join(payload_root, "tools", "tools")
    packs_dir = os.path.join(payload_root, "packs")

    if not os.path.isdir(runtime_bin):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "runtime payload missing",
                                  {"payload_root": os.path.basename(payload_root)})
        return EXIT_REFUSED, {"message": "runtime payload missing", "refusal": refusal}

    tx_id = plan.get("transaction_id") or str(uuid.uuid4())
    stage_root = install_root + ".staging." + tx_id
    if os.path.exists(stage_root):
        shutil.rmtree(stage_root, ignore_errors=True)
    ensure_dir(stage_root)
    txn = SetupTransaction(stage_root, "setup.install", tx_id, deterministic)
    txn.log("PLAN", "pending", "plan accepted")
    txn.log("STAGE", "pending", "staging install payloads")

    try:
        created_data_root = False
        ensure_dir(os.path.join(stage_root, "bin"))
        ensure_dir(os.path.join(stage_root, "instances"))
        ensure_dir(os.path.join(stage_root, "saves"))
        ensure_dir(os.path.join(stage_root, "exports"))
        ensure_dir(os.path.join(stage_root, "store", "packs"))
        ensure_dir(os.path.join(stage_root, "store", "profiles"))
        ensure_dir(os.path.join(stage_root, "store", "blueprints"))
        ensure_dir(os.path.join(stage_root, "store", "locks"))
        ensure_dir(os.path.join(stage_root, "store", "migrations"))
        ensure_dir(os.path.join(stage_root, "store", "repro"))
        copy_tree(runtime_bin, os.path.join(stage_root, "bin"), overwrite=True)
        if os.path.isdir(launcher_bin):
            copy_tree(launcher_bin, os.path.join(stage_root, "bin"), overwrite=True)
        if os.path.isdir(tools_dir):
            copy_tree(tools_dir, os.path.join(stage_root, "tools"), overwrite=True)
        write_json(os.path.join(stage_root, "semantic_contract_registry.json"), _semantic_contract_registry_payload())

        if args.simulate_failure == "stage":
            raise RuntimeError("simulated stage failure")

        created_at = now_timestamp(deterministic)
        install_id = stable_install_id(
            {
                "install_version": str(args.versions.get("game_version", "0.0.0")).strip() or "0.0.0",
                "invocation_digest64": str(plan.get("invocation_digest64", "")).strip(),
                "mode": install_mode,
                "semantic_contract_registry_hash": _semantic_contract_registry_hash(),
            }
        )
        if not deterministic:
            install_id = stable_install_id(
                {
                    "install_version": str(args.versions.get("game_version", "0.0.0")).strip() or "0.0.0",
                    "nonce": str(uuid.uuid4()),
                    "mode": install_mode,
                    "semantic_contract_registry_hash": _semantic_contract_registry_hash(),
                }
            )

        manifest_payload = install_manifest_payload(
            install_id=install_id,
            install_root=install_root,
            store_root=effective_store_root,
            mode=install_mode,
            created_at=created_at,
            build_number=args.build_number or 0,
            versions=args.versions,
            stage_root=stage_root,
        )
        validation = validate_install_manifest(
            repo_root=REPO_ROOT_HINT,
            install_manifest_path=os.path.join(stage_root, DEFAULT_INSTALL_MANIFEST),
            manifest_payload=manifest_payload,
        )
        if validation.get("result") != "complete":
            raise RuntimeError(str(validation.get("refusal_code", "install_manifest_invalid")))
        write_json(os.path.join(stage_root, DEFAULT_INSTALL_MANIFEST), manifest_payload)
        write_json(os.path.join(stage_root, DEFAULT_SETUP_STATE),
                   setup_state_payload(install_id, manifest_path, data_root, ui_mode, created_at))

        compat_report = build_compat_report(
            context="install",
            install_id=install_id,
            instance_id=None,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=manifest_payload.get("supported_capabilities", []),
            missing_capabilities=[],
            compatibility_mode="full",
            refusal_codes=[],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=None,
        )
        write_json(os.path.join(stage_root, DEFAULT_COMPAT_REPORT), compat_report)

        if not os.path.isdir(data_root):
            ensure_dir(data_root)
            created_data_root = True

        if os.path.isdir(packs_dir):
            packs_target = os.path.join(data_root, "packs")
            if not os.path.isdir(packs_target):
                copy_tree(packs_dir, packs_target, overwrite=False)

        if args.simulate_failure == "commit":
            raise RuntimeError("simulated commit failure")

        try:
            os.replace(stage_root, install_root)
        except Exception:
            shutil.copytree(stage_root, install_root)
            shutil.rmtree(stage_root, ignore_errors=True)

        if install_mode == "portable":
            initialize_store_root(install_root)
        else:
            initialize_store_root(effective_store_root)

        txn = SetupTransaction(install_root, "setup.install", tx_id, deterministic)
        txn.log("COMMIT", "ok", "install committed")

        if created_data_root:
            ensure_dir(data_root)

        warnings = []
        if getattr(args, "network_notice", None):
            warnings.append(args.network_notice)
        details = {
            "details": {
                "install_root": install_root,
                "data_root": data_root,
                "install_mode": install_mode,
                "store_root": effective_store_root,
                "transaction_id": tx_id,
                "compat_report": os.path.join(install_root, DEFAULT_COMPAT_REPORT).replace("\\", "/"),
                "network_status": getattr(args, "network_status", ""),
                "network_notice": getattr(args, "network_notice", "") or "",
                "warnings": warnings,
            }
        }
        return EXIT_OK, details
    except Exception as exc:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", str(exc), {})
        try:
            txn.log("ROLLBACK", "refused", "install rollback", refusal=refusal)
        except Exception:
            pass
        shutil.rmtree(stage_root, ignore_errors=True)
        if created_data_root and os.path.isdir(data_root):
            shutil.rmtree(data_root, ignore_errors=True)
        return EXIT_REFUSED, {"message": "install failed", "refusal": refusal}


def repair_from_plan(plan: dict, args: argparse.Namespace, deterministic: bool) -> Tuple[int, dict]:
    install_root = plan.get("install_root") or args.install_root or ""
    data_root = plan.get("data_root") or args.data_root or ""
    payload_root = plan.get("payload_root") or args.payload_root or ""

    if not install_root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "install_root is required", {})
        return EXIT_REFUSED, {"message": "missing install_root", "refusal": refusal}

    install_root = normalize_path(install_root)
    if not os.path.isdir(install_root):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION", "install root missing",
                                  {"install_root": os.path.basename(install_root)})
        return EXIT_REFUSED, {"message": "install root missing", "refusal": refusal}

    manifest_path = os.path.join(install_root, DEFAULT_INSTALL_MANIFEST)
    if not os.path.isfile(manifest_path):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION", "install manifest missing",
                                  {"manifest": DEFAULT_INSTALL_MANIFEST})
        return EXIT_REFUSED, {"message": "install manifest missing", "refusal": refusal}

    runtime_bin = os.path.join(payload_root, "runtime", "bin")
    launcher_bin = os.path.join(payload_root, "launcher", "bin")
    tools_dir = os.path.join(payload_root, "tools", "tools")

    if not os.path.isdir(runtime_bin):
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT",
                                  "runtime payload missing",
                                  {"payload_root": os.path.basename(payload_root)})
        return EXIT_REFUSED, {"message": "runtime payload missing", "refusal": refusal}

    tx_id = plan.get("transaction_id") or str(uuid.uuid4())
    txn = SetupTransaction(install_root, "setup.repair", tx_id, deterministic)
    txn.log("PLAN", "pending", "plan accepted")
    txn.log("STAGE", "pending", "staging repair")

    setup_state = read_setup_state(install_root) or {}
    if not data_root:
        data_root = setup_state.get("data_root") or ""

    try:
        backup_index = os.path.join(install_root, ".dsu", "rollback_index.json")
        ensure_dir(os.path.dirname(backup_index))
        backup_path = backup_install_root(install_root, data_root, tx_id, deterministic)
        append_backup(backup_index, {
            "transaction_id": tx_id,
            "path": normalize_path(backup_path),
            "created_at": now_timestamp(deterministic),
        })

        sync_tree(runtime_bin, os.path.join(install_root, "bin"))
        if os.path.isdir(launcher_bin):
            sync_tree(launcher_bin, os.path.join(install_root, "bin"))
        if os.path.isdir(tools_dir):
            sync_tree(tools_dir, os.path.join(install_root, "tools"))

        validation = validate_install_manifest(
            repo_root=REPO_ROOT_HINT,
            install_manifest_path=manifest_path,
        )
        if validation.get("result") != "complete":
            raise RuntimeError(str(validation.get("refusal_code", "install_manifest_invalid")))

        if args.simulate_failure == "commit":
            raise RuntimeError("simulated commit failure")

        compat_report = build_compat_report(
            context="repair",
            install_id=setup_state.get("install_id"),
            instance_id=None,
            runtime_id=None,
            capability_baseline=args.capability_baseline,
            required_capabilities=[],
            provided_capabilities=[],
            missing_capabilities=[],
            compatibility_mode="full",
            refusal_codes=[],
            mitigation_hints=[],
            deterministic=deterministic,
            refusal=None,
        )
        write_json(os.path.join(install_root, DEFAULT_COMPAT_REPORT), compat_report)

        txn.log("COMMIT", "ok", "repair committed")
        return EXIT_OK, {
            "details": {
                "install_root": install_root,
                "transaction_id": tx_id,
                "backup_path": normalize_path(backup_path),
            }
        }
    except Exception as exc:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", str(exc), {})
        txn.log("ROLLBACK", "refused", "repair rollback", refusal=refusal)
        backup_index = os.path.join(install_root, ".dsu", "rollback_index.json")
        backup_entry = latest_backup(backup_index)
        if backup_entry:
            backup_path = backup_entry.get("path")
            if backup_path and os.path.isdir(backup_path):
                shutil.rmtree(install_root, ignore_errors=True)
                shutil.copytree(backup_path, install_root)
        return EXIT_REFUSED, {"message": "repair failed", "refusal": refusal}


def uninstall_from_plan(plan: dict, args: argparse.Namespace, deterministic: bool) -> Tuple[int, dict]:
    install_root = plan.get("install_root") or args.install_root or ""
    data_root = plan.get("data_root") or args.data_root or ""

    if not install_root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "install_root is required", {})
        return EXIT_REFUSED, {"message": "missing install_root", "refusal": refusal}

    install_root = normalize_path(install_root)
    if not os.path.isdir(install_root):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION", "install root missing",
                                  {"install_root": os.path.basename(install_root)})
        return EXIT_REFUSED, {"message": "install root missing", "refusal": refusal}

    setup_state = read_setup_state(install_root) or {}
    if not data_root:
        data_root = setup_state.get("data_root") or ""
    data_root = normalize_path(data_root) if data_root else ""

    tx_id = plan.get("transaction_id") or str(uuid.uuid4())
    txn = SetupTransaction(install_root, "setup.uninstall", tx_id, deterministic)
    txn.log("PLAN", "pending", "plan accepted")
    txn.log("STAGE", "pending", "staging uninstall")

    preserved_data_root = data_root
    if data_root and not args.remove_data:
        if data_root.startswith(install_root):
            preserved_data_root = install_root + ".data"
            if os.path.exists(preserved_data_root):
                preserved_data_root = install_root + ".data_" + tx_id[:8]
            shutil.move(data_root, preserved_data_root)

    if args.simulate_failure == "commit":
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "simulated commit failure", {})
        txn.log("ROLLBACK", "refused", "uninstall rollback", refusal=refusal)
        return EXIT_REFUSED, {"message": "uninstall failed", "refusal": refusal}

    shutil.rmtree(install_root, ignore_errors=True)

    if args.remove_data and preserved_data_root:
        shutil.rmtree(preserved_data_root, ignore_errors=True)

    return EXIT_OK, {
        "details": {
            "install_root": install_root,
            "data_root": preserved_data_root if not args.remove_data else "",
            "transaction_id": tx_id,
        }
    }


def rollback_from_plan(plan: dict, args: argparse.Namespace, deterministic: bool) -> Tuple[int, dict]:
    install_root = plan.get("install_root") or args.install_root or ""
    if not install_root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "install_root is required", {})
        return EXIT_REFUSED, {"message": "missing install_root", "refusal": refusal}
    install_root = normalize_path(install_root)
    if not os.path.isdir(install_root):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION", "install root missing",
                                  {"install_root": os.path.basename(install_root)})
        return EXIT_REFUSED, {"message": "install root missing", "refusal": refusal}

    backup_index = os.path.join(install_root, ".dsu", "rollback_index.json")
    transaction_entry = select_rollback_transaction(
        transaction_log_path(install_root),
        to_release_id=str(getattr(args, "to", "") or "").strip(),
    )
    entry = None
    backup_target = str(transaction_entry.get("backup_path", "")).strip()
    if backup_target:
        entry = {"path": backup_target, "transaction_id": str(transaction_entry.get("transaction_id", "")).strip()}
    if entry is None:
        entry = latest_backup(backup_index)
    if not entry:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "no rollback backup available", {})
        return EXIT_REFUSED, {"message": "no rollback available", "refusal": refusal}

    backup_path = entry.get("path")
    if not backup_path or not os.path.isdir(backup_path):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION", "rollback backup missing", {})
        return EXIT_REFUSED, {"message": "rollback backup missing", "refusal": refusal}

    tx_id = plan.get("transaction_id") or str(uuid.uuid4())
    txn = SetupTransaction(install_root, "setup.rollback", tx_id, deterministic)
    txn.log("PLAN", "pending", "plan accepted")
    txn.log("STAGE", "pending", "staging rollback")

    staging = install_root + ".rollback.current." + tx_id[:8]
    try:
        os.replace(install_root, staging)
    except Exception:
        shutil.copytree(install_root, staging)
        shutil.rmtree(install_root, ignore_errors=True)

    try:
        os.replace(backup_path, install_root)
    except Exception:
        shutil.copytree(backup_path, install_root)
        shutil.rmtree(backup_path, ignore_errors=True)

    shutil.rmtree(staging, ignore_errors=True)
    append_install_transaction(
        transaction_log_path(install_root),
        {
            "transaction_id": tx_id,
            "action": "update.rollback",
            "from_release_id": str(dict(plan or {}).get("from_release_id", "")).strip(),
            "to_release_id": str(getattr(args, "to", "") or "").strip(),
            "backup_path": normalize_path(backup_path),
            "status": "complete",
            "install_profile_id": str(dict(plan or {}).get("install_profile_id", "")).strip(),
            "resolution_policy_id": str(dict(transaction_entry or {}).get("resolution_policy_id", "")).strip() or DEFAULT_RELEASE_RESOLUTION_POLICY_ID,
            "install_plan_hash": str(dict(transaction_entry or {}).get("install_plan_hash", "")).strip(),
            "prior_component_set_hash": str(dict(transaction_entry or {}).get("prior_component_set_hash", "")).strip(),
        },
    )
    txn.log("COMMIT", "ok", "rollback committed")
    return EXIT_OK, {
        "details": {
            "install_root": install_root,
            "transaction_id": tx_id,
            "restored_from": normalize_path(backup_path),
        }
    }


def handle_apply(args: argparse.Namespace, deterministic: bool) -> int:
    plan_path = getattr(args, "plan", None)
    if plan_path:
        plan = load_json(plan_path)
    else:
        if not getattr(args, "manifest", None):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "manifest is required", {})
            output_refusal("missing manifest", refusal, args.format)
            return EXIT_REFUSED
        invocation = build_invocation(args, deterministic)
        tx_id = args.transaction_id or str(uuid.uuid5(uuid.NAMESPACE_URL, digest64(invocation)))
        artifact_root = derive_artifact_root(args.manifest, getattr(args, "artifact_root", None))
        payload_root = payload_root_from_artifact(artifact_root, getattr(args, "payload_root", None))
        plan = make_plan(invocation, args.manifest, payload_root, deterministic, tx_id)

    if getattr(args, "dry_run", False):
        output_ok("dry-run apply ok", {"details": {"operation": plan.get("op")}}, args.format)
        return EXIT_OK

    op = plan.get("op") or getattr(args, "op", "")
    if op == "install":
        code, payload = install_from_plan(plan, args, deterministic)
    elif op == "repair":
        code, payload = repair_from_plan(plan, args, deterministic)
    elif op == "uninstall":
        code, payload = uninstall_from_plan(plan, args, deterministic)
    elif op == "rollback":
        code, payload = rollback_from_plan(plan, args, deterministic)
    else:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "unknown operation", {"op": op or ""})
        output_refusal("unknown operation", refusal, args.format)
        return EXIT_REFUSED

    if code == EXIT_OK:
        output_ok("%s ok" % op, payload, args.format)
    else:
        output_refusal("%s failed" % op, payload.get("refusal", {}), args.format)
    return code


def handle_detect(args: argparse.Namespace, deterministic: bool) -> int:
    if not args.install_root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "install_root is required", {})
        output_refusal("missing install_root", refusal, args.format)
        return EXIT_REFUSED
    install_root = normalize_path(args.install_root)
    manifest_path = os.path.join(install_root, DEFAULT_INSTALL_MANIFEST)
    ok = os.path.isfile(manifest_path)
    output_ok("detect ok", {
        "details": {
            "install_root": install_root,
            "install_manifest": manifest_path.replace("\\", "/"),
            "install_present": True if ok else False,
        }
    }, args.format)
    return EXIT_OK


def handle_manifest_validate(args: argparse.Namespace, deterministic: bool) -> int:
    if not args.in_path:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "manifest path is required", {})
        output_refusal("missing manifest", refusal, args.format)
        return EXIT_REFUSED
    if not os.path.isfile(args.in_path):
        refusal = refusal_payload(5, "REFUSE_INTEGRITY_VIOLATION", "manifest file missing", {})
        output_refusal("manifest missing", refusal, args.format)
        return EXIT_REFUSED
    data = open(args.in_path, "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    digest64_val = base64.b64encode(hashlib.sha256(data).digest()).decode("ascii")
    details = {
        "content_digest32": sha[:32],
        "content_digest64": digest64_val,
    }
    output_ok("manifest ok", {"details": details}, args.format)
    return EXIT_OK


def handle_install_registry(args: argparse.Namespace) -> int:
    registry_path = normalize_path(getattr(args, "registry_path", "") or default_install_registry_path(REPO_ROOT_HINT))
    cmd = str(getattr(args, "registry_cmd", "") or "").strip().lower()
    target = str(getattr(args, "registry_target", "") or "").strip()
    install_id = str(getattr(args, "install_id", "") or "").strip() or target
    install_profile_id = str(getattr(args, "install_profile_id", "") or getattr(args, "profile", "") or "").strip() or DEFAULT_INSTALL_PROFILE_ID
    requested_resolution_policy_id = str(getattr(args, "resolution_policy_id", "") or getattr(args, "policy", "") or "").strip()
    resolution_policy = _load_release_resolution_policy_for_root(
        str(getattr(args, "install_root", "") or "").strip() or REPO_ROOT_HINT,
        requested_resolution_policy_id or DEFAULT_RELEASE_RESOLUTION_POLICY_ID,
    )
    if requested_resolution_policy_id and not resolution_policy:
        refusal = refusal_payload(
            1,
            "REFUSE_INVALID_INTENT",
            "unknown install resolution policy",
            {"policy": requested_resolution_policy_id},
        )
        output_refusal("unknown install policy", refusal, args.format)
        return EXIT_REFUSED
    resolution_policy_id = (
        str(canonicalize_release_resolution_policy(resolution_policy).get("policy_id", "")).strip()
        or DEFAULT_RELEASE_RESOLUTION_POLICY_ID
    )

    def _plan_targets() -> dict:
        platform_value = str(getattr(args, "platform", "") or "").strip()
        mapped = platform_targets_for_tag(platform_value, repo_root=_plan_source_root())
        if any(str(value).strip() for value in mapped.values()):
            return {
                "target_id": str(mapped.get("target_id", "")).strip(),
                "platform_id": str(mapped.get("platform_id", "")).strip(),
                "os_id": str(mapped.get("os_id", "")).strip(),
                "arch_id": str(mapped.get("arch_id", "")).strip(),
                "abi_id": str(mapped.get("abi_id", "")).strip(),
                "tier": int(mapped.get("tier", 0) or 0),
                "platform_tag": platform_value,
            }
        return {
            "target_id": "",
            "platform_id": platform_value,
            "os_id": "",
            "arch_id": str(getattr(args, "arch", "") or "").strip(),
            "abi_id": str(getattr(args, "abi", "") or "").strip(),
            "tier": 0,
            "platform_tag": platform_value,
        }

    def _plan_source_root() -> str:
        if str(getattr(args, "install_root", "") or "").strip():
            return normalize_path(str(getattr(args, "install_root", "")).strip())
        return REPO_ROOT_HINT

    def _build_component_plan() -> dict:
        targets = _plan_targets()
        plan_result = build_default_component_install_plan(
            _plan_source_root(),
            install_profile_id=install_profile_id,
            target_platform=str(targets.get("platform_id", "")).strip(),
            target_arch=str(targets.get("arch_id", "")).strip(),
            target_abi=str(targets.get("abi_id", "")).strip(),
        )
        install_plan = dict(plan_result.get("install_plan") or {})
        if install_plan:
            extensions = dict(install_plan.get("extensions") or {})
            extensions["resolution_policy_id"] = resolution_policy_id
            install_plan["extensions"] = extensions
            plan_result = dict(plan_result)
            plan_result["install_plan"] = install_plan
            plan_result["resolution_policy"] = dict(resolution_policy)
        return plan_result

    def _plan_storage_root() -> str:
        explicit_store_root = str(getattr(args, "store_root", "") or "").strip()
        if explicit_store_root:
            return normalize_path(explicit_store_root)
        explicit_install_root = str(getattr(args, "install_root", "") or "").strip()
        if explicit_install_root:
            return normalize_path(os.path.join(explicit_install_root, "store"))
        return normalize_path(os.path.join(REPO_ROOT_HINT, "store"))

    if cmd == "status":
        raw_args: List[str] = []
        if getattr(args, "install_root", ""):
            raw_args.extend(["--install-root", str(getattr(args, "install_root", "")).strip()])
        if install_id:
            raw_args.extend(["--install-id", install_id])
        if getattr(args, "registry_path", ""):
            raw_args.extend(["--install-registry-path", str(getattr(args, "registry_path", "")).strip()])
        result = discover_install(
            raw_args=raw_args,
            executable_path=os.path.abspath(sys.argv[0]),
            cwd=os.getcwd(),
            env=os.environ,
        )
        discovery_result = str(result.get("result", "")).strip() or "refused"
        refusal_code = str(result.get("refusal_code", "")).strip()
        reason = ""
        for row in list(result.get("errors") or []):
            row_map = dict(row or {})
            if str(row_map.get("code", "")).strip() == refusal_code and str(row_map.get("message", "")).strip():
                reason = str(row_map.get("message", "")).strip()
                break
        component_plan = {}
        resolved_root = str(result.get("resolved_install_root_path", "")).strip()
        if resolved_root:
            release_manifest_path = os.path.join(resolved_root, "manifests", "release_manifest.json")
            platform_tag = ""
            if os.path.isfile(release_manifest_path):
                try:
                    platform_tag = str(load_release_manifest(release_manifest_path).get("platform_tag", "")).strip()
                except ValueError:
                    platform_tag = ""
            targets = platform_targets_for_tag(platform_tag, repo_root=resolved_root)
            plan_result = build_default_component_install_plan(
                resolved_root,
                install_profile_id=install_profile_id,
                target_platform=str(targets.get("platform_id", "")).strip(),
                target_arch=str(targets.get("arch_id", "")).strip(),
                target_abi=str(targets.get("abi_id", "")).strip(),
            )
            install_plan = dict(plan_result.get("install_plan") or {})
            component_plan = {
                "result": str(plan_result.get("result", "")).strip(),
                "graph_id": str(plan_result.get("graph_id", "")).strip(),
                "target_id": str(targets.get("target_id", "")).strip(),
                "target_platform": str(install_plan.get("target_platform", "")).strip(),
                "target_arch": str(install_plan.get("target_arch", "")).strip(),
                "target_abi": str(dict(install_plan.get("extensions") or {}).get("target_abi", "")).strip(),
                "target_tier": int(targets.get("tier", 0) or 0),
                "selected_component_count": int(len(list(install_plan.get("selected_components") or []))),
                "install_plan_fingerprint": str(install_plan.get("deterministic_fingerprint", "")).strip(),
            }
        write_output(
            {
                "result": discovery_result,
                "message": "setup install discovery status",
                "refusal_code": refusal_code,
                "reason": reason,
                "summary": {
                    "mode": str(result.get("mode", "")).strip(),
                    "resolution_source": str(result.get("resolution_source", "")).strip(),
                    "resolved_install_root": str(result.get("resolved_install_root_path", "")).strip(),
                    "resolved_install_id": str(result.get("resolved_install_id", "")).strip(),
                },
                "remediation_hint": (
                    ""
                    if discovery_result == "complete"
                    else "Use `setup install register <path>` for installed mode, or place `install.manifest.json` beside the product binaries for portable mode."
                ),
                "details": {
                    "product_id": "setup",
                    "default_registry_path": registry_path,
                    "install_discovery": result,
                    "install_profile_id": install_profile_id,
                    "resolution_policy_id": resolution_policy_id,
                    "component_install_plan": component_plan,
                },
            },
            args.format,
        )
        _emit_setup_event(
            "lib",
            "lib.install.status",
            severity="info" if discovery_result == "complete" else "warn",
            params={
                "result": discovery_result,
                "install_profile_id": install_profile_id,
                "resolved_install_root": str(result.get("resolved_install_root_path", "")).strip(),
                "resolution_source": str(result.get("resolution_source", "")).strip(),
            },
        )
        return EXIT_OK if str(result.get("result", "")).strip() == "complete" else EXIT_REFUSED

    if cmd == "plan":
        plan_result = _build_component_plan()
        install_plan = dict(plan_result.get("install_plan") or {})
        payload = {
            "result": str(plan_result.get("result", "")).strip() or "refused",
            "message": "setup install plan",
            "install_profile_id": install_profile_id,
            "resolution_policy_id": resolution_policy_id,
            "source_root": _plan_source_root(),
            "target": _plan_targets(),
            "graph_id": str(plan_result.get("graph_id", "")).strip(),
            "release_id": str(plan_result.get("release_id", "")).strip(),
            "install_plan": install_plan,
            "errors": list(plan_result.get("errors") or []),
        }
        out_path = str(getattr(args, "out_plan", "") or getattr(args, "out", "") or "").strip()
        if out_path:
            write_json(out_path, payload)
            payload["plan_path"] = normalize_path(out_path)
        write_output(payload, args.format)
        _emit_setup_event(
            "lib",
            "lib.install.plan",
            severity="info" if payload["result"] == "complete" else "warn",
            params={
                "result": payload["result"],
                "install_profile_id": install_profile_id,
                "resolution_policy_id": resolution_policy_id,
                "plan_id": str(install_plan.get("plan_id", "")).strip(),
                "graph_id": str(payload.get("graph_id", "")).strip(),
                "plan_path": str(payload.get("plan_path", "")).strip(),
            },
        )
        return EXIT_OK if payload["result"] == "complete" else EXIT_REFUSED

    if cmd == "apply":
        plan_token = str(getattr(args, "plan", "") or "").strip()
        payload = {}
        if plan_token:
            if os.path.isfile(plan_token):
                payload = load_json(plan_token)
            else:
                candidate = os.path.join(_plan_storage_root(), "plans", "{}.json".format(plan_token))
                if os.path.isfile(candidate):
                    payload = load_json(candidate)
        if not payload:
            plan_result = _build_component_plan()
            payload = {
                "result": str(plan_result.get("result", "")).strip() or "refused",
                "install_profile_id": install_profile_id,
                "graph_id": str(plan_result.get("graph_id", "")).strip(),
                "release_id": str(plan_result.get("release_id", "")).strip(),
                "install_plan": dict(plan_result.get("install_plan") or {}),
                "errors": list(plan_result.get("errors") or []),
            }
        if str(payload.get("result", "")).strip() != "complete":
            write_output(
                {
                    "result": "refused",
                    "message": "setup install apply refused",
                    "install_profile_id": install_profile_id,
                    "resolution_policy_id": resolution_policy_id,
                    "errors": list(payload.get("errors") or []),
                    "install_plan": dict(payload.get("install_plan") or {}),
                },
                args.format,
            )
            return EXIT_REFUSED
        install_plan = dict(payload.get("install_plan") or {})
        store_root = _plan_storage_root()
        plan_id = str(install_plan.get("plan_id", "")).strip() or "install_plan.unnamed"
        plan_path = os.path.join(store_root, "plans", "{}.json".format(plan_id))
        write_json(plan_path, payload)
        write_output(
            {
                "result": "complete",
                "message": "setup install apply completed",
                "install_profile_id": str(install_plan.get("install_profile_id", "")).strip() or install_profile_id,
                "resolution_policy_id": resolution_policy_id,
                "store_root": store_root,
                "plan_path": normalize_path(plan_path),
                "selected_component_ids": list(install_plan.get("selected_components") or []),
                "disabled_optional_components": list(dict(install_plan.get("extensions") or {}).get("disabled_optional_components") or []),
                "mode": "mock_store_apply",
            },
            args.format,
        )
        _emit_setup_event(
            "lib",
            "lib.install.apply",
            params={
                "install_profile_id": str(install_plan.get("install_profile_id", "")).strip() or install_profile_id,
                "resolution_policy_id": resolution_policy_id,
                "plan_id": plan_id,
                "store_root": store_root,
                "selected_component_count": int(len(list(install_plan.get("selected_components") or []))),
            },
        )
        return EXIT_OK

    if cmd == "list":
        registry = load_install_registry(registry_path)
        output_ok(
            "install registry listed",
            {
                "details": {
                    "registry_path": registry_path,
                    "installs": list((registry.get("record") or {}).get("installs") or []),
                }
            },
            args.format,
        )
        return EXIT_OK

    if cmd in {"add", "register"}:
        if not target:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "install path is required", {})
            output_refusal("missing install path", refusal, args.format)
            return EXIT_REFUSED
        manifest_path = target
        if os.path.isdir(target):
            manifest_path = os.path.join(target, DEFAULT_INSTALL_MANIFEST)
        result = registry_add_install(
            repo_root=REPO_ROOT_HINT,
            registry_path=registry_path,
            install_manifest_path=manifest_path,
        )
        if result.get("result") != "complete":
            refusal = refusal_payload(5, str(result.get("refusal_code", REFUSAL_INSTALL_HASH_MISMATCH)), "install registry add failed", {})
            output_refusal("install registry add failed", refusal, args.format)
            return EXIT_REFUSED
        output_ok(
            "install registry add ok",
            {
                "details": {
                    "registry_path": registry_path,
                    "entry": result.get("registry_entry") or {},
                    "created": bool(result.get("created", False)),
                }
            },
            args.format,
        )
        return EXIT_OK

    if cmd in {"remove", "unregister"}:
        if not install_id:
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "install_id is required", {})
            output_refusal("missing install_id", refusal, args.format)
            return EXIT_REFUSED
        result = registry_remove_install(registry_path=registry_path, install_id=install_id)
        output_ok(
            "install registry remove ok",
            {
                "details": {
                    "registry_path": registry_path,
                    "install_id": install_id,
                    "removed": bool(result.get("removed", False)),
                }
            },
            args.format,
        )
        return EXIT_OK

    if cmd == "verify":
        result = verify_install_registry(repo_root=REPO_ROOT_HINT, registry_path=registry_path)
        if result.get("result") != "complete":
            refusal = refusal_payload(5, "REFUSE_INSTALL_REGISTRY_VERIFY_FAILED", "install registry verify failed", {})
            write_output({"result": "refused", "message": "install registry verify failed", "refusal": refusal, "details": result}, args.format)
            return EXIT_REFUSED
        output_ok(
            "install registry verify ok",
            {"details": result},
            args.format,
        )
        return EXIT_OK

    refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "unknown install registry command", {"cmd": cmd})
    output_refusal("unknown install registry command", refusal, args.format)
    return EXIT_REFUSED


def handle_update(args: argparse.Namespace, deterministic: bool) -> int:
    cmd = str(getattr(args, "update_cmd", "") or "").strip().lower()
    if not cmd:
        refusal = _update_refusal(
            "refusal.update.invalid_intent",
            "update command is required",
            ["Run `setup update check --channel mock` to inspect the local release index."],
        )
        output_refusal("missing update command", refusal, args.format)
        return EXIT_REFUSED

    discovery = _discover_install_context(args)
    if str(discovery.get("result", "")).strip() != "complete":
        refusal = _update_refusal(
            str(discovery.get("refusal_code", "")).strip() or "refusal.install.not_found",
            "install discovery failed",
            [
                "Run `setup install status` to inspect install discovery.",
                "Use `setup install register <path>` for installed mode or place `install.manifest.json` beside the product binaries for portable mode.",
            ],
        )
        write_output({"result": "refused", "message": "setup update refused", "refusal": refusal, "details": {"install_discovery": discovery}}, args.format)
        return EXIT_REFUSED

    install_root = normalize_path(str(discovery.get("resolved_install_root_path", "")).strip())
    install_manifest_path = os.path.join(install_root, DEFAULT_INSTALL_MANIFEST)
    current_validation = validate_install_manifest(repo_root=REPO_ROOT_HINT, install_manifest_path=install_manifest_path)
    if str(current_validation.get("result", "")).strip() != "complete":
        refusal = _update_refusal(
            str(current_validation.get("refusal_code", "")).strip() or "refusal.update.current_install_invalid",
            "current install manifest is invalid",
            ["Run `setup verify --root {}` to inspect the current install.".format(install_root)],
        )
        write_output({"result": "refused", "message": "setup update refused", "refusal": refusal, "details": {"validation": current_validation}}, args.format)
        return EXIT_REFUSED

    current_install_manifest = dict(current_validation.get("install_manifest") or {})
    effective_policy_id, effective_policy_row = _load_effective_trust_policy(
        install_root=install_root,
        install_manifest=current_install_manifest,
        requested_trust_policy_id=str(getattr(args, "trust_policy_id", "") or "").strip(),
        mod_policy_id=str(current_install_manifest.get("default_mod_policy_id", "")).strip(),
    )
    trust_roots = load_trust_root_registry(repo_root=REPO_ROOT_HINT, install_root=install_root)
    planned_payload = {}
    if cmd == "apply":
        plan_token = str(getattr(args, "plan", "") or "").strip()
        if plan_token and os.path.isfile(plan_token):
            planned_payload = load_json(plan_token)
    install_profile_id = (
        str(getattr(args, "install_profile_id", "") or getattr(args, "profile", "") or "").strip()
        or str(planned_payload.get("install_profile_id", "")).strip()
        or str(dict(current_install_manifest.get("extensions") or {}).get("official.install_profile_id", "")).strip()
        or DEFAULT_INSTALL_PROFILE_ID
    )
    requested_resolution_policy_id = (
        str(getattr(args, "resolution_policy_id", "") or getattr(args, "policy", "") or "").strip()
        or str(dict(planned_payload.get("update_plan") or {}).get("resolution_policy_id", "")).strip()
        or str(planned_payload.get("resolution_policy_id", "")).strip()
        or str(dict(current_install_manifest.get("extensions") or {}).get("official.install_resolution_policy_id", "")).strip()
        or DEFAULT_RELEASE_RESOLUTION_POLICY_ID
    )
    release_index_path = infer_release_index_path(
        install_root,
        str(getattr(args, "release_index", "") or "").strip() or str(planned_payload.get("release_index_path", "")).strip(),
    )
    if not os.path.isfile(release_index_path):
        refusal = _update_refusal(
            "refusal.update.index_missing",
            "release index is missing",
            [
                "Place `manifests/release_index.json` inside the target bundle, or pass `--release-index <path>`.",
                "Rebuild the distribution bundle if the release index was not generated.",
            ],
        )
        write_output({"result": "refused", "message": "setup update refused", "refusal": refusal, "details": {"release_index_path": release_index_path}}, args.format)
        return EXIT_REFUSED

    release_index = load_release_index(release_index_path)
    install_profile = _load_install_profile_for_root(install_root, install_profile_id)
    resolution_policy = _load_release_resolution_policy_for_root(install_root, requested_resolution_policy_id)
    if requested_resolution_policy_id and not resolution_policy:
        refusal = _update_refusal(
            "refusal.update.invalid_policy",
            "unknown release resolution policy",
            ["Use `setup update --policy exact_suite|latest_compatible|lab`."],
        )
        write_output({"result": "refused", "message": "setup update refused", "refusal": refusal}, args.format)
        return EXIT_REFUSED
    resolution_policy_id = (
        str(canonicalize_release_resolution_policy(resolution_policy).get("policy_id", "")).strip()
        or DEFAULT_RELEASE_RESOLUTION_POLICY_ID
    )
    target_ids = platform_targets_for_tag(
        str(getattr(args, "platform", "") or "").strip(),
        repo_root=install_root,
    )
    resolution = resolve_update_plan(
        current_install_manifest,
        release_index,
        install_profile_id=install_profile_id,
        install_profile=install_profile,
        resolution_policy_id=resolution_policy_id,
        resolution_policy=resolution_policy,
        target_platform=str(target_ids.get("platform_id", "")).strip(),
        target_arch=str(target_ids.get("arch_id", "")).strip(),
        target_abi=str(target_ids.get("abi_id", "")).strip(),
        component_graph=dict(dict(release_index.get("extensions") or {}).get("component_graph") or {}),
        trust_policy=effective_policy_row,
        trust_policy_id=effective_policy_id,
        trust_roots=list(trust_roots.get("trust_roots") or []),
        install_root=install_root,
        release_index_path=release_index_path,
    )
    update_plan = dict(resolution.get("update_plan") or {})
    update_required = bool(dict(update_plan.get("extensions") or {}).get("update_required"))

    if cmd == "check":
        payload = {
            "result": str(resolution.get("result", "")).strip() or "refused",
            "message": "setup update check",
            "install_root": install_root,
            "release_index_path": release_index_path,
            "install_profile_id": install_profile_id,
            "resolution_policy_id": resolution_policy_id,
            "trust_policy_id": effective_policy_id,
            "current_release_id": str(update_plan.get("from_release_id", "")).strip(),
            "target_release_id": str(update_plan.get("to_release_id", "")).strip(),
            "update_required": update_required,
            "components_to_add": list(update_plan.get("components_to_add") or []),
            "components_to_remove": list(update_plan.get("components_to_remove") or []),
            "components_to_upgrade": list(update_plan.get("components_to_upgrade") or []),
            "selected_yanked_component_ids": list(dict(update_plan.get("extensions") or {}).get("selected_yanked_component_ids") or []),
            "warnings": list(resolution.get("warnings") or []),
            "errors": list(resolution.get("errors") or []),
        }
        write_output(payload, args.format)
        _emit_setup_event(
            "update",
            "update.check.result",
            severity="info" if payload["result"] == "complete" else "warn",
            params={
                "result": payload["result"],
                "install_profile_id": install_profile_id,
                "resolution_policy_id": resolution_policy_id,
                "install_root": install_root,
                "target_release_id": str(payload.get("target_release_id", "")).strip(),
                "update_required": bool(update_required),
            },
        )
        return EXIT_OK if payload["result"] == "complete" else EXIT_REFUSED

    if cmd == "plan":
        payload = {
            "result": str(resolution.get("result", "")).strip() or "refused",
            "message": "setup update plan",
            "install_root": install_root,
            "release_index_path": release_index_path,
            "install_profile_id": install_profile_id,
            "resolution_policy_id": resolution_policy_id,
            "trust_policy_id": effective_policy_id,
            "update_plan": update_plan,
            "warnings": list(resolution.get("warnings") or []),
            "errors": list(resolution.get("errors") or []),
        }
        out_path = str(getattr(args, "out_plan", "") or getattr(args, "out", "") or "").strip()
        if out_path:
            write_json(out_path, payload)
            payload["plan_path"] = normalize_path(out_path)
        write_output(payload, args.format)
        _emit_setup_event(
            "update",
            "update.plan.generated",
            severity="info" if payload["result"] == "complete" else "warn",
            params={
                "result": payload["result"],
                "install_profile_id": install_profile_id,
                "resolution_policy_id": resolution_policy_id,
                "install_root": install_root,
                "plan_id": str(update_plan.get("plan_id", "")).strip(),
                "plan_path": str(payload.get("plan_path", "")).strip(),
            },
        )
        return EXIT_OK if payload["result"] == "complete" else EXIT_REFUSED

    if cmd != "apply":
        refusal = _update_refusal(
            "refusal.update.invalid_intent",
            "unknown update command",
            ["Use `setup update check`, `setup update plan`, or `setup update apply`."],
        )
        output_refusal("unknown update command", refusal, args.format)
        return EXIT_REFUSED

    if str(resolution.get("result", "")).strip() != "complete":
        refusal = _update_refusal(
            str(resolution.get("refusal_code", "")).strip() or "refusal.update.resolution_failed",
            "update resolution failed",
            ["Run `setup update plan --channel {}` to inspect the refusal details.".format(str(getattr(args, "channel", "") or "mock").strip() or "mock")],
        )
        write_output(
            {
                "result": "refused",
                "message": "setup update apply refused",
                "refusal": refusal,
                "details": {
                    "update_plan": update_plan,
                    "warnings": list(resolution.get("warnings") or []),
                    "errors": list(resolution.get("errors") or []),
                },
            },
            args.format,
        )
        return EXIT_REFUSED

    if not update_required:
        write_output(
            {
                "result": "complete",
                "message": "setup update apply completed",
                "install_root": install_root,
                "install_profile_id": install_profile_id,
                "resolution_policy_id": resolution_policy_id,
                "update_required": False,
                "details": {"update_plan": update_plan},
            },
            args.format,
        )
        _emit_setup_event(
            "update",
            "update.apply.completed",
            params={
                "install_root": install_root,
                "install_profile_id": install_profile_id,
                "resolution_policy_id": resolution_policy_id,
                "plan_id": str(update_plan.get("plan_id", "")).strip(),
                "target_release_id": str(update_plan.get("to_release_id", "")).strip(),
                "update_required": False,
            },
        )
        return EXIT_OK

    source_root = resolve_release_artifact_root(release_index_path, resolution.get("platform_entry") or {})
    source_manifest_path = os.path.join(source_root, DEFAULT_RELEASE_MANIFEST_REL)
    verify_result = verify_release_manifest(
        source_root,
        source_manifest_path,
        repo_root=source_root,
        trust_policy_id=effective_policy_id,
    )
    if str(verify_result.get("result", "")).strip() != "complete":
        refusal = _update_refusal(
            "refusal.update.verification_failed",
            "target release manifest verification failed",
            ["Run `setup verify --release-manifest {}` against the target bundle.".format(source_manifest_path)],
        )
        write_output({"result": "refused", "message": "setup update apply refused", "refusal": refusal, "details": {"verification": verify_result}}, args.format)
        return EXIT_REFUSED

    tx_id = str(getattr(args, "transaction_id", "") or "").strip() or str(uuid.uuid4())
    data_root = str((read_setup_state(install_root) or {}).get("data_root", "")).strip()
    backup_index = os.path.join(install_root, ".dsu", "rollback_index.json")
    ensure_dir(os.path.dirname(backup_index))
    backup_path = backup_install_root(install_root, data_root, tx_id, deterministic)
    append_backup(
        backup_index,
        {
            "transaction_id": tx_id,
            "path": normalize_path(backup_path),
            "created_at": now_timestamp(deterministic),
        },
    )

    add_rows = list(update_plan.get("components_to_add") or [])
    remove_rows = list(update_plan.get("components_to_remove") or [])
    upgrade_rows = list(update_plan.get("components_to_upgrade") or [])
    try:
        _remove_managed_paths(install_root, remove_rows)
        _copy_managed_paths(source_root, install_root, add_rows + upgrade_rows)
        _copy_file = shutil.copyfile
        for rel_path in (
            "manifests/release_manifest.json",
            "manifests/release_index.json",
            "data/registries/semantic_contract_registry.json",
        ):
            src_path = os.path.join(source_root, rel_path.replace("/", os.sep))
            if not os.path.isfile(src_path):
                continue
            dst_path = os.path.join(install_root, rel_path.replace("/", os.sep))
            ensure_dir(os.path.dirname(dst_path))
            _copy_file(src_path, dst_path)
        source_install_manifest = load_json(os.path.join(source_root, DEFAULT_INSTALL_MANIFEST))
        merged_manifest = _merge_install_manifest_for_update(current_install_manifest, source_install_manifest, update_plan)
        merged_validation = validate_install_manifest(
            repo_root=REPO_ROOT_HINT,
            install_manifest_path=install_manifest_path,
            manifest_payload=merged_manifest,
        )
        if str(merged_validation.get("result", "")).strip() != "complete":
            raise RuntimeError(str(merged_validation.get("refusal_code", "refusal.update.install_manifest_invalid")))
        write_json(install_manifest_path, merged_manifest)
        write_json(os.path.join(install_root, "manifests", DEFAULT_INSTALL_MANIFEST), merged_manifest)
        append_install_transaction(
            transaction_log_path(install_root),
            {
                "transaction_id": tx_id,
                "action": "update.apply",
                "from_release_id": str(update_plan.get("from_release_id", "")).strip(),
                "to_release_id": str(update_plan.get("to_release_id", "")).strip(),
                "backup_path": normalize_path(backup_path),
                "install_profile_id": install_profile_id,
                "resolution_policy_id": resolution_policy_id,
                "install_plan_hash": str(update_plan.get("deterministic_fingerprint", "")).strip(),
                "prior_component_set_hash": str(dict(update_plan.get("extensions") or {}).get("prior_component_set_hash", "")).strip(),
                "selected_component_ids": list(dict(update_plan.get("extensions") or {}).get("target_selected_component_ids") or []),
                "extensions": {
                    "release_index_path": normalize_path(release_index_path),
                    "release_root": normalize_path(source_root),
                },
            },
        )
    except Exception as exc:
        if os.path.isdir(backup_path):
            shutil.rmtree(install_root, ignore_errors=True)
            shutil.copytree(backup_path, install_root)
        refusal = _update_refusal(
            "refusal.update.apply_failed",
            str(exc),
            ["Run `setup rollback --to {}` if the install no longer matches the expected release.".format(str(update_plan.get("from_release_id", "")).strip() or "<previous_release_id>")],
        )
        write_output({"result": "refused", "message": "setup update apply failed", "refusal": refusal, "details": {"update_plan": update_plan}}, args.format)
        return EXIT_REFUSED

    write_output(
        {
            "result": "complete",
            "message": "setup update apply completed",
            "install_root": install_root,
            "install_profile_id": install_profile_id,
            "resolution_policy_id": resolution_policy_id,
            "current_release_id": str(update_plan.get("from_release_id", "")).strip(),
            "target_release_id": str(update_plan.get("to_release_id", "")).strip(),
            "update_required": True,
            "plan_id": str(update_plan.get("plan_id", "")).strip(),
            "details": {
                "transaction_id": tx_id,
                "backup_path": normalize_path(backup_path),
                "verification_steps": list(update_plan.get("verification_steps") or []),
            },
        },
        args.format,
    )
    _emit_setup_event(
        "update",
        "update.apply.completed",
        params={
            "install_root": install_root,
            "install_profile_id": install_profile_id,
            "resolution_policy_id": resolution_policy_id,
            "plan_id": str(update_plan.get("plan_id", "")).strip(),
            "target_release_id": str(update_plan.get("to_release_id", "")).strip(),
            "update_required": True,
            "transaction_id": tx_id,
        },
    )
    return EXIT_OK


def handle_trust(args: argparse.Namespace) -> int:
    cmd = str(getattr(args, "trust_cmd", "") or "").strip().lower()
    requested_policy_id = str(getattr(args, "trust_policy_id", "") or "").strip()

    if cmd in {"list", "status"}:
        install_root = normalize_path(str(getattr(args, "install_root", "") or "").strip()) if str(getattr(args, "install_root", "") or "").strip() else ""
        if not install_root:
            discovery = _discover_install_context(args)
            if str(discovery.get("result", "")).strip() == "complete":
                install_root = normalize_path(str(discovery.get("resolved_install_root_path", "")).strip())
        install_manifest = {}
        if install_root:
            manifest_path = os.path.join(install_root, DEFAULT_INSTALL_MANIFEST)
            if os.path.isfile(manifest_path):
                validation = validate_install_manifest(repo_root=REPO_ROOT_HINT, install_manifest_path=manifest_path)
                install_manifest = dict(validation.get("install_manifest") or {})
        effective_policy_id, policy_row = _load_effective_trust_policy(
            install_root=install_root,
            install_manifest=install_manifest,
            requested_trust_policy_id=requested_policy_id,
        )
        root_registry = load_trust_root_registry(repo_root=REPO_ROOT_HINT, install_root=install_root)
        output_ok(
            "trust status",
            {
                "details": {
                    "install_root": install_root,
                    "trust_policy_id": effective_policy_id,
                    "trust_policy": policy_row,
                    "trust_roots": list(dict(root_registry.get("record") or {}).get("trust_roots") or []),
                    "status_kind": "status" if cmd == "status" else "list",
                }
            },
            args.format,
        )
        return EXIT_OK

    discovery = _discover_install_context(args)
    if str(discovery.get("result", "")).strip() != "complete":
        refusal = refusal_payload(
            5,
            str(discovery.get("refusal_code", "")).strip() or "refusal.install.not_found",
            "install discovery failed",
            {"remediation": "Use `setup install register <path>` or `--install-root <path>` to target an install."},
        )
        output_refusal("trust operation refused", refusal, args.format)
        return EXIT_REFUSED

    install_root = normalize_path(str(discovery.get("resolved_install_root_path", "")).strip())
    install_manifest_path = os.path.join(install_root, DEFAULT_INSTALL_MANIFEST)
    validation = validate_install_manifest(repo_root=REPO_ROOT_HINT, install_manifest_path=install_manifest_path)
    install_manifest = dict(validation.get("install_manifest") or {})

    if cmd == "import":
        bundle_path = normalize_path(str(getattr(args, "bundle", "") or "").strip())
        if not bundle_path or not os.path.isfile(bundle_path):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "trust root bundle is required", {})
            output_refusal("missing trust root bundle", refusal, args.format)
            return EXIT_REFUSED
        imported_rows = _load_imported_trust_root_rows(bundle_path)
        if not imported_rows:
            refusal = refusal_payload(5, "REFUSE_INVALID_INTENT", "trust root bundle did not contain any trust roots", {})
            output_refusal("trust import refused", refusal, args.format)
            return EXIT_REFUSED
        local_path = _trust_root_local_registry_path(install_root)
        existing_local = []
        if os.path.isfile(local_path):
            existing_local = list(dict(load_json(local_path).get("record") or {}).get("trust_roots") or [])
        merged = {}
        for row in existing_local + imported_rows:
            row_map = dict(row or {})
            signer_id = str(row_map.get("signer_id", "")).strip()
            if signer_id:
                merged[signer_id] = row_map
        write_trust_root_registry(local_path, [merged[key] for key in sorted(merged.keys())])
        output_ok(
            "trust roots imported",
            {
                "details": {
                    "install_root": install_root,
                    "local_registry_path": local_path.replace("\\", "/"),
                    "imported_signer_ids": sorted(merged.keys()),
                }
            },
            args.format,
        )
        return EXIT_OK

    if cmd == "policy":
        subcmd = str(getattr(args, "trust_policy_cmd", "") or "").strip().lower()
        if subcmd != "set":
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "unknown trust policy command", {"cmd": subcmd})
            output_refusal("unknown trust policy command", refusal, args.format)
            return EXIT_REFUSED
        effective_policy_id, policy_row = _load_effective_trust_policy(
            install_root=install_root,
            install_manifest=install_manifest,
            requested_trust_policy_id=requested_policy_id,
        )
        if not policy_row:
            refusal = refusal_payload(5, "REFUSE_INVALID_INTENT", "trust policy is not declared", {"trust_policy_id": effective_policy_id})
            output_refusal("trust policy set refused", refusal, args.format)
            return EXIT_REFUSED
        updated_manifest = normalize_install_manifest(dict(install_manifest or {}))
        updated_manifest.setdefault("extensions", {})
        updated_manifest["extensions"] = dict(updated_manifest.get("extensions") or {})
        updated_manifest["extensions"]["official.trust_policy_id"] = effective_policy_id
        updated_manifest["deterministic_fingerprint"] = install_deterministic_fingerprint(updated_manifest)
        manifest_validation = validate_install_manifest(
            repo_root=REPO_ROOT_HINT,
            install_manifest_path=install_manifest_path,
            manifest_payload=updated_manifest,
        )
        if str(manifest_validation.get("result", "")).strip() != "complete":
            refusal = refusal_payload(5, "REFUSE_INVALID_INTENT", "updated install manifest failed validation", {})
            output_refusal("trust policy set refused", refusal, args.format)
            return EXIT_REFUSED
        write_json(install_manifest_path, updated_manifest)
        mirrored_manifest_path = os.path.join(install_root, "manifests", DEFAULT_INSTALL_MANIFEST)
        if os.path.isdir(os.path.dirname(mirrored_manifest_path)):
            write_json(mirrored_manifest_path, updated_manifest)
        output_ok(
            "trust policy set",
            {
                "details": {
                    "install_root": install_root,
                    "trust_policy_id": effective_policy_id,
                }
            },
            args.format,
        )
        return EXIT_OK

    refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "unknown trust command", {"cmd": cmd})
    output_refusal("unknown trust command", refusal, args.format)
    return EXIT_REFUSED


def handle_governance(args: argparse.Namespace) -> int:
    cmd = str(getattr(args, "governance_cmd", "") or "").strip().lower()
    if cmd != "status":
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "unknown governance command", {"cmd": cmd})
        output_refusal("unknown governance command", refusal, args.format)
        return EXIT_REFUSED

    install_root = normalize_path(str(getattr(args, "install_root", "") or "").strip()) if str(getattr(args, "install_root", "") or "").strip() else ""
    if not install_root:
        discovery = _discover_install_context(args)
        if str(discovery.get("result", "")).strip() == "complete":
            install_root = normalize_path(str(discovery.get("resolved_install_root_path", "")).strip())

    payload = _governance_status_payload(install_root)
    output_ok(
        "governance status",
        {
            "details": payload,
        },
        args.format,
    )
    return EXIT_OK


def handle_instance(args: argparse.Namespace, deterministic: bool) -> int:
    cmd = str(getattr(args, "instance_cmd", "") or "").strip().lower()
    if not cmd:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "instance command is required", {})
        output_refusal("missing instance command", refusal, args.format)
        return EXIT_REFUSED

    extra: List[str] = []
    if deterministic:
        extra.append("--deterministic")

    if cmd == "create":
        extra += [
            "instances", "create",
            "--install-manifest", args.install_manifest,
            "--data-root", args.data_root,
            "--mode", args.mode,
            "--instance-kind", args.instance_kind,
            "--mod-policy-id", args.mod_policy_id,
            "--overlay-conflict-policy-id", args.overlay_conflict_policy_id,
            "--default-session-template-id", args.default_session_template_id,
            "--seed-policy", args.seed_policy,
            "--ui-mode-default", args.ui_mode_default,
            "--tick-budget-policy-id", args.tick_budget_policy_id,
            "--compute-profile-id", args.compute_profile_id,
        ]
        if args.instance_root:
            extra += ["--instance-root", args.instance_root]
        if args.instance_id:
            extra += ["--instance-id", args.instance_id]
        if args.store_root:
            extra += ["--store-root", args.store_root]
        if args.capability_lockfile:
            extra += ["--capability-lockfile", args.capability_lockfile]
        if args.sandbox_policy:
            extra += ["--sandbox-policy", args.sandbox_policy]
        if args.sandbox_policy_ref:
            extra += ["--sandbox-policy-ref", args.sandbox_policy_ref]
        if args.renderer_mode:
            extra += ["--renderer-mode", args.renderer_mode]
        if args.allow_read_only_fallback:
            extra += ["--allow-read-only-fallback"]
        if args.update_channel:
            extra += ["--update-channel", args.update_channel]
        if args.created_at:
            extra += ["--created-at", args.created_at]
        for profile in args.profile or []:
            extra += ["--active-profile", profile]
        for modpack in args.modpack or []:
            extra += ["--active-modpack", modpack]
        for pack_root in args.pack_root or []:
            extra += ["--pack-root", pack_root]
        for save_ref in args.save_ref or []:
            extra += ["--save-ref", save_ref]
        for product_build in args.required_product_build or []:
            extra += ["--required-product-build", product_build]
        for contract_range in args.required_contract_range or []:
            extra += ["--required-contract-range", contract_range]
        if args.last_opened_save_id:
            extra += ["--last-opened-save-id", args.last_opened_save_id]
        rc, payload, _stderr = run_script(resolve_ops_cli(), extra)
        write_output(payload, args.format)
        return rc

    if cmd == "clone":
        extra += [
            "instances", "clone",
            "--source-manifest", args.source_manifest,
            "--data-root", args.data_root,
        ]
        if args.instance_id:
            extra += ["--instance-id", args.instance_id]
        if args.store_root:
            extra += ["--store-root", args.store_root]
        if args.duplicate_embedded_artifacts:
            extra += ["--duplicate-embedded-artifacts"]
        if args.sandbox_policy:
            extra += ["--sandbox-policy", args.sandbox_policy]
        if args.created_at:
            extra += ["--created-at", args.created_at]
        rc, payload, _stderr = run_script(resolve_ops_cli(), extra)
        write_output(payload, args.format)
        return rc

    if cmd == "edit":
        extra += ["instances", "edit", "--instance-manifest", args.instance_manifest]
        if args.install_manifest:
            extra += ["--install-manifest", args.install_manifest]
        if args.sandbox_policy:
            extra += ["--sandbox-policy", args.sandbox_policy]
        if args.mode:
            extra += ["--mode", args.mode]
        if args.instance_kind:
            extra += ["--instance-kind", args.instance_kind]
        if args.store_root:
            extra += ["--store-root", args.store_root]
        if args.renderer_mode:
            extra += ["--renderer-mode", args.renderer_mode]
        if args.ui_mode_default:
            extra += ["--ui-mode-default", args.ui_mode_default]
        if args.allow_read_only_fallback:
            extra += ["--allow-read-only-fallback"]
        if args.deny_read_only_fallback:
            extra += ["--deny-read-only-fallback"]
        if args.tick_budget_policy_id:
            extra += ["--tick-budget-policy-id", args.tick_budget_policy_id]
        if args.compute_profile_id:
            extra += ["--compute-profile-id", args.compute_profile_id]
        if args.default_session_template_id:
            extra += ["--default-session-template-id", args.default_session_template_id]
        if args.seed_policy:
            extra += ["--seed-policy", args.seed_policy]
        if args.mod_policy_id:
            extra += ["--mod-policy-id", args.mod_policy_id]
        if args.overlay_conflict_policy_id:
            extra += ["--overlay-conflict-policy-id", args.overlay_conflict_policy_id]
        if args.last_opened_save_id is not None:
            extra += ["--last-opened-save-id", args.last_opened_save_id]
        for profile in args.profile or []:
            extra += ["--profile", profile]
        for modpack in args.modpack or []:
            extra += ["--modpack", modpack]
        for save_ref in args.save_ref or []:
            extra += ["--save-ref", save_ref]
        for product_build in args.required_product_build or []:
            extra += ["--required-product-build", product_build]
        for contract_range in args.required_contract_range or []:
            extra += ["--required-contract-range", contract_range]
        rc, payload, _stderr = run_script(resolve_ops_cli(), extra)
        write_output(payload, args.format)
        return rc

    if cmd == "export":
        instance_manifest_path = resolve_instance_manifest_path(
            getattr(args, "instance_id", ""),
            explicit_path=getattr(args, "instance_manifest", ""),
            store_root=getattr(args, "store_root", ""),
        )
        if not instance_manifest_path or not os.path.isfile(instance_manifest_path):
            refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "instance manifest is required for export", {})
            output_refusal("missing instance manifest", refusal, args.format)
            return EXIT_REFUSED
        payload = export_instance_bundle(
            repo_root=REPO_ROOT_HINT,
            instance_manifest_path=instance_manifest_path,
            out_path=normalize_path(args.out),
            export_mode=str(getattr(args, "mode", "") or "portable").strip() or "portable",
            bundle_id=str(getattr(args, "bundle_id", "") or "").strip(),
        )
        write_output(bridge_engine_payload(payload, "instance export ok"), args.format)
        return EXIT_OK if str(payload.get("result", "")).strip() == "complete" else EXIT_REFUSED

    if cmd == "import":
        import_engine = resolve_import_engine_module()
        payload = import_engine.import_instance_bundle(
            repo_root=REPO_ROOT_HINT,
            bundle_path=normalize_path(args.bundle),
            out_path=normalize_path(args.out) if args.out else "",
            import_mode=str(getattr(args, "import_mode", "") or "").strip(),
            store_root=normalize_path(args.store_root) if args.store_root else "",
            instance_id=str(getattr(args, "instance_id", "") or "").strip(),
        )
        write_output(bridge_engine_payload(payload, "instance import ok"), args.format)
        return EXIT_OK if str(payload.get("result", "")).strip() == "complete" else EXIT_REFUSED

    refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "unknown instance command", {"cmd": cmd})
    output_refusal("unknown instance command", refusal, args.format)
    return EXIT_REFUSED


def handle_save(args: argparse.Namespace) -> int:
    cmd = str(getattr(args, "save_cmd", "") or "").strip().lower()
    if cmd == "export":
        save_manifest_path = str(getattr(args, "save_manifest", "") or "").strip()
        if not save_manifest_path:
            save_manifest_path = resolve_save_manifest_path(
                repo_root=REPO_ROOT_HINT,
                install_root=normalize_path(args.store_root) if args.store_root else "",
                instance_root="",
                instance_manifest={},
                save_id=str(getattr(args, "save_id", "") or "").strip(),
            )
        if not save_manifest_path or not os.path.isfile(save_manifest_path):
            output_refusal("missing save manifest", refusal_payload(1, "REFUSE_INVALID_INTENT", "save manifest is required for export", {}), args.format)
            return EXIT_REFUSED
        payload = export_save_bundle(
            repo_root=REPO_ROOT_HINT,
            save_manifest_path=save_manifest_path,
            out_path=normalize_path(args.out),
            vendor_packs=str(getattr(args, "vendor_packs", "no") or "no").strip().lower() == "yes",
            bundle_id=str(getattr(args, "bundle_id", "") or "").strip(),
            store_root=normalize_path(args.store_root) if args.store_root else "",
        )
        write_output(bridge_engine_payload(payload, "save export ok"), args.format)
        return EXIT_OK if str(payload.get("result", "")).strip() == "complete" else EXIT_REFUSED
    if cmd == "import":
        import_engine = resolve_import_engine_module()
        payload = import_engine.import_save_bundle(
            repo_root=REPO_ROOT_HINT,
            bundle_path=normalize_path(args.bundle),
            out_path=normalize_path(args.out) if args.out else "",
            store_root=normalize_path(args.store_root) if args.store_root else "",
        )
        write_output(bridge_engine_payload(payload, "save import ok"), args.format)
        return EXIT_OK if str(payload.get("result", "")).strip() == "complete" else EXIT_REFUSED
    output_refusal("unknown save command", refusal_payload(1, "REFUSE_INVALID_INTENT", "unknown save command", {"cmd": cmd}), args.format)
    return EXIT_REFUSED


def handle_migrate_save(args: argparse.Namespace, deterministic: bool) -> int:
    extra: List[str] = [
        "--repo-root", REPO_ROOT_HINT,
        "--artifact-kind-id", "artifact.save",
        "--artifact-path", args.save_manifest,
        "--tick-applied", str(int(getattr(args, "tick_applied", 0) or 0)),
    ]
    if str(getattr(args, "out", "") or "").strip():
        extra += ["--output-path", args.out]
    if str(getattr(args, "to_version", "") or "").strip():
        extra += ["--migration-id", "migration.save_format.manual_to_{}".format(str(args.to_version).strip())]
    rc, payload, _stderr = run_script(resolve_apply_migration_cli(), extra)
    if deterministic and isinstance(payload, dict):
        payload.setdefault("extensions", {})
        payload["extensions"] = dict(payload.get("extensions") or {})
        payload["extensions"]["official.deterministic_invocation"] = True
    write_output(payload, args.format)
    if isinstance(payload, dict):
        _emit_setup_event(
            "lib",
            "lib.save.migrated",
            severity="info" if int(rc) == 0 else "warn",
            params={
                "result": str(payload.get("result", "")).strip() or ("complete" if int(rc) == 0 else "refused"),
                "artifact_path": str(getattr(args, "save_manifest", "")).strip(),
                "migration_chain_id": str(dict(payload.get("decision_record") or {}).get("chain_id", "")).strip(),
            },
        )
    return rc


def handle_migrate_instance(args: argparse.Namespace, deterministic: bool) -> int:
    del deterministic
    extra: List[str] = [
        "--repo-root", REPO_ROOT_HINT,
        "--artifact-kind-id", "artifact.instance_manifest",
        "--artifact-path", args.instance_manifest,
    ]
    if str(getattr(args, "out", "") or "").strip():
        extra += ["--output-path", args.out]
    if bool(getattr(args, "allow_read_only", False)):
        extra += ["--allow-read-only"]
    rc, payload, _stderr = run_script(resolve_apply_migration_cli(), extra)
    write_output(payload, args.format)
    if isinstance(payload, dict):
        _emit_setup_event(
            "lib",
            "lib.instance.migrated",
            severity="info" if int(rc) == 0 else "warn",
            params={
                "result": str(payload.get("result", "")).strip() or ("complete" if int(rc) == 0 else "refused"),
                "artifact_path": str(getattr(args, "instance_manifest", "")).strip(),
                "migration_chain_id": str(dict(payload.get("decision_record") or {}).get("chain_id", "")).strip(),
            },
        )
    return rc


def handle_pack(args: argparse.Namespace) -> int:
    cmd = str(getattr(args, "pack_cmd", "") or "").strip().lower()
    if cmd == "export":
        pack_root = resolve_pack_root(str(getattr(args, "pack_id", "") or "").strip(), explicit_root=str(getattr(args, "pack_root", "") or "").strip())
        payload = export_pack_bundle(
            repo_root=REPO_ROOT_HINT,
            pack_root=pack_root,
            out_path=normalize_path(args.out),
            bundle_id=str(getattr(args, "bundle_id", "") or "").strip(),
        )
        write_output(bridge_engine_payload(payload, "pack export ok"), args.format)
        return EXIT_OK if str(payload.get("result", "")).strip() == "complete" else EXIT_REFUSED
    if cmd == "import":
        import_engine = resolve_import_engine_module()
        payload = import_engine.import_pack_bundle(
            repo_root=REPO_ROOT_HINT,
            bundle_path=normalize_path(args.bundle),
            out_path=normalize_path(args.out) if args.out else "",
            store_root=normalize_path(args.store_root) if args.store_root else "",
        )
        write_output(bridge_engine_payload(payload, "pack import ok"), args.format)
        return EXIT_OK if str(payload.get("result", "")).strip() == "complete" else EXIT_REFUSED
    output_refusal("unknown pack command", refusal_payload(1, "REFUSE_INVALID_INTENT", "unknown pack command", {"cmd": cmd}), args.format)
    return EXIT_REFUSED


def handle_install(args: argparse.Namespace, deterministic: bool) -> int:
    if str(getattr(args, "registry_cmd", "") or "").strip():
        return handle_install_registry(args)
    if not args.manifest:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "manifest is required", {})
        output_refusal("missing manifest", refusal, args.format)
        return EXIT_REFUSED
    if not args.install_root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "install_root is required", {})
        output_refusal("missing install_root", refusal, args.format)
        return EXIT_REFUSED
    invocation = build_invocation(args, deterministic)
    tx_id = args.transaction_id or str(uuid.uuid5(uuid.NAMESPACE_URL, digest64(invocation)))
    artifact_root = derive_artifact_root(args.manifest, args.artifact_root)
    payload_root = payload_root_from_artifact(artifact_root, args.payload_root)
    plan = make_plan(invocation, args.manifest, payload_root, deterministic, tx_id)
    return handle_apply(argparse.Namespace(**{**vars(args), "plan": None, "manifest": args.manifest, "op": "install"}), deterministic)


def handle_repair(args: argparse.Namespace, deterministic: bool) -> int:
    invocation = build_invocation(args, deterministic)
    tx_id = args.transaction_id or str(uuid.uuid5(uuid.NAMESPACE_URL, digest64(invocation)))
    artifact_root = derive_artifact_root(args.manifest, args.artifact_root)
    payload_root = payload_root_from_artifact(artifact_root, args.payload_root)
    plan = make_plan(invocation, args.manifest, payload_root, deterministic, tx_id)
    code, payload = repair_from_plan(plan, args, deterministic)
    if code == EXIT_OK:
        output_ok("repair ok", payload, args.format)
    else:
        output_refusal("repair failed", payload.get("refusal", {}), args.format)
    return code


def handle_uninstall(args: argparse.Namespace, deterministic: bool) -> int:
    invocation = build_invocation(args, deterministic)
    tx_id = args.transaction_id or str(uuid.uuid5(uuid.NAMESPACE_URL, digest64(invocation)))
    plan = make_plan(invocation, args.manifest or "", args.payload_root or "", deterministic, tx_id)
    code, payload = uninstall_from_plan(plan, args, deterministic)
    if code == EXIT_OK:
        output_ok("uninstall ok", payload, args.format)
    else:
        output_refusal("uninstall failed", payload.get("refusal", {}), args.format)
    return code


def handle_rollback(args: argparse.Namespace, deterministic: bool) -> int:
    invocation = build_invocation(args, deterministic)
    tx_id = args.transaction_id or str(uuid.uuid5(uuid.NAMESPACE_URL, digest64(invocation)))
    plan = make_plan(invocation, args.manifest or "", args.payload_root or "", deterministic, tx_id)
    code, payload = rollback_from_plan(plan, args, deterministic)
    if code == EXIT_OK:
        output_ok("rollback ok", payload, args.format)
        _emit_setup_event(
            "update",
            "update.rollback.completed",
            params={
                "install_root": str(getattr(args, "install_root", "") or "").strip(),
                "target_release_id": str(getattr(args, "to", "") or "").strip(),
                "transaction_id": str(dict(payload.get("details") or {}).get("transaction_id", "")).strip(),
            },
        )
    else:
        output_refusal("rollback failed", payload.get("refusal", {}), args.format)
    return code


def handle_store(args: argparse.Namespace) -> int:
    cmd = str(getattr(args, "store_cmd", "") or "").strip().lower()
    if cmd != "gc":
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "unknown store command", {"cmd": cmd})
        output_refusal("unknown store command", refusal, args.format)
        return EXIT_REFUSED

    install_root = normalize_path(str(getattr(args, "install_root", "") or "").strip()) if str(getattr(args, "install_root", "") or "").strip() else ""
    explicit_store_root = normalize_path(str(getattr(args, "store_root", "") or "").strip()) if str(getattr(args, "store_root", "") or "").strip() else ""
    store_root = explicit_store_root
    install_roots: List[str] = []
    if install_root:
        install_roots.append(install_root)

    if not store_root:
        discovery = _discover_install_context(args)
        if str(discovery.get("result", "")).strip() != "complete":
            refusal = refusal_payload(
                5,
                str(discovery.get("refusal_code", "")).strip() or "refusal.install.not_found",
                "store GC requires a target install or store root",
                {
                    "remediation": "Use `setup store gc --install-root <path>` or `--store-root <path>` to target the store explicitly.",
                },
            )
            output_refusal("store gc refused", refusal, args.format)
            return EXIT_REFUSED
        install_root = normalize_path(str(discovery.get("resolved_install_root_path", "")).strip())
        install_roots = [install_root] if install_root else []
        install_manifest_path = os.path.join(install_root, DEFAULT_INSTALL_MANIFEST)
        validation = validate_install_manifest(repo_root=REPO_ROOT_HINT, install_manifest_path=install_manifest_path)
        if str(validation.get("result", "")).strip() != "complete":
            refusal = refusal_payload(
                5,
                str(validation.get("refusal_code", "")).strip() or "refusal.install.invalid_manifest",
                "install manifest validation failed",
                {
                    "remediation": "Run `setup verify --root {}` to repair the install before retrying store GC.".format(install_root),
                },
            )
            output_refusal("store gc refused", refusal, args.format)
            return EXIT_REFUSED
        store_root = normalize_path(resolve_store_root_from_install(install_root, dict(validation.get("install_manifest") or {})))

    if not store_root:
        refusal = refusal_payload(
            5,
            "refusal.store.gc.store_root_missing",
            "store root could not be resolved",
            {
                "remediation": "Provide `--store-root <path>` or ensure `install.manifest.json` declares `store_root_ref`.",
            },
        )
        output_refusal("store gc refused", refusal, args.format)
        return EXIT_REFUSED

    result = run_store_gc(
        store_root,
        repo_root=REPO_ROOT_HINT,
        gc_policy_id=str(getattr(args, "gc_policy_id", "") or DEFAULT_GC_POLICY_ID).strip() or DEFAULT_GC_POLICY_ID,
        install_roots=install_roots,
        registry_path=str(getattr(args, "registry_path", "") or "").strip(),
        allow_aggressive=bool(getattr(args, "allow_aggressive", False)),
        allow_portable=bool(getattr(args, "allow_portable_store", False)),
    )
    if str(result.get("result", "")).strip() != "complete":
        refusal = refusal_payload(
            5,
            str(result.get("refusal_code", "")).strip() or "refusal.store.gc.unknown",
            str(result.get("message", "")).strip() or "store gc refused",
            {
                "remediation": str(result.get("remediation", "")).strip(),
            },
        )
        output_refusal("store gc refused", refusal, args.format)
        _emit_setup_event(
            "lib",
            "lib.store.gc.refused",
            severity="warn",
            params={
                "store_root": store_root,
                "gc_policy_id": str(getattr(args, "gc_policy_id", "") or DEFAULT_GC_POLICY_ID).strip() or DEFAULT_GC_POLICY_ID,
                "refusal_code": str(result.get("refusal_code", "")).strip(),
            },
        )
        return EXIT_REFUSED

    gc_report = dict(result.get("gc_report") or {})
    output_ok(
        "store gc completed",
        {
            "details": {
                "store_root": store_root,
                "gc_policy": dict(result.get("gc_policy") or {}),
                "gc_report": gc_report,
                "reachability_report": dict(result.get("reachability_report") or {}),
                "store_verify_report": dict(result.get("store_verify_report") or {}),
            }
        },
        args.format,
    )
    _emit_setup_event(
        "lib",
        "lib.store.gc.completed",
        params={
            "store_root": store_root,
            "gc_policy_id": str(gc_report.get("gc_policy_id", "")).strip(),
            "deleted_count": int(len(list(gc_report.get("deleted_hashes") or []))),
            "quarantined_count": int(len(list(gc_report.get("quarantined_hashes") or []))),
        },
    )
    return EXIT_OK


def _legacy_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dominium setup CLI (offline-first, transactional).")
    ap.add_argument("--descriptor", action="store_true")
    ap.add_argument("--descriptor-file", default="")
    ap.add_argument("--format", default="json", choices=["json", "text"])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--deterministic", nargs="?", const="1", default="0")
    ap.add_argument("--transaction-id", default=None)
    ap.add_argument("--ui-mode", default="cli")
    ap.add_argument("--capability-baseline", default=DEFAULT_CAPABILITY_BASELINE)
    ap.add_argument("--build-number", default=0, type=int)
    ap.add_argument("--artifact-root", default=None)
    ap.add_argument("--payload-root", default=None)
    ap.add_argument("--network-mode", default="auto")
    ap.add_argument("--simulate-failure", default=None)

    sub = ap.add_subparsers(dest="cmd")

    export_inv = sub.add_parser("export-invocation")
    export_inv.add_argument("--manifest", required=False)
    export_inv.add_argument("--op", required=True)
    export_inv.add_argument("--scope", default="portable")
    export_inv.add_argument("--platform", default="")
    export_inv.add_argument("--install-root", dest="install_root", default="")
    export_inv.add_argument("--data-root", dest="data_root", default="")
    export_inv.add_argument("--ui-mode", default=None)
    export_inv.add_argument("--frontend-id", default="")
    export_inv.add_argument("--state", default=None)
    export_inv.add_argument("--out", required=True)

    plan_cmd = sub.add_parser("plan")
    plan_cmd.add_argument("--manifest", required=False)
    plan_cmd.add_argument("--invocation", default=None)
    plan_cmd.add_argument("--request", default=None)
    plan_cmd.add_argument("--op", default="install")
    plan_cmd.add_argument("--scope", default="portable")
    plan_cmd.add_argument("--platform", default="")
    plan_cmd.add_argument("--install-root", dest="install_root", default="")
    plan_cmd.add_argument("--data-root", dest="data_root", default="")
    plan_cmd.add_argument("--ui-mode", default=None)
    plan_cmd.add_argument("--frontend-id", default="")
    plan_cmd.add_argument("--install-mode", dest="install_mode", default="")
    plan_cmd.add_argument("--store-root", dest="store_root", default="")
    plan_cmd.add_argument("--out", default=None)
    plan_cmd.add_argument("--out-plan", dest="out_plan", default=None)

    apply_cmd = sub.add_parser("apply")
    apply_cmd.add_argument("--plan", default=None)
    apply_cmd.add_argument("--manifest", required=False)
    apply_cmd.add_argument("--op", default="install")
    apply_cmd.add_argument("--scope", default="portable")
    apply_cmd.add_argument("--platform", default="")
    apply_cmd.add_argument("--install-root", dest="install_root", default="")
    apply_cmd.add_argument("--data-root", dest="data_root", default="")
    apply_cmd.add_argument("--ui-mode", default=None)
    apply_cmd.add_argument("--frontend-id", default="")
    apply_cmd.add_argument("--install-mode", dest="install_mode", default="")
    apply_cmd.add_argument("--store-root", dest="store_root", default="")
    apply_cmd.add_argument("--dry-run", action="store_true")
    apply_cmd.add_argument("--remove-data", action="store_true")

    detect_cmd = sub.add_parser("detect")
    detect_cmd.add_argument("--install-root", dest="install_root", default="")

    manifest_cmd = sub.add_parser("manifest")
    manifest_sub = manifest_cmd.add_subparsers(dest="subcmd")
    manifest_validate = manifest_sub.add_parser("validate")
    manifest_validate.add_argument("--in", dest="in_path", required=False)
    manifest_validate.add_argument("--json", action="store_true")

    install_cmd = sub.add_parser("install")
    install_cmd.add_argument("registry_cmd", nargs="?", choices=["list", "add", "remove", "verify", "register", "unregister", "status", "plan", "apply"])
    install_cmd.add_argument("registry_target", nargs="?")
    install_cmd.add_argument("--registry-path", dest="registry_path", default="")
    install_cmd.add_argument("--install-id", dest="install_id", default="")
    install_cmd.add_argument("--profile", dest="install_profile_id", default="")
    install_cmd.add_argument("--policy", dest="resolution_policy_id", default="")
    install_cmd.add_argument("--manifest", required=False)
    install_cmd.add_argument("--op", default="install")
    install_cmd.add_argument("--scope", default="portable")
    install_cmd.add_argument("--platform", default="")
    install_cmd.add_argument("--arch", default="")
    install_cmd.add_argument("--abi", default="")
    install_cmd.add_argument("--install-root", dest="install_root", default="")
    install_cmd.add_argument("--data-root", dest="data_root", default="")
    install_cmd.add_argument("--frontend-id", default="")
    install_cmd.add_argument("--ui-mode", default=None)
    install_cmd.add_argument("--install-mode", dest="install_mode", default="")
    install_cmd.add_argument("--store-root", dest="store_root", default="")
    install_cmd.add_argument("--plan", default="")
    install_cmd.add_argument("--out", default="")
    install_cmd.add_argument("--out-plan", dest="out_plan", default="")
    install_cmd.add_argument("--json", action="store_true")

    update_cmd = sub.add_parser("update")
    update_sub = update_cmd.add_subparsers(dest="update_cmd")

    for update_name in ("check", "plan", "apply"):
        update_parser = update_sub.add_parser(update_name)
        update_parser.add_argument("--channel", default="mock")
        update_parser.add_argument("--release-index", default="")
        update_parser.add_argument("--plan", default="")
        update_parser.add_argument("--install-root", dest="install_root", default="")
        update_parser.add_argument("--install-id", dest="install_id", default="")
        update_parser.add_argument("--registry-path", dest="registry_path", default="")
        update_parser.add_argument("--profile", dest="install_profile_id", default="")
        update_parser.add_argument("--policy", dest="resolution_policy_id", default="")
        update_parser.add_argument("--platform", default="")
        update_parser.add_argument("--arch", default="")
        update_parser.add_argument("--abi", default="")
        update_parser.add_argument("--trust-policy-id", default="")
        update_parser.add_argument("--out", default="")
        update_parser.add_argument("--out-plan", dest="out_plan", default="")
        update_parser.add_argument("--json", action="store_true")

    instance_cmd = sub.add_parser("instance")
    instance_sub = instance_cmd.add_subparsers(dest="instance_cmd")

    instance_create = instance_sub.add_parser("create")
    instance_create.add_argument("--install-manifest", required=True)
    instance_create.add_argument("--data-root", required=True)
    instance_create.add_argument("--instance-root", default=None)
    instance_create.add_argument("--instance-id", default=None)
    instance_create.add_argument("--mode", choices=["linked", "portable"], default="portable")
    instance_create.add_argument("--instance-kind", choices=["instance.client", "instance.server", "instance.tooling"], default="instance.client")
    instance_create.add_argument("--store-root", default=None)
    instance_create.add_argument("--profile", action="append", default=[])
    instance_create.add_argument("--modpack", action="append", default=[])
    instance_create.add_argument("--pack-root", action="append", default=[])
    instance_create.add_argument("--capability-lockfile", default=None)
    instance_create.add_argument("--sandbox-policy", default=None)
    instance_create.add_argument("--sandbox-policy-ref", default=None)
    instance_create.add_argument("--mod-policy-id", default="mod.policy.default")
    instance_create.add_argument("--overlay-conflict-policy-id", default="overlay.conflict.default")
    instance_create.add_argument("--default-session-template-id", default="session.template.default")
    instance_create.add_argument("--seed-policy", choices=["fixed", "prompt", "deterministic_counter"], default="prompt")
    instance_create.add_argument("--renderer-mode", choices=["software", "hardware_stub"], default=None)
    instance_create.add_argument("--ui-mode-default", choices=["cli", "tui", "rendered"], default="cli")
    instance_create.add_argument("--allow-read-only-fallback", action="store_true")
    instance_create.add_argument("--tick-budget-policy-id", default="tick.budget.default")
    instance_create.add_argument("--compute-profile-id", default="compute.profile.default")
    instance_create.add_argument("--save-ref", action="append", default=[])
    instance_create.add_argument("--last-opened-save-id", default="")
    instance_create.add_argument("--required-product-build", action="append", default=[])
    instance_create.add_argument("--required-contract-range", action="append", default=[])
    instance_create.add_argument("--update-channel", default="stable")
    instance_create.add_argument("--created-at", default=None)

    instance_clone = instance_sub.add_parser("clone")
    instance_clone.add_argument("--source-manifest", required=True)
    instance_clone.add_argument("--data-root", required=True)
    instance_clone.add_argument("--instance-id", default=None)
    instance_clone.add_argument("--store-root", default=None)
    instance_clone.add_argument("--duplicate-embedded-artifacts", action="store_true")
    instance_clone.add_argument("--sandbox-policy", default=None)
    instance_clone.add_argument("--created-at", default=None)

    instance_edit = instance_sub.add_parser("edit")
    instance_edit.add_argument("--instance-manifest", required=True)
    instance_edit.add_argument("--install-manifest", default=None)
    instance_edit.add_argument("--sandbox-policy", default=None)
    instance_edit.add_argument("--mode", choices=["linked", "portable"], default=None)
    instance_edit.add_argument("--instance-kind", choices=["instance.client", "instance.server", "instance.tooling"], default=None)
    instance_edit.add_argument("--store-root", default=None)
    instance_edit.add_argument("--profile", action="append", default=[])
    instance_edit.add_argument("--modpack", action="append", default=[])
    instance_edit.add_argument("--save-ref", action="append", default=[])
    instance_edit.add_argument("--last-opened-save-id", default=None)
    instance_edit.add_argument("--renderer-mode", choices=["software", "hardware_stub"], default=None)
    instance_edit.add_argument("--ui-mode-default", choices=["cli", "tui", "rendered"], default=None)
    instance_edit.add_argument("--allow-read-only-fallback", action="store_true")
    instance_edit.add_argument("--deny-read-only-fallback", action="store_true")
    instance_edit.add_argument("--tick-budget-policy-id", default=None)
    instance_edit.add_argument("--compute-profile-id", default=None)
    instance_edit.add_argument("--default-session-template-id", default=None)
    instance_edit.add_argument("--seed-policy", choices=["fixed", "prompt", "deterministic_counter"], default=None)
    instance_edit.add_argument("--mod-policy-id", default=None)
    instance_edit.add_argument("--overlay-conflict-policy-id", default=None)
    instance_edit.add_argument("--required-product-build", action="append", default=[])
    instance_edit.add_argument("--required-contract-range", action="append", default=[])

    instance_export = instance_sub.add_parser("export")
    instance_export.add_argument("--instance-manifest", default="")
    instance_export.add_argument("--instance-id", default="")
    instance_export.add_argument("--out", required=True)
    instance_export.add_argument("--mode", choices=["linked", "portable"], default="portable")
    instance_export.add_argument("--bundle-id", default=None)
    instance_export.add_argument("--created-at", default=None)
    instance_export.add_argument("--created-by", default=None)
    instance_export.add_argument("--tool-version", default=None)
    instance_export.add_argument("--trust-tier", default=None)
    instance_export.add_argument("--store-root", default=None)

    instance_import = instance_sub.add_parser("import")
    instance_import.add_argument("--bundle", required=True)
    instance_import.add_argument("--out", default="")
    instance_import.add_argument("--instance-id", default=None)
    instance_import.add_argument("--import-mode", choices=["linked", "portable"], default=None)
    instance_import.add_argument("--store-root", default=None)
    instance_import.add_argument("--available-pack", action="append", default=[])
    instance_import.add_argument("--confirm", action="store_true")

    save_cmd = sub.add_parser("save")
    save_sub = save_cmd.add_subparsers(dest="save_cmd")

    save_export = save_sub.add_parser("export")
    save_export.add_argument("--save-id", default="")
    save_export.add_argument("--save-manifest", default="")
    save_export.add_argument("--out", required=True)
    save_export.add_argument("--vendor-packs", choices=["yes", "no"], default="no")
    save_export.add_argument("--bundle-id", default=None)
    save_export.add_argument("--store-root", default="")

    save_import = save_sub.add_parser("import")
    save_import.add_argument("--bundle", required=True)
    save_import.add_argument("--out", default="")
    save_import.add_argument("--store-root", default="")

    pack_cmd = sub.add_parser("pack")
    pack_sub = pack_cmd.add_subparsers(dest="pack_cmd")

    pack_export = pack_sub.add_parser("export")
    pack_export.add_argument("--pack-id", default="")
    pack_export.add_argument("--pack-root", default="")
    pack_export.add_argument("--out", required=True)
    pack_export.add_argument("--bundle-id", default=None)

    pack_import = pack_sub.add_parser("import")
    pack_import.add_argument("--bundle", required=True)
    pack_import.add_argument("--out", default="")
    pack_import.add_argument("--store-root", default="")

    repair_cmd = sub.add_parser("repair")
    repair_cmd.add_argument("--manifest", required=True)
    repair_cmd.add_argument("--op", default="repair")
    repair_cmd.add_argument("--scope", default="portable")
    repair_cmd.add_argument("--platform", default="")
    repair_cmd.add_argument("--install-root", dest="install_root", required=True)
    repair_cmd.add_argument("--data-root", dest="data_root", default="")
    repair_cmd.add_argument("--frontend-id", default="")
    repair_cmd.add_argument("--ui-mode", default=None)
    repair_cmd.add_argument("--install-mode", dest="install_mode", default="")
    repair_cmd.add_argument("--store-root", dest="store_root", default="")

    uninstall_cmd = sub.add_parser("uninstall")
    uninstall_cmd.add_argument("--manifest", required=False)
    uninstall_cmd.add_argument("--op", default="uninstall")
    uninstall_cmd.add_argument("--scope", default="portable")
    uninstall_cmd.add_argument("--platform", default="")
    uninstall_cmd.add_argument("--install-root", dest="install_root", required=True)
    uninstall_cmd.add_argument("--data-root", dest="data_root", default="")
    uninstall_cmd.add_argument("--frontend-id", default="")
    uninstall_cmd.add_argument("--ui-mode", default=None)
    uninstall_cmd.add_argument("--remove-data", action="store_true")

    rollback_cmd = sub.add_parser("rollback")
    rollback_cmd.add_argument("--manifest", required=False)
    rollback_cmd.add_argument("--op", default="rollback")
    rollback_cmd.add_argument("--scope", default="portable")
    rollback_cmd.add_argument("--platform", default="")
    rollback_cmd.add_argument("--install-root", dest="install_root", required=True)
    rollback_cmd.add_argument("--data-root", dest="data_root", default="")
    rollback_cmd.add_argument("--frontend-id", default="")
    rollback_cmd.add_argument("--ui-mode", default=None)
    rollback_cmd.add_argument("--to", default="")

    trust_cmd = sub.add_parser("trust")
    trust_sub = trust_cmd.add_subparsers(dest="trust_cmd")

    trust_list_cmd = trust_sub.add_parser("list")
    trust_list_cmd.add_argument("--install-root", dest="install_root", default="")
    trust_list_cmd.add_argument("--trust-policy-id", default="")
    trust_list_cmd.add_argument("--json", action="store_true")

    trust_status_cmd = trust_sub.add_parser("status")
    trust_status_cmd.add_argument("--install-root", dest="install_root", default="")
    trust_status_cmd.add_argument("--install-id", dest="install_id", default="")
    trust_status_cmd.add_argument("--registry-path", dest="registry_path", default="")
    trust_status_cmd.add_argument("--trust-policy-id", default="")
    trust_status_cmd.add_argument("--json", action="store_true")

    trust_import_cmd = trust_sub.add_parser("import")
    trust_import_cmd.add_argument("bundle")
    trust_import_cmd.add_argument("--install-root", dest="install_root", default="")
    trust_import_cmd.add_argument("--trust-policy-id", default="")
    trust_import_cmd.add_argument("--json", action="store_true")

    trust_policy_cmd = trust_sub.add_parser("policy")
    trust_policy_sub = trust_policy_cmd.add_subparsers(dest="trust_policy_cmd")
    trust_policy_set_cmd = trust_policy_sub.add_parser("set")
    trust_policy_set_cmd.add_argument("policy_id")
    trust_policy_set_cmd.add_argument("--install-root", dest="install_root", default="")
    trust_policy_set_cmd.add_argument("--trust-policy-id", default="")
    trust_policy_set_cmd.add_argument("--json", action="store_true")

    governance_cmd = sub.add_parser("governance")
    governance_sub = governance_cmd.add_subparsers(dest="governance_cmd")
    governance_status_cmd = governance_sub.add_parser("status")
    governance_status_cmd.add_argument("--install-root", dest="install_root", default="")
    governance_status_cmd.add_argument("--install-id", dest="install_id", default="")
    governance_status_cmd.add_argument("--registry-path", dest="registry_path", default="")
    governance_status_cmd.add_argument("--json", action="store_true")

    store_cmd = sub.add_parser("store")
    store_sub = store_cmd.add_subparsers(dest="store_cmd")
    store_gc_cmd = store_sub.add_parser("gc")
    store_gc_cmd.add_argument("--policy", dest="gc_policy_id", default=DEFAULT_GC_POLICY_ID)
    store_gc_cmd.add_argument("--store-root", dest="store_root", default="")
    store_gc_cmd.add_argument("--install-root", dest="install_root", default="")
    store_gc_cmd.add_argument("--install-id", dest="install_id", default="")
    store_gc_cmd.add_argument("--registry-path", dest="registry_path", default="")
    store_gc_cmd.add_argument("--allow-aggressive", action="store_true")
    store_gc_cmd.add_argument("--allow-portable-store", action="store_true")
    store_gc_cmd.add_argument("--json", action="store_true")

    migrate_save_cmd = sub.add_parser("migrate-save")
    migrate_save_cmd.add_argument("--save-manifest", required=True)
    migrate_save_cmd.add_argument("--out", default="")
    migrate_save_cmd.add_argument("--to-version", default="")
    migrate_save_cmd.add_argument("--tick-applied", type=int, default=0)
    migrate_save_cmd.add_argument("--json", action="store_true")

    migrate_instance_cmd = sub.add_parser("migrate-instance")
    migrate_instance_cmd.add_argument("--instance-manifest", required=True)
    migrate_instance_cmd.add_argument("--out", default="")
    migrate_instance_cmd.add_argument("--allow-read-only", action="store_true")
    migrate_instance_cmd.add_argument("--json", action="store_true")

    verify_cmd = sub.add_parser("verify")
    verify_cmd.add_argument("--root", default="")
    verify_cmd.add_argument("--schema-root", default="")
    verify_cmd.add_argument("--bundle-id", default="")
    verify_cmd.add_argument("--mod-policy-id", default="mod_policy.lab")
    verify_cmd.add_argument("--overlay-conflict-policy-id", default="")
    verify_cmd.add_argument("--contract-bundle-path", default="")
    verify_cmd.add_argument("--release-manifest", default="")
    verify_cmd.add_argument("--trust-policy-id", default="")
    verify_cmd.add_argument("--out-report", default="")
    verify_cmd.add_argument("--out-lock", default="")
    verify_cmd.add_argument("--write-outputs", action="store_true")

    list_packs_cmd = sub.add_parser("list-packs")
    list_packs_cmd.add_argument("--root", default="")
    list_packs_cmd.add_argument("--schema-root", default="")
    list_packs_cmd.add_argument("--bundle-id", default="")
    list_packs_cmd.add_argument("--mod-policy-id", default="mod_policy.lab")
    list_packs_cmd.add_argument("--overlay-conflict-policy-id", default="")
    list_packs_cmd.add_argument("--contract-bundle-path", default="")
    list_packs_cmd.add_argument("--trust-policy-id", default="")

    build_lock_cmd = sub.add_parser("build-lock")
    build_lock_cmd.add_argument("--root", default="")
    build_lock_cmd.add_argument("--schema-root", default="")
    build_lock_cmd.add_argument("--bundle-id", default="")
    build_lock_cmd.add_argument("--mod-policy-id", default="mod_policy.lab")
    build_lock_cmd.add_argument("--overlay-conflict-policy-id", default="")
    build_lock_cmd.add_argument("--contract-bundle-path", default="")
    build_lock_cmd.add_argument("--trust-policy-id", default="")
    build_lock_cmd.add_argument("--out-report", default="")
    build_lock_cmd.add_argument("--out-lock", default="")

    diagnose_cmd = sub.add_parser("diagnose-pack")
    diagnose_cmd.add_argument("--root", default="")
    diagnose_cmd.add_argument("--schema-root", default="")
    diagnose_cmd.add_argument("--bundle-id", default="")
    diagnose_cmd.add_argument("--mod-policy-id", default="mod_policy.lab")
    diagnose_cmd.add_argument("--overlay-conflict-policy-id", default="")
    diagnose_cmd.add_argument("--contract-bundle-path", default="")
    diagnose_cmd.add_argument("--trust-policy-id", default="")
    diagnose_cmd.add_argument("--pack-id", required=True)

    args = ap.parse_args(argv)
    if bool(getattr(args, "json", False)):
        args.format = "json"

    deterministic = parse_deterministic(args.deterministic)
    if bool(args.descriptor) or str(args.descriptor_file or "").strip():
        emitted = emit_product_descriptor(
            REPO_ROOT_HINT,
            product_id="setup",
            descriptor_file=str(args.descriptor_file or "").strip(),
        )
        print(descriptor_json_text(dict(emitted.get("descriptor") or {})))
        return EXIT_OK
    args.deterministic = deterministic
    args.versions = {
        "engine_version": os.environ.get("DOMINO_VERSION_STRING", "0.0.0"),
        "game_version": os.environ.get("DOMINIUM_GAME_VERSION", "0.0.0"),
        "launcher_version": os.environ.get("DOMINIUM_LAUNCHER_VERSION", "0.0.0"),
        "setup_version": os.environ.get("DOMINIUM_SETUP_VERSION", "0.0.0"),
        "tools_version": os.environ.get("DOMINIUM_TOOLS_VERSION", "0.0.0"),
        "protocol_network": os.environ.get("DOM_PROTOCOL_NETWORK", "0"),
        "protocol_save": os.environ.get("DOM_PROTOCOL_SAVE", "0"),
        "protocol_mod": os.environ.get("DOM_PROTOCOL_MOD", "0"),
        "protocol_replay": os.environ.get("DOM_PROTOCOL_REPLAY", "0"),
        "supported_capabilities": [],
        "trust_tier": os.environ.get("DOM_TRUST_TIER", "official"),
    }
    args.capability_baseline = args.capability_baseline or DEFAULT_CAPABILITY_BASELINE

    args.network_status, args.network_notice = detect_network_status(args.network_mode)

    if args.cmd == "export-invocation":
        return handle_export_invocation(args, deterministic)
    if args.cmd == "plan":
        return handle_plan(args, deterministic)
    if args.cmd == "apply":
        return handle_apply(args, deterministic)
    if args.cmd == "detect":
        return handle_detect(args, deterministic)
    if args.cmd == "manifest" and args.subcmd == "validate":
        fmt = "json" if args.json else args.format
        args.format = fmt
        return handle_manifest_validate(args, deterministic)
    if args.cmd == "install":
        return handle_install(args, deterministic)
    if args.cmd == "update":
        return handle_update(args, deterministic)
    if args.cmd == "instance":
        return handle_instance(args, deterministic)
    if args.cmd == "save":
        return handle_save(args)
    if args.cmd == "pack":
        return handle_pack(args)
    if args.cmd == "repair":
        return handle_repair(args, deterministic)
    if args.cmd == "uninstall":
        return handle_uninstall(args, deterministic)
    if args.cmd == "rollback":
        return handle_rollback(args, deterministic)
    if args.cmd == "trust":
        return handle_trust(args)
    if args.cmd == "governance":
        return handle_governance(args)
    if args.cmd == "store":
        return handle_store(args)
    if args.cmd == "migrate-save":
        return handle_migrate_save(args, deterministic)
    if args.cmd == "migrate-instance":
        return handle_migrate_instance(args, deterministic)
    if args.cmd == "verify":
        return handle_verify(args, deterministic)
    if args.cmd == "list-packs":
        return handle_list_packs(args, deterministic)
    if args.cmd == "build-lock":
        return handle_build_lock(args, deterministic)
    if args.cmd == "diagnose-pack":
        return handle_diagnose_pack(args, deterministic)

    ap.print_help()
    return EXIT_USAGE


def main(argv: list[str] | None = None) -> int:
    def appshell_product_bootstrap(context: dict) -> int:
        delegate_argv = list(context.get("delegate_argv") or [])
        return _legacy_main(delegate_argv)

    return appshell_main(
        product_id="setup",
        argv=list(sys.argv[1:] if argv is None else argv),
        repo_root_hint=REPO_ROOT_HINT,
        product_bootstrap=appshell_product_bootstrap,
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        output_error("setup error: %s" % str(exc), "json")
        sys.exit(EXIT_ERROR)
