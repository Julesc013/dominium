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

from src.appshell import appshell_main  # noqa: E402
from src.appshell.pack_verifier_adapter import verify_pack_root  # noqa: E402
from src.compat import descriptor_json_text, emit_product_descriptor  # noqa: E402


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _launcher_defaults() -> dict:
    from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID
    from tools.xstack.sessionx.creator import (
        DEFAULT_BUDGET_POLICY_ID,
        DEFAULT_EXPERIENCE_ID,
        DEFAULT_FIDELITY_POLICY_ID,
        DEFAULT_LAW_PROFILE_ID,
        DEFAULT_PARAMETER_BUNDLE_ID,
        DEFAULT_PRIVILEGE_LEVEL,
        DEFAULT_SCENARIO_ID,
    )
    from tools.xstack.sessionx.pipeline_contract import DEFAULT_PIPELINE_ID

    return {
        "DEFAULT_BUNDLE_ID": DEFAULT_BUNDLE_ID,
        "DEFAULT_BUDGET_POLICY_ID": DEFAULT_BUDGET_POLICY_ID,
        "DEFAULT_EXPERIENCE_ID": DEFAULT_EXPERIENCE_ID,
        "DEFAULT_FIDELITY_POLICY_ID": DEFAULT_FIDELITY_POLICY_ID,
        "DEFAULT_LAW_PROFILE_ID": DEFAULT_LAW_PROFILE_ID,
        "DEFAULT_PARAMETER_BUNDLE_ID": DEFAULT_PARAMETER_BUNDLE_ID,
        "DEFAULT_PIPELINE_ID": DEFAULT_PIPELINE_ID,
        "DEFAULT_PRIVILEGE_LEVEL": DEFAULT_PRIVILEGE_LEVEL,
        "DEFAULT_SCENARIO_ID": DEFAULT_SCENARIO_ID,
    }


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
    best_payload = {}
    best_key = ("", "", "", "")
    for name in sorted(entry for entry in os.listdir(root) if entry.endswith(".json")):
        payload, err = _read_json(os.path.join(root, name))
        if err:
            continue
        key = (
            str(payload.get("stopped_utc", "")),
            str(payload.get("started_utc", "")),
            str(payload.get("run_id", "")),
            str(name),
        )
        if key >= best_key:
            best_key = key
            best_payload = payload
    if not best_payload:
        return {}
    return best_payload


def _validate_session_vs_dist(
    repo_root: str,
    dist_root: str,
    session_spec_path: str,
    require_bundle: str,
) -> Dict[str, object]:
    from tools.xstack.compatx.validator import validate_instance

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
    from tools.xstack.packagingx import validate_dist_layout

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
    from tools.xstack.packagingx import validate_dist_layout
    from tools.xstack.sessionx.runner import boot_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script
    from tools.xstack.sessionx.server_gate import server_validate_transition

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
    selected_mod_policy_id = (
        str((comp.get("session_payload") or {}).get("mod_policy_id", "")).strip()
        or str((comp.get("lockfile_payload") or {}).get("mod_policy_id", "")).strip()
        or "mod_policy.lab"
    )
    selected_conflict_policy_id = str((comp.get("lockfile_payload") or {}).get("overlay_conflict_policy_id", "")).strip()
    compat = verify_pack_root(
        repo_root=repo_root,
        root=dist_abs,
        bundle_id=resolved_bundle,
        mod_policy_id=selected_mod_policy_id,
        overlay_conflict_policy_id=selected_conflict_policy_id,
        contract_bundle_path="",
    )
    if str(compat.get("result", "")) != "complete":
        return _refusal(
            "PACK_INCOMPATIBLE",
            "offline pack verification failed before launch",
            "Run launcher compat-status or setup verify to inspect the pack set.",
            {
                "bundle_id": resolved_bundle,
                "mod_policy_id": selected_mod_policy_id,
            },
            "$.pack_compatibility_report",
        )
    compat_report = dict(compat.get("report") or {})
    compat_pack_lock = dict(compat.get("pack_lock") or {})
    if not bool(compat_report.get("valid", False)):
        refusal_codes = list(compat_report.get("refusal_codes") or [])
        return _refusal(
            "PACK_INCOMPATIBLE",
            "offline pack verification refused the selected pack set",
            "Resolve the refused packs or choose a compatible bundle/mod policy before launching.",
            {
                "bundle_id": resolved_bundle,
                "mod_policy_id": selected_mod_policy_id,
                "report_id": str(compat_report.get("report_id", "")),
                "refusal_codes": ",".join(str(item) for item in refusal_codes),
            },
            "$.pack_compatibility_report.valid",
        )
    dist_pack_lock_hash = str((comp.get("lockfile_payload") or {}).get("pack_lock_hash", "")).strip()
    compat_pack_lock_hash = str(compat_pack_lock.get("pack_lock_hash", "")).strip()
    if compat_pack_lock_hash and dist_pack_lock_hash and compat_pack_lock_hash != dist_pack_lock_hash:
        return _refusal(
            "LOCKFILE_MISMATCH",
            "offline verification pack_lock_hash does not match dist lockfile",
            "Rebuild the dist lockfile or rebuild the validated pack lock from the same pack set.",
            {
                "dist_pack_lock_hash": dist_pack_lock_hash,
                "verified_pack_lock_hash": compat_pack_lock_hash,
            },
            "$.pack_lock_hash",
        )

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

    requested_stage = str(boot.get("last_stage_id", "")).strip()
    if str(script_path).strip():
        requested_stage = "stage.session_running"
    server_gate = server_validate_transition(
        repo_root=repo_root,
        session_spec_path=session_spec_path,
        from_stage_id=str(boot.get("last_stage_id", "")),
        to_stage_id=requested_stage,
        authority_context=dict((comp.get("session_payload") or {}).get("authority_context") or {}),
    )
    if server_gate.get("result") != "complete":
        return server_gate

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
        "server_gate": server_gate,
        "script": script_result,
        "launch_mode": "headless",
        "lockfile_enforcement": "required",
        "pack_compatibility_report": compat_report,
        "verified_pack_lock_hash": compat_pack_lock_hash,
    }


