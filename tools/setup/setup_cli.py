#!/usr/bin/env python3
from __future__ import print_function

import argparse
import base64
import hashlib
import json
import os
import shutil
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple


DEFAULT_CAPABILITY_BASELINE = "BASELINE_MAINLINE_CORE"
NULL_UUID = "00000000-0000-0000-0000-000000000000"
DEFAULT_INSTALL_MANIFEST = "install.manifest.json"
DEFAULT_COMPAT_REPORT = "compat_report.json"
DEFAULT_SETUP_STATE = "setup_state.json"

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_REFUSED = 3


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


def install_manifest_payload(install_id: str,
                             install_root: str,
                             created_at: str,
                             build_number: int,
                             versions: dict) -> dict:
    binaries = {
        "engine": {
            "product_id": "domino.engine",
            "product_version": versions.get("engine_version", "0.0.0"),
        },
        "game": {
            "product_id": "dominium.game",
            "product_version": versions.get("game_version", "0.0.0"),
        },
        "client": {
            "product_id": "dominium.client",
            "product_version": versions.get("game_version", "0.0.0"),
        },
        "server": {
            "product_id": "dominium.server",
            "product_version": versions.get("game_version", "0.0.0"),
        },
        "launcher": {
            "product_id": "dominium.launcher",
            "product_version": versions.get("launcher_version", "0.0.0"),
        },
        "setup": {
            "product_id": "dominium.setup",
            "product_version": versions.get("setup_version", "0.0.0"),
        },
        "tools": {
            "product_id": "dominium.tools",
            "product_version": versions.get("tools_version", "0.0.0"),
        },
    }
    return {
        "install_id": install_id,
        "install_root": install_root,
        "binaries": binaries,
        "supported_capabilities": versions.get("supported_capabilities", []),
        "protocol_versions": {
            "network": versions.get("protocol_network", "0"),
            "save": versions.get("protocol_save", "0"),
            "mod": versions.get("protocol_mod", "0"),
            "replay": versions.get("protocol_replay", "0"),
        },
        "build_identity": int(build_number),
        "trust_tier": versions.get("trust_tier", "official"),
        "created_at": created_at,
        "extensions": {},
    }


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


def write_output(payload: dict, fmt: str) -> None:
    if fmt == "text":
        msg = payload.get("message") or payload.get("result") or ""
        print(msg)
        return
    print(json.dumps(payload, indent=2))


def output_refusal(message: str, refusal: dict, fmt: str) -> None:
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

    if not install_root:
        refusal = refusal_payload(1, "REFUSE_INVALID_INTENT", "install_root is required", {})
        return EXIT_REFUSED, {"message": "missing install_root", "refusal": refusal}

    install_root = normalize_path(install_root)
    data_root = normalize_path(data_root) if data_root else normalize_path(os.path.join(install_root, "data"))

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
        ensure_dir(os.path.join(stage_root, "bin"))
        copy_tree(runtime_bin, os.path.join(stage_root, "bin"), overwrite=True)
        if os.path.isdir(launcher_bin):
            copy_tree(launcher_bin, os.path.join(stage_root, "bin"), overwrite=True)
        if os.path.isdir(tools_dir):
            copy_tree(tools_dir, os.path.join(stage_root, "tools"), overwrite=True)

        if args.simulate_failure == "stage":
            raise RuntimeError("simulated stage failure")

        created_at = now_timestamp(deterministic)
        install_id = str(uuid.uuid4())
        if deterministic:
            install_id = str(uuid.uuid5(uuid.NAMESPACE_URL, plan.get("invocation_digest64", "")))

        manifest_payload = install_manifest_payload(
            install_id=install_id,
            install_root=".",
            created_at=created_at,
            build_number=args.build_number or 0,
            versions=args.versions,
        )
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


def handle_install(args: argparse.Namespace, deterministic: bool) -> int:
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
    else:
        output_refusal("rollback failed", payload.get("refusal", {}), args.format)
    return code


def main() -> int:
    ap = argparse.ArgumentParser(description="Dominium setup CLI (offline-first, transactional).")
    ap.add_argument("--format", default="json", choices=["json", "text"])
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
    install_cmd.add_argument("--manifest", required=True)
    install_cmd.add_argument("--op", default="install")
    install_cmd.add_argument("--scope", default="portable")
    install_cmd.add_argument("--platform", default="")
    install_cmd.add_argument("--install-root", dest="install_root", required=True)
    install_cmd.add_argument("--data-root", dest="data_root", default="")
    install_cmd.add_argument("--frontend-id", default="")
    install_cmd.add_argument("--ui-mode", default=None)

    repair_cmd = sub.add_parser("repair")
    repair_cmd.add_argument("--manifest", required=True)
    repair_cmd.add_argument("--op", default="repair")
    repair_cmd.add_argument("--scope", default="portable")
    repair_cmd.add_argument("--platform", default="")
    repair_cmd.add_argument("--install-root", dest="install_root", required=True)
    repair_cmd.add_argument("--data-root", dest="data_root", default="")
    repair_cmd.add_argument("--frontend-id", default="")
    repair_cmd.add_argument("--ui-mode", default=None)

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

    args = ap.parse_args()

    deterministic = parse_deterministic(args.deterministic)
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
    if args.cmd == "repair":
        return handle_repair(args, deterministic)
    if args.cmd == "uninstall":
        return handle_uninstall(args, deterministic)
    if args.cmd == "rollback":
        return handle_rollback(args, deterministic)

    ap.print_help()
    return EXIT_USAGE


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        output_error("setup error: %s" % str(exc), "json")
        sys.exit(EXIT_ERROR)
