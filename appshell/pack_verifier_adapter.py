"""AppShell adapters for offline pack verification surfaces."""

from __future__ import annotations

import os

from appshell.paths import VROOT_STORE, get_current_virtual_paths, vpath_root
from packs.compat import verify_pack_set, write_pack_compatibility_outputs
from security.trust import (
    ARTIFACT_KIND_PACK,
    ARTIFACT_KIND_PACK_COMPAT,
    effective_trust_policy_id,
    verify_artifact_trust,
)


def verify_pack_root(
    *,
    repo_root: str,
    root: str,
    bundle_id: str,
    mod_policy_id: str,
    overlay_conflict_policy_id: str,
    contract_bundle_path: str,
    trust_policy_id: str = "",
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
    packs_root_rel = "packs"
    bundles_root_rel = "bundles"
    if os.path.isdir(os.path.join(target_root, "store", "packs")):
        packs_root_rel = "store/packs"
    if os.path.isdir(os.path.join(target_root, "store", "bundles")):
        bundles_root_rel = "store/bundles"
    schema_root = target_root if os.path.isdir(os.path.join(target_root, "schemas")) else repo_root
    result = verify_pack_set(
        repo_root=target_root,
        bundle_id=str(bundle_id).strip(),
        mod_policy_id=str(mod_policy_id).strip() or "mod_policy.lab",
        overlay_conflict_policy_id=str(overlay_conflict_policy_id).strip(),
        schema_repo_root=schema_root,
        packs_root_rel=packs_root_rel,
        bundles_root_rel=bundles_root_rel,
        universe_contract_bundle_path=str(contract_bundle_path).strip(),
    )
    effective_policy_id = effective_trust_policy_id(
        requested_trust_policy_id=trust_policy_id,
        install_manifest={},
        mod_policy_id=str(mod_policy_id or "").strip(),
    )
    trust_rows: list[dict] = []
    trust_errors: list[dict] = []
    trust_warnings: list[dict] = []
    if str(result.get("result", "")) == "complete":
        for row in list(dict(result.get("report") or {}).get("pack_list") or []):
            pack_row = dict(row or {})
            for artifact_kind, content_hash in (
                (ARTIFACT_KIND_PACK, str(pack_row.get("canonical_hash", "")).strip()),
                (ARTIFACT_KIND_PACK_COMPAT, str(pack_row.get("compat_manifest_hash", "")).strip()),
            ):
                trust_report = verify_artifact_trust(
                    artifact_kind=artifact_kind,
                    content_hash=content_hash,
                    trust_policy_id=effective_policy_id,
                    repo_root=repo_root,
                    install_root=target_root,
                    trust_level_id=str(pack_row.get("trust_level_id", "")).strip(),
                )
                trust_rows.append(
                    {
                        "artifact_kind": artifact_kind,
                        "pack_id": str(pack_row.get("pack_id", "")).strip(),
                        "trust_report": trust_report,
                    }
                )
                if str(trust_report.get("result", "")) == "refused":
                    trust_errors.append(
                        {
                            "code": str(trust_report.get("refusal_code", "")).strip() or "refusal.pack.trust_denied",
                            "path": str(pack_row.get("pack_id", "")).strip() or "pack_list",
                            "message": str(trust_report.get("reason", "")).strip() or "trust policy refused the pack artifact",
                        }
                    )
                for warning in list(trust_report.get("warnings") or []):
                    warning_row = dict(warning or {})
                    trust_warnings.append(
                        {
                            "code": str(warning_row.get("code", "")).strip() or "warn.trust.signature_missing",
                            "path": str(pack_row.get("pack_id", "")).strip() or "pack_list",
                            "message": str(warning_row.get("message", "")).strip() or "trust policy warning",
                        }
                    )
        if trust_errors:
            result = dict(result)
            result["result"] = "refused"
    combined_warnings = list(result.get("warnings") or []) + trust_warnings
    combined_errors = list(result.get("errors") or []) + trust_errors
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
        "packs_root_rel": packs_root_rel,
        "bundles_root_rel": bundles_root_rel,
        "report": dict(result.get("report") or {}),
        "pack_lock": dict(result.get("pack_lock") or {}),
        "trust_policy_id": effective_policy_id,
        "trust_rows": trust_rows,
        "warnings": combined_warnings,
        "errors": combined_errors,
        "written_report_path": str(result.get("written_report_path", "")).replace("\\", "/"),
        "written_lock_path": str(result.get("written_lock_path", "")).replace("\\", "/"),
    }


__all__ = ["verify_pack_root"]