def cmd_compat_status(
    repo_root: str,
    dist_root: str,
    bundle_id: str,
    mod_policy_id: str,
    overlay_conflict_policy_id: str,
    contract_bundle_path: str,
) -> Dict[str, object]:
    dist_abs = os.path.normpath(os.path.abspath(os.path.join(repo_root, dist_root))) if not os.path.isabs(dist_root) else os.path.normpath(dist_root)
    compat = verify_pack_root(
        repo_root=repo_root,
        root=dist_abs,
        bundle_id=str(bundle_id).strip(),
        mod_policy_id=str(mod_policy_id).strip() or "mod_policy.lab",
        overlay_conflict_policy_id=str(overlay_conflict_policy_id).strip(),
        contract_bundle_path=str(contract_bundle_path).strip(),
    )
    if str(compat.get("result", "")) != "complete":
        return _refusal(
            "PACK_INCOMPATIBLE",
            "offline pack verification failed",
            "Run setup verify against the same dist root to inspect details.",
            {
                "dist_root": _norm(os.path.relpath(dist_abs, repo_root)),
                "bundle_id": str(bundle_id).strip(),
            },
            "$.pack_compatibility_report",
        )
    return {
        "result": "complete",
        "dist_root": _norm(os.path.relpath(dist_abs, repo_root)),
        "bundle_id": str(bundle_id).strip(),
        "mod_policy_id": str(mod_policy_id).strip() or "mod_policy.lab",
        "report": dict(compat.get("report") or {}),
        "pack_lock": dict(compat.get("pack_lock") or {}),
        "warnings": list(compat.get("warnings") or []),
        "errors": list(compat.get("errors") or []),
    }


def cmd_create_session(
    repo_root: str,
    save_id: str,
    bundle_id: str,
    pipeline_id: str,
    scenario_id: str,
    experience_id: str,
    law_profile_id: str,
    parameter_bundle_id: str,
    budget_policy_id: str,
    fidelity_policy_id: str,
    privilege_level: str,
    compile_outputs: bool,
) -> Dict[str, object]:
    from tools.xstack.sessionx.creator import create_session_spec

    return create_session_spec(
        repo_root=repo_root,
        save_id=str(save_id),
        bundle_id=str(bundle_id),
        pipeline_id=str(pipeline_id),
        scenario_id=str(scenario_id),
        mission_id="",
        experience_id=str(experience_id),
        law_profile_id=str(law_profile_id),
        parameter_bundle_id=str(parameter_bundle_id),
        budget_policy_id=str(budget_policy_id),
        fidelity_policy_id=str(fidelity_policy_id),
        rng_seed_string="seed.launcher.session.{}".format(str(save_id)),
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.launcher.universe.{}".format(str(save_id)),
        universe_id="",
        entitlements=[],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level=str(privilege_level),
        compile_outputs=bool(compile_outputs),
        saves_root_rel="saves",
    )


