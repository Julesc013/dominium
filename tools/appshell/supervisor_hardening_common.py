"""Deterministic helpers for SUPERVISOR-HARDEN-0 reporting and enforcement."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from typing import Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.appshell.paths import clear_current_virtual_paths, set_current_virtual_paths, vpath_init  # noqa: E402
from src.appshell.supervisor import SupervisorEngine, build_supervisor_run_spec, canonicalize_args  # noqa: E402
from tools.appshell.appshell6_probe import run_supervisor_probe, verify_supervisor_replay  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


SUPERVISOR_SURFACE_MAP_PATH = "docs/audit/SUPERVISOR_SURFACE_MAP.md"
LOG_MERGE_RULES_PATH = "docs/appshell/LOG_MERGE_RULES.md"
SUPERVISOR_HARDENING_FINAL_PATH = "docs/audit/SUPERVISOR_HARDENING_FINAL.md"
SUPERVISOR_HARDENING_REPORT_PATH = "data/audit/supervisor_hardening_report.json"
SUPERVISOR_HARDENING_TOOL_PATH = "tools/appshell/tool_run_supervisor_hardening.py"
SUPERVISOR_HARDENING_REPORT_ID = "appshell.supervisor_harden.v1"
LAST_REVIEWED = "2026-03-13"

SUPERVISOR_SURFACES = (
    {
        "path": "src/runtime/process_spawn.py",
        "surface": "process_spawn",
        "classification": "canonical",
        "purpose": "deterministic process spawn abstraction",
        "readiness_logic": "none",
        "attach_logic": "none",
        "log_merge_logic": "none",
        "crash_policy_logic": "none",
        "wallclock_usage": "none",
        "required_markers": ("build_python_process_spec(", "spawn_process(", "poll_process("),
    },
    {
        "path": "src/appshell/supervisor/args_canonicalizer.py",
        "surface": "args_canonicalizer",
        "classification": "canonical",
        "purpose": "stable flag ordering, quoting, and arg hashing",
        "readiness_logic": "none",
        "attach_logic": "none",
        "log_merge_logic": "none",
        "crash_policy_logic": "none",
        "wallclock_usage": "none",
        "required_markers": ("canonicalize_args(", "argv_text_hash", "_quote_arg("),
    },
    {
        "path": "src/appshell/supervisor/supervisor_engine.py",
        "surface": "supervisor_engine",
        "classification": "canonical",
        "purpose": "spawn, readiness, attach, log merge, restart, and diag capture",
        "readiness_logic": "bounded negotiated readiness",
        "attach_logic": "attach_ipc_endpoint + query_ipc_status",
        "log_merge_logic": "stable sort by source_product_id/channel_id/seq_no",
        "crash_policy_logic": "bounded restarts with iteration backoff and diag capture",
        "wallclock_usage": "none",
        "required_markers": (
            "_wait_for_endpoint_ready_process(",
            "canonicalize_args(",
            "_log_merge_sort_key(",
            "restart_backoff_remaining",
            "explain.supervisor_restart",
            "explain.supervisor_stop",
            "REFUSAL_SUPERVISOR_CHILD_NOT_READY",
        ),
    },
    {
        "path": "src/appshell/commands/command_engine.py",
        "surface": "launcher_commands",
        "classification": "canonical",
        "purpose": "launcher command entrypoints for start/status/stop/attach",
        "readiness_logic": "delegated to supervisor_engine",
        "attach_logic": "delegated to supervisor_engine",
        "log_merge_logic": "status payload only",
        "crash_policy_logic": "delegated to supervisor_engine",
        "wallclock_usage": "none",
        "required_markers": ("launch_supervisor_service(", "invoke_supervisor_service_command(", "attach_supervisor_children("),
    },
    {
        "path": "tools/appshell/supervisor_service.py",
        "surface": "supervisor_service",
        "classification": "canonical",
        "purpose": "persistent launcher-owned supervisor host",
        "readiness_logic": "engine.start + endpoint server readiness",
        "attach_logic": "AppShellIPCEndpointServer",
        "log_merge_logic": "delegated to supervisor_engine",
        "crash_policy_logic": "delegated to supervisor_engine",
        "wallclock_usage": "none",
        "required_markers": ("SupervisorEngine(", "engine.start()", "engine.wait_for_shutdown()"),
    },
    {
        "path": "tools/appshell/appshell6_probe.py",
        "surface": "runtime_probe",
        "classification": "canonical",
        "purpose": "deterministic supervisor replay probe",
        "readiness_logic": "launcher start/status/stop replay",
        "attach_logic": "attach_supervisor_children",
        "log_merge_logic": "aggregated log snapshot hash",
        "crash_policy_logic": "probe only",
        "wallclock_usage": "none",
        "required_markers": ("run_supervisor_probe(", "verify_supervisor_replay(", "aggregated_logs"),
    },
)

SCAN_FILES = (
    "src/appshell/supervisor/supervisor_engine.py",
    "src/appshell/commands/command_engine.py",
    "tools/appshell/supervisor_service.py",
    "tools/appshell/appshell6_probe.py",
)
WALLCLOCK_TOKENS = ("time.sleep(", "time.time(", "datetime.utcnow(", "perf_counter(", "monotonic(", "timeout=")
ATTACH_BYPASS_TOKENS = ("socket.socket(", "open_ipc_listener(", "connect_ipc_client(")
ATTACH_BYPASS_ALLOW = {
    "src/appshell/supervisor/supervisor_engine.py": {"attach_ipc_endpoint("},
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _write_text(path: str, text: str) -> None:
    abs_path = _norm(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    abs_path = _norm(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload or {}), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _markdown_table(headers: Iterable[str], rows: Iterable[Iterable[object]]) -> str:
    header_row = "| " + " | ".join(str(item) for item in headers) + " |"
    sep_row = "| " + " | ".join("---" for _ in headers) + " |"
    body_rows = ["| " + " | ".join(str(item) for item in row) + " |" for row in rows]
    return "\n".join([header_row, sep_row] + body_rows) if body_rows else "\n".join([header_row, sep_row])


def _doc_header(*, title: str, compatibility: str) -> str:
    return "\n".join(
        [
            "Status: CANONICAL",
            "Last Reviewed: {}".format(LAST_REVIEWED),
            "Supersedes: none",
            "Superseded By: none",
            "Version: 1.0.0",
            "Compatibility: {}".format(compatibility),
            "Stability: provisional",
            "Future Series: DOC-CONVERGENCE",
            "Replacement Target: canon-aligned documentation set for convergence and release preparation",
            "",
            "# {}".format(title),
            "",
        ]
    )


def _surface_rows(repo_root: str) -> list[dict]:
    rows: list[dict] = []
    for entry in SUPERVISOR_SURFACES:
        rel_path = str(entry.get("path", "")).strip()
        text = _read_text(repo_root, rel_path)
        missing = [token for token in list(entry.get("required_markers") or ()) if token not in text]
        rows.append(
            {
                "path": rel_path,
                "surface": str(entry.get("surface", "")).strip(),
                "classification": str(entry.get("classification", "")).strip(),
                "purpose": str(entry.get("purpose", "")).strip(),
                "readiness_logic": str(entry.get("readiness_logic", "")).strip(),
                "attach_logic": str(entry.get("attach_logic", "")).strip(),
                "log_merge_logic": str(entry.get("log_merge_logic", "")).strip(),
                "crash_policy_logic": str(entry.get("crash_policy_logic", "")).strip(),
                "wallclock_usage": str(entry.get("wallclock_usage", "")).strip(),
                "missing_markers": missing,
            }
        )
    return rows


def _wallclock_findings(repo_root: str) -> list[dict]:
    findings: list[dict] = []
    for rel_path in SCAN_FILES:
        text = _read_text(repo_root, rel_path)
        for token in WALLCLOCK_TOKENS:
            if token in text:
                findings.append(
                    {
                        "code": "wallclock_token",
                        "file_path": rel_path,
                        "message": "supervisor surface contains forbidden wall-clock token `{}`".format(token),
                    }
                )
    return findings


def _attach_bypass_findings(repo_root: str) -> list[dict]:
    findings: list[dict] = []
    for rel_path in SCAN_FILES:
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for token in ATTACH_BYPASS_TOKENS:
            if token not in text:
                continue
            allowed_markers = ATTACH_BYPASS_ALLOW.get(rel_path, set())
            if any(marker in text for marker in allowed_markers):
                continue
            findings.append(
                {
                    "code": "attach_bypass_token",
                    "file_path": rel_path,
                    "message": "supervisor surface contains low-level IPC token `{}` outside the canonical attach path".format(token),
                }
            )
    return findings


def _log_merge_findings(repo_root: str) -> list[dict]:
    findings: list[dict] = []
    engine_text = _read_text(repo_root, "src/appshell/supervisor/supervisor_engine.py")
    required = (
        "\"channel_id\": \"log\"",
        "key=_log_merge_sort_key",
        "str(row_map.get(\"channel_id\", \"\")).strip()",
    )
    missing = [token for token in required if token not in engine_text]
    if missing:
        findings.append(
            {
                "code": "log_merge_rule_missing",
                "file_path": "src/appshell/supervisor/supervisor_engine.py",
                "message": "supervisor log merge is missing stable merge markers: {}".format(", ".join(missing)),
            }
        )
    return findings


def _sample_canonical_args() -> dict:
    return canonicalize_args(
        positional=["tools/appshell/supervisor_service.py"],
        flag_pairs=(
            ("--topology", "singleplayer"),
            ("--seed", "seed.sample"),
            ("--repo-root", "."),
            ("--contract-bundle-hash", "0" * 64),
        ),
    )


def _portable_installed_parity(repo_root: str) -> dict:
    actual_repo_root = _norm(repo_root)
    template_abs = os.path.join(actual_repo_root, "data", "session_templates", "session.mvp_default.json")
    profile_abs = os.path.join(actual_repo_root, "dist", "profiles", "bundle.mvp_default.json")
    pack_lock_abs = os.path.join(actual_repo_root, "dist", "locks", "pack_lock.mvp_default.json")
    registry_src = os.path.join(actual_repo_root, "data", "registries", "supervisor_policy_registry.json")
    vroot_registry_src = os.path.join(actual_repo_root, "data", "registries", "virtual_root_registry.json")
    temp_parent = os.path.join(actual_repo_root, "build", "tmp")
    os.makedirs(temp_parent, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dominium.supervisor.harden.", dir=temp_parent) as temp_root:
        temp_repo_root = os.path.join(temp_root, "repo")
        portable_root = os.path.join(temp_root, "portable")
        installed_root = os.path.join(temp_root, "installs", "primary")
        os.makedirs(os.path.join(temp_repo_root, "data", "registries"), exist_ok=True)
        os.makedirs(portable_root, exist_ok=True)
        os.makedirs(installed_root, exist_ok=True)
        shutil.copyfile(registry_src, os.path.join(temp_repo_root, "data", "registries", "supervisor_policy_registry.json"))
        shutil.copyfile(vroot_registry_src, os.path.join(temp_repo_root, "data", "registries", "virtual_root_registry.json"))
        _write_json(
            os.path.join(portable_root, "install.manifest.json"),
            {
                "schema_version": "1.0.0",
                "install_id": "install.portable.supervisor",
                "install_version": "0.0.0",
                "store_root_ref": {"root_path": "."},
                "semantic_contract_registry_hash": "0" * 64,
            },
        )
        os.makedirs(os.path.join(temp_root, "installs", "store"), exist_ok=True)
        _write_json(
            os.path.join(installed_root, "install.manifest.json"),
            {
                "schema_version": "1.0.0",
                "install_id": "install.registry.supervisor",
                "install_version": "0.0.0",
                "store_root_ref": {"root_path": "../store"},
                "semantic_contract_registry_hash": "0" * 64,
            },
        )
        _write_json(
            os.path.join(temp_repo_root, "data", "registries", "install_registry.json"),
            {
                "schema_id": "dominium.registry.install_registry",
                "schema_version": "1.0.0",
                "record": {
                    "registry_id": "dominium.registry.install_registry",
                    "registry_version": "1.0.0",
                    "installs": [
                        {
                            "install_id": "install.registry.supervisor",
                            "path": "../../installs/primary",
                            "version": "0.0.0",
                            "contract_registry_hash": "0" * 64,
                        }
                    ],
                },
            },
        )
        try:
            portable_context = vpath_init(
                {
                    "repo_root": temp_repo_root,
                    "product_id": "launcher",
                    "raw_args": ["--install-root", portable_root],
                    "executable_path": os.path.join(portable_root, "dominium_launcher"),
                }
            )
            set_current_virtual_paths(portable_context)
            portable_spec = build_supervisor_run_spec(
                repo_root=temp_repo_root,
                seed="seed.supervisor.portable",
                session_template_path=template_abs,
                profile_bundle_path=profile_abs,
                pack_lock_path=pack_lock_abs,
                topology="server_only",
            )
            clear_current_virtual_paths()
            installed_context = vpath_init(
                {
                    "repo_root": temp_repo_root,
                    "product_id": "launcher",
                    "raw_args": ["--install-id", "install.registry.supervisor"],
                    "executable_path": os.path.join(temp_root, "bin", "dominium_launcher"),
                }
            )
            set_current_virtual_paths(installed_context)
            installed_spec = build_supervisor_run_spec(
                repo_root=temp_repo_root,
                seed="seed.supervisor.installed",
                session_template_path=template_abs,
                profile_bundle_path=profile_abs,
                pack_lock_path=pack_lock_abs,
                topology="server_only",
            )
            clear_current_virtual_paths()
        finally:
            clear_current_virtual_paths()
        outputs = {
            "portable": {
                "vpath_result": _token(portable_context.get("result")),
                "resolution_source": _token(portable_context.get("resolution_source")),
                "run_spec_result": _token(portable_spec.get("result")),
                "runtime_paths": dict(portable_spec.get("runtime_paths") or {}),
            },
            "installed": {
                "vpath_result": _token(installed_context.get("result")),
                "resolution_source": _token(installed_context.get("resolution_source")),
                "run_spec_result": _token(installed_spec.get("result")),
                "runtime_paths": dict(installed_spec.get("runtime_paths") or {}),
            },
        }
        outputs["deterministic_fingerprint"] = canonical_sha256(outputs)
        return outputs


def _crash_policy_probe(repo_root: str) -> dict:
    repo_root_abs = _norm(repo_root)
    lab_spec = build_supervisor_run_spec(
        repo_root=repo_root_abs,
        seed="seed.supervisor.crash.lab",
        supervisor_policy_id="supervisor.policy.lab",
        topology="server_only",
    )
    if _token(lab_spec.get("result")) != "complete":
        return {"result": "refused", "reason": "lab_run_spec_failed", "details": lab_spec}
    default_spec = build_supervisor_run_spec(
        repo_root=repo_root_abs,
        seed="seed.supervisor.crash.default",
        supervisor_policy_id="supervisor.policy.default",
        topology="server_only",
    )
    if _token(default_spec.get("result")) != "complete":
        return {"result": "refused", "reason": "default_run_spec_failed", "details": default_spec}

    lab_engine = SupervisorEngine(repo_root=repo_root_abs, run_spec=lab_spec)
    default_engine = SupervisorEngine(repo_root=repo_root_abs, run_spec=default_spec)
    lab_summary = {}
    default_summary = {}
    try:
        lab_started = lab_engine.start()
        if _token(lab_started.get("result")) != "complete":
            return {"result": "refused", "reason": "lab_start_failed", "details": lab_started}
        lab_process = lab_engine._process_handles.get("server")
        if lab_process is None or getattr(lab_process, "stdin", None) is None:
            return {"result": "refused", "reason": "lab_stdin_missing"}
        lab_process.stdin.write("crash\n")
        lab_process.stdin.flush()
        first_refresh = lab_engine.refresh()
        second_refresh = lab_engine.refresh()
        third_refresh = lab_engine.refresh()
        first_row = dict((dict(first_refresh.get("state") or {}).get("processes") or [{}])[0])
        second_row = dict((dict(second_refresh.get("state") or {}).get("processes") or [{}])[0])
        third_row = dict((dict(third_refresh.get("state") or {}).get("processes") or [{}])[0])
        lab_summary = {
            "after_first_refresh_status": str(first_row.get("status", "")).strip(),
            "after_second_refresh_status": str(second_row.get("status", "")).strip(),
            "after_third_refresh_status": str(third_row.get("status", "")).strip(),
            "restart_count": int(third_row.get("restart_count", 0) or 0),
            "restart_backoff_remaining": int(third_row.get("restart_backoff_remaining", 0) or 0),
            "diag_bundle_dir": str(first_row.get("diag_bundle_dir", "")).strip(),
        }
    finally:
        try:
            lab_engine.stop()
        except Exception:
            pass

    try:
        default_started = default_engine.start()
        if _token(default_started.get("result")) != "complete":
            return {"result": "refused", "reason": "default_start_failed", "details": default_started}
        default_process = default_engine._process_handles.get("server")
        if default_process is None or getattr(default_process, "stdin", None) is None:
            return {"result": "refused", "reason": "default_stdin_missing"}
        default_process.stdin.write("crash\n")
        default_process.stdin.flush()
        default_first_refresh = default_engine.refresh()
        default_second_refresh = default_engine.refresh()
        default_third_refresh = default_engine.refresh()
        default_first_row = dict((dict(default_first_refresh.get("state") or {}).get("processes") or [{}])[0])
        default_second_row = dict((dict(default_second_refresh.get("state") or {}).get("processes") or [{}])[0])
        default_row = dict((dict(default_third_refresh.get("state") or {}).get("processes") or [{}])[0])
        default_summary = {
            "after_first_refresh_status": str(default_first_row.get("status", "")).strip(),
            "after_second_refresh_status": str(default_second_row.get("status", "")).strip(),
            "status": str(default_row.get("status", "")).strip(),
            "restart_count": int(default_row.get("restart_count", 0) or 0),
            "restart_backoff_remaining": int(default_row.get("restart_backoff_remaining", 0) or 0),
            "diag_bundle_dir": str(default_second_row.get("diag_bundle_dir", "")).strip() or str(default_row.get("diag_bundle_dir", "")).strip(),
        }
    finally:
        try:
            default_engine.stop()
        except Exception:
            pass

    return {
        "result": "complete",
        "lab_policy": lab_summary,
        "default_policy": default_summary,
        "deterministic_fingerprint": canonical_sha256({"lab": lab_summary, "default": default_summary}),
    }


def build_supervisor_hardening_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    surface_rows = _surface_rows(root)
    runtime_probe = run_supervisor_probe(root, suffix="supervisor_harden", topology="singleplayer", supervisor_policy_id="supervisor.policy.lab")
    replay_probe = verify_supervisor_replay(root, suffix="supervisor_harden")
    crash_policy_probe = _crash_policy_probe(root)
    parity_probe = _portable_installed_parity(root)
    sample_args = _sample_canonical_args()
    violations = []
    for row in surface_rows:
        if row["missing_markers"]:
            violations.append(
                {
                    "code": "surface_markers_missing",
                    "file_path": row["path"],
                    "message": "required supervisor hardening markers are missing: {}".format(", ".join(row["missing_markers"])),
                }
            )
    violations.extend(_wallclock_findings(root))
    violations.extend(_log_merge_findings(root))
    violations.extend(_attach_bypass_findings(root))
    if _token(runtime_probe.get("result")) != "complete":
        violations.append(
            {
                "code": "runtime_probe_failed",
                "file_path": "tools/appshell/appshell6_probe.py",
                "message": "supervisor runtime probe did not complete",
            }
        )
    if _token(replay_probe.get("result")) != "complete":
        violations.append(
            {
                "code": "replay_probe_failed",
                "file_path": "tools/appshell/tool_replay_supervisor.py",
                "message": "supervisor replay probe did not complete",
            }
        )
    if _token(crash_policy_probe.get("result")) != "complete":
        violations.append(
            {
                "code": "crash_policy_probe_failed",
                "file_path": "src/appshell/supervisor/supervisor_engine.py",
                "message": "supervisor crash policy probe did not complete",
            }
        )
    else:
        lab_policy = dict(crash_policy_probe.get("lab_policy") or {})
        default_policy = dict(crash_policy_probe.get("default_policy") or {})
        if str(lab_policy.get("after_second_refresh_status", "")).strip() != "restart_pending":
            violations.append(
                {
                    "code": "restart_backoff_missing",
                    "file_path": "src/appshell/supervisor/supervisor_engine.py",
                    "message": "lab policy did not enter restart_pending on the bounded crash refresh sequence",
                }
            )
        if int(lab_policy.get("restart_count", 0) or 0) < 1 or str(lab_policy.get("after_third_refresh_status", "")).strip() != "running":
            violations.append(
                {
                    "code": "restart_policy_not_applied",
                    "file_path": "src/appshell/supervisor/supervisor_engine.py",
                    "message": "lab policy did not restart the crashed child after deterministic backoff",
                }
            )
        if int(default_policy.get("restart_count", 0) or 0) != 0 or str(default_policy.get("status", "")).strip() == "running":
            violations.append(
                {
                    "code": "restart_policy_bypassed",
                    "file_path": "src/appshell/supervisor/supervisor_engine.py",
                    "message": "default policy did not leave the crashed child exited within the bounded refresh sequence",
                }
            )
    report = {
        "schema_version": "1.0.0",
        "report_id": SUPERVISOR_HARDENING_REPORT_ID,
        "repo_root": root.replace("\\", "/"),
        "surface_rows": surface_rows,
        "runtime_probe": runtime_probe,
        "replay_probe": replay_probe,
        "crash_policy_probe": crash_policy_probe,
        "portable_installed_parity": parity_probe,
        "sample_args": sample_args,
        "violations": sorted(
            [dict(row) for row in violations],
            key=lambda row: (str(row.get("file_path", "")), str(row.get("code", "")), str(row.get("message", ""))),
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    report["result"] = "complete" if not report["violations"] else "refused"
    return report


def supervisor_hardening_violations(repo_root: str) -> list[dict]:
    return list(build_supervisor_hardening_report(repo_root).get("violations") or [])


def _render_surface_map(report: Mapping[str, object]) -> str:
    surface_rows = list(report.get("surface_rows") or [])
    rows = [
        (
            str(row.get("surface", "")).strip(),
            str(row.get("path", "")).strip(),
            str(row.get("classification", "")).strip(),
            str(row.get("purpose", "")).strip(),
            str(row.get("readiness_logic", "")).strip(),
            str(row.get("attach_logic", "")).strip(),
            str(row.get("log_merge_logic", "")).strip(),
            str(row.get("crash_policy_logic", "")).strip(),
            str(row.get("wallclock_usage", "")).strip(),
        )
        for row in surface_rows
    ]
    return "\n".join(
        [
            _doc_header(
                title="Supervisor Surface Map",
                compatibility="Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/SUPERVISOR_MODEL.md`, `docs/appshell/IPC_DISCOVERY.md`, and `docs/appshell/IPC_ATTACH_CONSOLES.md`.",
            ),
            "## Inventory",
            "",
            _markdown_table(
                (
                    "Surface",
                    "Path",
                    "Class",
                    "Purpose",
                    "Readiness",
                    "Attach",
                    "Log Merge",
                    "Crash Policy",
                    "Wallclock",
                ),
                rows,
            ),
            "",
            "## Notes",
            "",
            "- Process spawning is centralized in `src/runtime/process_spawn.py`.",
            "- Readiness is driven by child ready handshakes plus bounded negotiated IPC attach/status verification.",
            "- Log aggregation is stable by `(source_product_id, channel_id, seq_no, endpoint_id, event_id)`.",
            "- Crash handling captures a diag bundle before restart decisions are evaluated.",
            "",
        ]
    )


def _render_log_merge_rules(report: Mapping[str, object]) -> str:
    sample = dict(report.get("sample_args") or {})
    return "\n".join(
        [
            _doc_header(
                title="Log Merge Rules",
                compatibility="Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/LOGGING_AND_TRACING.md`, and `docs/appshell/SUPERVISOR_MODEL.md`.",
            ),
            "## Canonical Merge Key",
            "",
            "Supervisor log aggregation merges rows in ascending order by:",
            "",
            "1. `source_product_id`",
            "2. `channel_id`",
            "3. `seq_no`",
            "4. `endpoint_id`",
            "5. `event_id`",
            "",
            "Arrival timing must never affect the merged order.",
            "",
            "## Channel Discipline",
            "",
            "- Aggregated child log rows carry `channel_id = log`.",
            "- `seq_no` remains monotonic within each channel.",
            "- Truncation keeps the last 128 rows after deterministic sorting, not after arrival-order append.",
            "",
            "## Canonical Args Reference",
            "",
            "- Sample `args_hash`: `{}`".format(_token(sample.get("args_hash"))),
            "- Sample `argv_text_hash`: `{}`".format(_token(sample.get("argv_text_hash"))),
            "",
        ]
    )


def _render_final_report(report: Mapping[str, object]) -> str:
    runtime_probe = dict(report.get("runtime_probe") or {})
    replay_probe = dict(report.get("replay_probe") or {})
    crash_policy = dict(report.get("crash_policy_probe") or {})
    parity = dict(report.get("portable_installed_parity") or {})
    violations = list(report.get("violations") or [])
    return "\n".join(
        [
            _doc_header(
                title="Supervisor Hardening Final",
                compatibility="Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/SUPERVISOR_MODEL.md`, `docs/appshell/IPC_DISCOVERY.md`, `docs/appshell/LOGGING_AND_TRACING.md`, and `docs/diag/REPRO_BUNDLE.md`.",
            ),
            "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
            "",
            "## Removed Wall-Clock Usage",
            "",
            "- No `sleep`, `time`, `datetime`, or timeout-driven readiness loops remain in the hardened supervisor surfaces.",
            "- Readiness now relies on deterministic ready handshakes plus bounded negotiated attach/status checks.",
            "",
            "## Canonical Arg Rules",
            "",
            "- Long flags are serialized in stable lexical order through `src/appshell/supervisor/args_canonicalizer.py`.",
            "- Canonical argv text uses deterministic JSON quoting for whitespace and escape-sensitive tokens.",
            "- Each supervised process row records `args_hash` and `argv_text_hash` in the run manifest.",
            "",
            "## Crash Handling",
            "",
            "- `supervisor.policy.default`: no restart; crash captures a diag bundle and leaves the child exited.",
            "- `supervisor.policy.lab`: bounded restart with deterministic iteration backoff before respawn.",
            "- `explain.supervisor_restart` and `explain.supervisor_stop` are emitted through the shared log engine.",
            "",
            "## Runtime Verification",
            "",
            "- Runtime probe result: `{}`".format(_token(runtime_probe.get("result"))),
            "- Replay probe result: `{}`".format(_token(replay_probe.get("result"))),
            "- Crash policy probe result: `{}`".format(_token(crash_policy.get("result"))),
            "- Portable/installed parity fingerprint: `{}`".format(_token(parity.get("deterministic_fingerprint"))),
            "",
            "## Violations",
            "",
            "- Count: `{}`".format(len(violations)),
            "- Remaining items: {}".format("none" if not violations else "; ".join(str(dict(row).get("code", "")).strip() for row in violations)),
            "",
            "## Readiness",
            "",
            "- Ready for `RESTRUCTURE-PREP-0` and `CONVERGENCE-GATE-0` once full-repo strict lanes are rerun.",
            "",
        ]
    )


def write_supervisor_hardening_outputs(repo_root: str, report: Mapping[str, object]) -> list[str]:
    root = _norm(repo_root)
    outputs = {
        SUPERVISOR_SURFACE_MAP_PATH: _render_surface_map(report),
        LOG_MERGE_RULES_PATH: _render_log_merge_rules(report),
        SUPERVISOR_HARDENING_FINAL_PATH: _render_final_report(report),
    }
    written: list[str] = []
    for rel_path, text in outputs.items():
        _write_text(os.path.join(root, rel_path.replace("/", os.sep)), text)
        written.append(rel_path)
    _write_json(os.path.join(root, SUPERVISOR_HARDENING_REPORT_PATH.replace("/", os.sep)), dict(report or {}))
    written.append(SUPERVISOR_HARDENING_REPORT_PATH)
    return written


__all__ = [
    "LOG_MERGE_RULES_PATH",
    "SUPERVISOR_HARDENING_FINAL_PATH",
    "SUPERVISOR_HARDENING_REPORT_PATH",
    "SUPERVISOR_HARDENING_TOOL_PATH",
    "SUPERVISOR_SURFACE_MAP_PATH",
    "build_supervisor_hardening_report",
    "supervisor_hardening_violations",
    "write_supervisor_hardening_outputs",
]
