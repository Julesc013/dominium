"""AppShell adapters for offline pack verification surfaces."""

from __future__ import annotations

import os

from src.appshell.paths import VROOT_STORE, get_current_virtual_paths, vpath_root
from src.packs.compat import verify_pack_set, write_pack_compatibility_outputs


def verify_pack_root(
    *,
    repo_root: str,
    root: str,
    bundle_id: str,
    mod_policy_id: str,
    overlay_conflict_policy_id: str,
    contract_bundle_path: str,
    out_report: str = "",
    out_lock: str = "",
    write_outputs: bool = False,
) -> dict:
    context = get_current_virtual_paths()
    if str(root or "").strip():
        base_root = str(root or "").strip()
        target_root = os.path.normpath(os.path.abspath(base_root if os.path.isabs(base_root) else os.path.join(repo_root, base_root)))
    elif context is not None and str(context.get("result", "")).strip() == "complete":
        target_root = vpath_root(VROOT_STORE, context)
    else:
        target_root = os.path.normpath(os.path.abspath(os.path.join(repo_root, "dist")))
    schema_root = target_root if os.path.isdir(os.path.join(target_root, "schemas")) else repo_root
    result = verify_pack_set(
        repo_root=target_root,
        bundle_id=str(bundle_id).strip(),
        mod_policy_id=str(mod_policy_id).strip() or "mod_policy.lab",
        overlay_conflict_policy_id=str(overlay_conflict_policy_id).strip(),
        schema_repo_root=schema_root,
        universe_contract_bundle_path=str(contract_bundle_path).strip(),
    )
    if bool(write_outputs) and str(result.get("result", "")) == "complete":
        written = write_pack_compatibility_outputs(
            report_path=str(out_report or "").strip(),
            report_payload=dict(result.get("report") or {}),
            pack_lock_path=str(out_lock or "").strip(),
            pack_lock_payload=dict(result.get("pack_lock") or {}) or None,
        )
        result["written_report_path"] = str(written.get("report_path", "")).strip()
        result["written_lock_path"] = str(written.get("pack_lock_path", "")).strip()
    return {
        "result": str(result.get("result", "refused")),
        "dist_root": target_root.replace("\\", "/"),
        "report": dict(result.get("report") or {}),
        "pack_lock": dict(result.get("pack_lock") or {}),
        "warnings": list(result.get("warnings") or []),
        "errors": list(result.get("errors") or []),
        "written_report_path": str(result.get("written_report_path", "")).replace("\\", "/"),
        "written_lock_path": str(result.get("written_lock_path", "")).replace("\\", "/"),
    }


__all__ = ["verify_pack_root"]