def _legacy_main(argv: list[str] | None = None) -> int:
    defaults = _launcher_defaults()

    parser = argparse.ArgumentParser(description="Launch deterministic lab sessions from dist bundles.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--descriptor", action="store_true")
    parser.add_argument("--descriptor-file", default="")
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

    compat_cmd = sub.add_parser("compat-status", help="Run offline pack compatibility verification against a dist root")
    compat_cmd.add_argument("--dist", default="dist")
    compat_cmd.add_argument("--bundle", default="")
    compat_cmd.add_argument("--mod-policy-id", default="mod_policy.lab")
    compat_cmd.add_argument("--overlay-conflict-policy-id", default="")
    compat_cmd.add_argument("--contract-bundle-path", default="")

    create_cmd = sub.add_parser("create-session", help="Create SessionSpec through launcher surface with declared pipeline_id")
    create_cmd.add_argument("--save-id", required=True)
    create_cmd.add_argument("--bundle", default=defaults["DEFAULT_BUNDLE_ID"])
    create_cmd.add_argument("--pipeline-id", default=defaults["DEFAULT_PIPELINE_ID"])
    create_cmd.add_argument("--scenario-id", default=defaults["DEFAULT_SCENARIO_ID"])
    create_cmd.add_argument("--experience-id", default=defaults["DEFAULT_EXPERIENCE_ID"])
    create_cmd.add_argument("--law-profile-id", default=defaults["DEFAULT_LAW_PROFILE_ID"])
    create_cmd.add_argument("--parameter-bundle-id", default=defaults["DEFAULT_PARAMETER_BUNDLE_ID"])
    create_cmd.add_argument("--budget-policy-id", default=defaults["DEFAULT_BUDGET_POLICY_ID"])
    create_cmd.add_argument("--fidelity-policy-id", default=defaults["DEFAULT_FIDELITY_POLICY_ID"])
    create_cmd.add_argument("--privilege-level", default=defaults["DEFAULT_PRIVILEGE_LEVEL"], choices=("observer", "operator", "system"))
    create_cmd.add_argument("--compile-outputs", default="on", choices=("on", "off"))

    args = parser.parse_args(argv)
    repo_root = _repo_root(args.repo_root)
    if bool(args.descriptor) or str(args.descriptor_file or "").strip():
        emitted = emit_product_descriptor(
            repo_root,
            product_id="launcher",
            descriptor_file=str(args.descriptor_file or "").strip(),
        )
        print(descriptor_json_text(dict(emitted.get("descriptor") or {})))
        return 0

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
    elif args.cmd == "compat-status":
        result = cmd_compat_status(
            repo_root=repo_root,
            dist_root=str(args.dist),
            bundle_id=str(args.bundle),
            mod_policy_id=str(args.mod_policy_id),
            overlay_conflict_policy_id=str(args.overlay_conflict_policy_id),
            contract_bundle_path=str(args.contract_bundle_path),
        )
    elif args.cmd == "create-session":
        result = cmd_create_session(
            repo_root=repo_root,
            save_id=str(args.save_id),
            bundle_id=str(args.bundle),
            pipeline_id=str(args.pipeline_id),
            scenario_id=str(args.scenario_id),
            experience_id=str(args.experience_id),
            law_profile_id=str(args.law_profile_id),
            parameter_bundle_id=str(args.parameter_bundle_id),
            budget_policy_id=str(args.budget_policy_id),
            fidelity_policy_id=str(args.fidelity_policy_id),
            privilege_level=str(args.privilege_level),
            compile_outputs=str(args.compile_outputs).strip().lower() != "off",
        )
    else:
        parser.print_help()
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


def appshell_product_bootstrap(context: dict) -> int:
    delegate_argv = ["--repo-root", str(context.get("repo_root", ".")).replace("/", "\\")]
    delegate_argv.extend(list(context.get("delegate_argv") or []))
    return _legacy_main(delegate_argv)


def main(argv: list[str] | None = None) -> int:
    return appshell_main(
        product_id="launcher",
        argv=argv,
        repo_root_hint=REPO_ROOT_HINT,
        product_bootstrap=appshell_product_bootstrap,
    )


if __name__ == "__main__":
    raise SystemExit(main())
