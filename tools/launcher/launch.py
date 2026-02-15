#!/usr/bin/env python3
"""Deterministic launcher command for dist + SessionSpec execution."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.validator import validate_instance  # noqa: E402
from tools.xstack.packagingx import validate_dist_layout  # noqa: E402
from tools.xstack.sessionx.runner import boot_session_spec  # noqa: E402
from tools.xstack.sessionx.script_runner import run_intent_script  # noqa: E402


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _refusal(reason_code: str, message: str, remediation_hint: str, relevant_ids: Dict[str, str], path: str) -> Dict[str, object]:
    ids = {}
    for key, value in sorted((relevant_ids or {}).items(), key=lambda row: str(row[0])):
        token = str(value).strip()
        if token:
            ids[str(key)] = token
    return {
        "result": "refused",
        "refusal": {
            "reason_code": str(reason_code),
            "message": str(message),
            "remediation_hint": str(remediation_hint),
            "relevant_ids": ids,
        },
        "errors": [
            {
                "code": str(reason_code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _find_dist_roots(root: str) -> List[str]:
    out: List[str] = []
    if os.path.isfile(os.path.join(root, "manifest.json")):
        out.append(root)
    if os.path.isdir(root):
        for name in sorted(os.listdir(root)):
            candidate = os.path.join(root, name)
            if os.path.isfile(os.path.join(candidate, "manifest.json")):
                out.append(candidate)
    return sorted(set(out))


def _list_saves(repo_root: str, saves_root: str) -> List[dict]:
    root = os.path.join(repo_root, saves_root.replace("/", os.sep))
    rows: List[dict] = []
    if not os.path.isdir(root):
        return rows
    for name in sorted(os.listdir(root)):
        save_dir = os.path.join(root, name)
        if not os.path.isdir(save_dir):
            continue
        spec = os.path.join(save_dir, "session_spec.json")
        if not os.path.isfile(spec):
            continue
        rows.append(
            {
                "save_id": str(name),
                "session_spec_path": _norm(os.path.relpath(spec, repo_root)),
            }
        )
    return rows


def _load_latest_run_meta(save_dir: str) -> dict:
    root = os.path.join(save_dir, "run_meta")
    if not os.path.isdir(root):
        return {}
    files = sorted(name for name in os.listdir(root) if name.endswith(".json"))
    if not files:
        return {}
    payload, err = _read_json(os.path.join(root, files[-1]))
    if err:
        return {}
    return payload


def _validate_session_vs_dist(
    repo_root: str,
    dist_root: str,
    session_spec_path: str,
    require_bundle: str,
) -> Dict[str, object]:
    spec_abs = os.path.normpath(os.path.abspath(session_spec_path))
    payload, err = _read_json(spec_abs)
    if err:
        return _refusal(
            "REFUSE_SESSION_SPEC_INVALID",
            "session spec is missing or invalid JSON",
            "Provide a valid SessionSpec file path.",
            {"session_spec_path": _norm(os.path.relpath(spec_abs, repo_root))},
            "$.session_spec",
        )
    valid = validate_instance(repo_root=repo_root, schema_name="session_spec", payload=payload, strict_top_level=True)
    if not bool(valid.get("valid", False)):
        return _refusal(
            "REFUSE_SESSION_SPEC_INVALID",
            "session spec failed schema validation",
            "Fix SessionSpec fields to satisfy schemas/session_spec.schema.json.",
            {"session_spec_path": _norm(os.path.relpath(spec_abs, repo_root))},
            "$.session_spec",
        )

    lock_path = os.path.join(dist_root, "lockfile.json")
    lock_payload, lock_err = _read_json(lock_path)
    if lock_err:
        return _refusal(
            "LOCKFILE_MISMATCH",
            "dist lockfile is missing or invalid",
            "Rebuild dist with tools/setup/build and retry launch.",
            {"dist_root": _norm(os.path.relpath(dist_root, repo_root))},
            "$.lockfile",
        )
    bundle_id = str(payload.get("bundle_id", "")).strip()
    if str(require_bundle).strip():
        bundle_id = str(require_bundle).strip()
    lock_bundle_id = str(lock_payload.get("bundle_id", "")).strip()
    if bundle_id != lock_bundle_id:
        return _refusal(
            "PACK_INCOMPATIBLE",
            "session bundle_id does not match dist lockfile bundle_id",
            "Use a SessionSpec created for this bundle or rebuild dist for the session bundle.",
            {
                "session_bundle_id": bundle_id,
                "dist_bundle_id": lock_bundle_id,
            },
            "$.bundle_id",
        )
    if str(payload.get("pack_lock_hash", "")).strip() != str(lock_payload.get("pack_lock_hash", "")).strip():
        return _refusal(
            "LOCKFILE_MISMATCH",
            "session pack_lock_hash does not match dist lockfile",
            "Regenerate SessionSpec against this dist lockfile inputs.",
            {
                "save_id": str(payload.get("save_id", "")),
                "bundle_id": lock_bundle_id,
            },
            "$.pack_lock_hash",
        )

    save_id = str(payload.get("save_id", "")).strip()
    save_dir = os.path.join(repo_root, "saves", save_id)
    run_meta = _load_latest_run_meta(save_dir)
    if isinstance(run_meta, dict) and run_meta:
        run_lock = str(run_meta.get("pack_lock_hash", "")).strip()
        if run_lock and run_lock != str(lock_payload.get("pack_lock_hash", "")).strip():
            return _refusal(
                "PACK_INCOMPATIBLE",
                "existing save run-meta pack_lock_hash is incompatible with dist lockfile",
                "Create a compatible save or rebuild dist matching the existing save lockfile.",
                {
                    "save_id": save_id,
                },
                "$.pack_lock_hash",
            )
        run_regs = dict(run_meta.get("registry_hashes") or {})
        lock_regs = dict(lock_payload.get("registries") or {})
        if run_regs and run_regs != lock_regs:
            return _refusal(
                "REGISTRY_MISMATCH",
                "existing save run-meta registry hashes are incompatible with dist lockfile",
                "Use a compatible save, or rebuild with matching registries.",
                {"save_id": save_id},
                "$.registry_hashes",
            )

    return {
        "result": "complete",
        "session_spec_path": _norm(os.path.relpath(spec_abs, repo_root)),
        "session_payload": payload,
        "lockfile_payload": lock_payload,
    }


def cmd_list_builds(repo_root: str, root: str) -> Dict[str, object]:
    root_abs = os.path.normpath(os.path.abspath(os.path.join(repo_root, root))) if not os.path.isabs(root) else os.path.normpath(root)
    rows = []
    for dist_root in _find_dist_roots(root_abs):
        checked = validate_dist_layout(repo_root=repo_root, dist_root=dist_root)
        if checked.get("result") == "complete":
            rows.append(
                {
                    "dist_root": _norm(os.path.relpath(dist_root, repo_root)),
                    "bundle_id": str(checked.get("bundle_id", "")),
                    "pack_lock_hash": str(checked.get("pack_lock_hash", "")),
                    "canonical_content_hash": str(checked.get("canonical_content_hash", "")),
                }
            )
    return {"result": "complete", "builds": sorted(rows, key=lambda item: item["dist_root"])}


def cmd_list_saves(repo_root: str, saves_root: str) -> Dict[str, object]:
    return {
        "result": "complete",
        "saves": _list_saves(repo_root, saves_root),
    }


def cmd_run(
    repo_root: str,
    dist_root: str,
    session_spec_path: str,
    script_path: str,
    workers: int,
    logical_shards: int,
    write_state: bool,
    bundle_id: str,
) -> Dict[str, object]:
    dist_abs = os.path.normpath(os.path.abspath(os.path.join(repo_root, dist_root))) if not os.path.isabs(dist_root) else os.path.normpath(dist_root)
    dist_check = validate_dist_layout(repo_root=repo_root, dist_root=dist_abs)
    if dist_check.get("result") != "complete":
        return dist_check
    comp = _validate_session_vs_dist(
        repo_root=repo_root,
        dist_root=dist_abs,
        session_spec_path=session_spec_path,
        require_bundle=bundle_id,
    )
    if comp.get("result") != "complete":
        return comp

    resolved_bundle = str(bundle_id).strip() or str((comp.get("session_payload") or {}).get("bundle_id", ""))
    lock_path = os.path.join(dist_abs, "lockfile.json")
    regs_dir = os.path.join(dist_abs, "registries")
    boot = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=session_spec_path,
        bundle_id=resolved_bundle,
        compile_if_missing=False,
        lockfile_path=lock_path,
        registries_dir=regs_dir,
    )
    if boot.get("result") != "complete":
        return boot

    script_result = {}
    if str(script_path).strip():
        script_result = run_intent_script(
            repo_root=repo_root,
            session_spec_path=session_spec_path,
            script_path=script_path,
            bundle_id=resolved_bundle,
            compile_if_missing=False,
            workers=int(workers),
            write_state=bool(write_state),
            logical_shards=int(logical_shards),
            lockfile_path=lock_path,
            registries_dir=regs_dir,
        )
        if script_result.get("result") != "complete":
            return script_result

    return {
        "result": "complete",
        "dist_root": _norm(os.path.relpath(dist_abs, repo_root)),
        "bundle_id": resolved_bundle,
        "session_spec_path": str(comp.get("session_spec_path", "")),
        "lockfile_path": _norm(os.path.relpath(lock_path, repo_root)),
        "registries_dir": _norm(os.path.relpath(regs_dir, repo_root)),
        "pack_lock_hash": str((comp.get("lockfile_payload") or {}).get("pack_lock_hash", "")),
        "registry_hashes": dict((comp.get("lockfile_payload") or {}).get("registries") or {}),
        "boot": boot,
        "script": script_result,
        "launch_mode": "headless",
        "lockfile_enforcement": "required",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch deterministic lab sessions from dist bundles.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="cmd")

    list_builds = sub.add_parser("list-builds", help="List available dist builds")
    list_builds.add_argument("--root", default="dist")

    list_saves = sub.add_parser("list-saves", help="List available session saves")
    list_saves.add_argument("--saves-root", default="saves")

    run_cmd = sub.add_parser("run", help="Validate dist + session and launch headless client")
    run_cmd.add_argument("--dist", default="dist")
    run_cmd.add_argument("--session", required=True)
    run_cmd.add_argument("--bundle", default="")
    run_cmd.add_argument("--script", default="")
    run_cmd.add_argument("--workers", type=int, default=1)
    run_cmd.add_argument("--logical-shards", type=int, default=1)
    run_cmd.add_argument("--write-state", default="off", choices=("on", "off"))

    args = parser.parse_args()
    repo_root = _repo_root(args.repo_root)

    if args.cmd == "list-builds":
        result = cmd_list_builds(repo_root=repo_root, root=str(args.root))
    elif args.cmd == "list-saves":
        result = cmd_list_saves(repo_root=repo_root, saves_root=str(args.saves_root))
    elif args.cmd == "run":
        result = cmd_run(
            repo_root=repo_root,
            dist_root=str(args.dist),
            session_spec_path=str(args.session),
            script_path=str(args.script),
            workers=int(args.workers),
            logical_shards=int(args.logical_shards),
            write_state=str(args.write_state).strip().lower() != "off",
            bundle_id=str(args.bundle),
        )
    else:
        parser.print_help()
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
