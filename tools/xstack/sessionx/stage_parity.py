"""CLI/TUI/GUI stage parity adapters over shared session-control execution."""

from __future__ import annotations

from typing import Dict

from .common import refusal
from .session_control import abort_session_spec, compact_session_save, resume_session_spec, session_stage_status


SUPPORTED_SURFACES = ("cli", "tui", "gui")


def _validate_surface(surface: str) -> Dict[str, object]:
    token = str(surface).strip().lower()
    if token in SUPPORTED_SURFACES:
        return {"result": "complete", "surface": token}
    return refusal(
        "PROCESS_INPUT_INVALID",
        "unsupported session surface '{}'".format(token or "<empty>"),
        "Use one of cli|tui|gui.",
        {"surface": token or "<empty>"},
        "$.surface",
    )


def _workspace_payload(surface: str, payload: Dict[str, object]) -> Dict[str, object]:
    result = dict(payload)
    result["surface"] = str(surface)
    if str(payload.get("result", "")) == "complete":
        result["workspace"] = {
            "surface": str(surface),
            "stage_id": str(payload.get("current_stage_id", payload.get("last_stage_id", ""))),
            "stage_log": list(payload.get("stage_log") or []),
            "refusal_codes": list(payload.get("refusal_codes") or []),
        }
    return result


def surface_stage_status(surface: str, repo_root: str, session_spec_path: str) -> Dict[str, object]:
    checked = _validate_surface(surface)
    if checked.get("result") != "complete":
        return checked
    payload = session_stage_status(repo_root=repo_root, session_spec_path=session_spec_path)
    return _workspace_payload(surface=str(checked.get("surface", "")), payload=payload)


def surface_abort_session(surface: str, repo_root: str, session_spec_path: str, stage_id: str = "", reason: str = "manual_abort") -> Dict[str, object]:
    checked = _validate_surface(surface)
    if checked.get("result") != "complete":
        return checked
    payload = abort_session_spec(
        repo_root=repo_root,
        session_spec_path=session_spec_path,
        stage_id=stage_id,
        reason=reason,
    )
    return _workspace_payload(surface=str(checked.get("surface", "")), payload=payload)


def surface_resume_session(
    surface: str,
    repo_root: str,
    session_spec_path: str,
    bundle_id: str = "",
    lockfile_path: str = "",
    registries_dir: str = "",
) -> Dict[str, object]:
    checked = _validate_surface(surface)
    if checked.get("result") != "complete":
        return checked
    payload = resume_session_spec(
        repo_root=repo_root,
        session_spec_path=session_spec_path,
        bundle_id=bundle_id,
        lockfile_path=lockfile_path,
        registries_dir=registries_dir,
    )
    return _workspace_payload(surface=str(checked.get("surface", "")), payload=payload)


def surface_compact_session(
    surface: str,
    repo_root: str,
    session_spec_path: str,
    compaction_policy_id: str,
) -> Dict[str, object]:
    checked = _validate_surface(surface)
    if checked.get("result") != "complete":
        return checked
    payload = compact_session_save(
        repo_root=repo_root,
        session_spec_path=session_spec_path,
        compaction_policy_id=compaction_policy_id,
    )
    return _workspace_payload(surface=str(checked.get("surface", "")), payload=payload)
