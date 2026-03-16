"""Deterministic DIST-5 UX smoke helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.appshell.rendered_stub import build_rendered_stub
from src.appshell.tui.tui_engine import build_tui_surface, render_tui_text
from tools.appshell.tool_generate_command_docs import generate_cli_reference
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


UX_POLISH_CRITERIA_PATH = "docs/release/UX_POLISH_CRITERIA.md"
CLI_REFERENCE_PATH = "docs/appshell/CLI_REFERENCE.md"
DIST5_UX_SMOKE_DOC_PATH = "docs/audit/DIST5_UX_SMOKE.md"
DIST5_UX_SMOKE_JSON_PATH = "data/audit/dist5_ux_smoke.json"
DIST5_FINAL_PATH = "docs/audit/DIST5_UX_POLISH_FINAL.md"
DIST5_REPORT_ID = "dist5.ux_smoke.v1"
RULE_REMEDIATION_ID = "INV-REFUSALS-MUST-HAVE-REMEDIATION"
RULE_HELP_ID = "INV-HELP-TEXT-REGISTERED"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _repo_rel(path: str, repo_root: str) -> str:
    abs_path = _norm(path)
    root = _norm(repo_root)
    try:
        rel_path = os.path.relpath(abs_path, root)
    except ValueError:
        return abs_path.replace("\\", "/")
    if rel_path.startswith(".."):
        return abs_path.replace("\\", "/")
    return rel_path.replace("\\", "/")


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _extract_json_objects(text: str) -> list[dict]:
    rows: list[dict] = []
    decoder = json.JSONDecoder()
    remaining = str(text or "").lstrip()
    while remaining:
        try:
            payload, index = decoder.raw_decode(remaining)
        except ValueError:
            newline_index = remaining.find("\n")
            if newline_index < 0:
                break
            remaining = remaining[newline_index + 1 :].lstrip()
            continue
        if isinstance(payload, Mapping):
            rows.append(dict(payload))
        remaining = remaining[index:].lstrip()
    return rows


def _first_payload_json(stdout: str, stderr: str) -> dict:
    for row in _extract_json_objects(stdout) + _extract_json_objects(stderr):
        row_map = dict(row or {})
        if row_map and "event_id" not in row_map:
            return row_map
    return {}


def _run_subprocess(repo_root: str, argv: Sequence[str]) -> dict:
    proc = subprocess.run(
        [sys.executable] + [str(item) for item in list(argv or [])],
        cwd=_norm(repo_root),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    stdout = str(proc.stdout or "")
    stderr = str(proc.stderr or "")
    return {
        "argv": [str(item) for item in list(argv or [])],
        "returncode": int(proc.returncode or 0),
        "stdout": stdout,
        "stderr": stderr,
        "payload": _first_payload_json(stdout, stderr),
    }


def _run_wrapper(repo_root: str, bin_name: str, argv: Sequence[str]) -> dict:
    wrapper_path = os.path.join(_norm(repo_root), "dist", "bin", _token(bin_name))
    return _run_subprocess(repo_root, [wrapper_path] + list(argv or []))


def _help_rows(repo_root: str) -> list[dict]:
    from tools.xstack.testx.tests.cap_neg1_testlib import product_bin_map

    rows: list[dict] = []
    for bin_name, product_id in sorted(product_bin_map(repo_root).items()):
        first = _run_wrapper(repo_root, bin_name, ["help"])
        second = _run_wrapper(repo_root, bin_name, ["help"])
        first_text = str(first.get("stdout", "")).replace("\r\n", "\n")
        second_text = str(second.get("stdout", "")).replace("\r\n", "\n")
        rows.append(
            {
                "bin_name": _token(bin_name),
                "product_id": _token(product_id),
                "returncode": int(first.get("returncode", 0)),
                "stable_across_runs": first_text == second_text,
                "contains_tip": "tip: use `help <topic>`" in first_text,
                "contains_examples": "examples:" in first_text.lower(),
                "contains_console": "console enter" in first_text,
                "contains_verify": "packs verify" in first_text,
                "stdout_fingerprint": canonical_sha256({"stdout": first_text}),
            }
        )
    return rows


def _refusal_rows(repo_root: str) -> list[dict]:
    rows = []
    client_refusal = _run_wrapper(
        repo_root,
        "dominium_client",
        ["compat-status", "--peer-descriptor-file", "build/tmp/missing_descriptor.json"],
    )
    launcher_refusal = _run_subprocess(repo_root, ["tools/launcher/launch.py", "install", "status"])
    for surface_id, report in (
        ("client.compat_status.invalid_peer", client_refusal),
        ("launcher.install_status.missing_install", launcher_refusal),
    ):
        payload = dict(report.get("payload") or {})
        row = {
            "surface_id": surface_id,
            "returncode": int(report.get("returncode", 0)),
            "result": _token(payload.get("result")),
            "refusal_code": _token(payload.get("refusal_code")) or _token(dict(payload.get("refusal") or {}).get("reason_code")),
            "reason": _token(payload.get("reason")) or _token(dict(payload.get("refusal") or {}).get("message")),
            "remediation_hint": _token(payload.get("remediation_hint")) or _token(dict(payload.get("refusal") or {}).get("remediation_hint")),
            "has_errors": bool(list(payload.get("errors") or [])),
            "payload_fingerprint": canonical_sha256(payload or {"result": "missing"}),
        }
        rows.append(row)
    return rows


def _status_rows(repo_root: str) -> list[dict]:
    rows = []
    probes = (
        ("client.compat_status", _run_wrapper(repo_root, "dominium_client", ["compat-status", "--mode", "cli"]), False),
        ("launcher.install_status", _run_subprocess(repo_root, ["tools/launcher/launch.py", "install", "status", "--json"]), True),
        ("setup.install_status", _run_subprocess(repo_root, ["tools/setup/setup_cli.py", "install", "status", "--json"]), True),
    )
    for surface_id, report, json_requested in probes:
        payload = dict(report.get("payload") or {})
        rows.append(
            {
                "surface_id": surface_id,
                "json_requested": bool(json_requested),
                "returncode": int(report.get("returncode", 0)),
                "payload_present": bool(payload),
                "result": _token(payload.get("result")),
                "message": _token(payload.get("message")),
                "has_summary": isinstance(payload.get("summary"), Mapping),
                "payload_fingerprint": canonical_sha256(payload or {"result": "missing"}),
            }
        )
    return rows


def _tui_probe(repo_root: str) -> dict:
    payload = build_tui_surface(repo_root, product_id="launcher")
    rendered = render_tui_text(payload)
    panel_ids = sorted(_token(row.get("panel_id")) for row in list(payload.get("panels") or []) if _token(dict(row).get("panel_id")))
    return {
        "backend_id": _token(payload.get("backend_id")),
        "effective_mode_id": _token(payload.get("effective_mode_id")),
        "show_help": bool(payload.get("show_help")),
        "help_lines": [str(item) for item in list(payload.get("help_lines") or [])],
        "panel_ids": panel_ids,
        "text_fingerprint": canonical_sha256({"text": rendered}),
        "payload_fingerprint": canonical_sha256(payload),
    }


def _rendered_probe() -> dict:
    payload = build_rendered_stub("client")
    quick_actions = sorted(_token(dict(row).get("label")) for row in list(payload.get("quick_actions") or []) if _token(dict(row).get("label")))
    return {
        "result": _token(payload.get("result")),
        "status": _token(payload.get("status")),
        "menu_title": _token(payload.get("menu_title")),
        "console_overlay_available": bool(payload.get("console_overlay_available")),
        "teleport_menu_available": bool(payload.get("teleport_menu_available")),
        "inspect_hotkey": _token(payload.get("inspect_hotkey")),
        "quick_actions": quick_actions,
        "payload_fingerprint": canonical_sha256(payload),
    }


def build_ux_smoke_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    help_rows = _help_rows(root)
    refusal_rows = _refusal_rows(root)
    status_rows = _status_rows(root)
    tui_probe = _tui_probe(root)
    rendered_probe = _rendered_probe()
    cli_reference_text = ""
    cli_reference_error = ""
    try:
        cli_reference_text = generate_cli_reference(root)
    except ValueError as exc:
        cli_reference_error = _token(exc)

    violations: list[dict] = []
    for row in help_rows:
        if int(row.get("returncode", 0)) != 0:
            violations.append(
                {
                    "code": "help_output_nonzero",
                    "message": "help surface returned non-zero exit code for {}".format(_token(row.get("bin_name"))),
                    "file_path": "dist/bin/{}".format(_token(row.get("bin_name"))),
                    "rule_id": RULE_HELP_ID,
                }
            )
        if not bool(row.get("stable_across_runs")):
            violations.append(
                {
                    "code": "help_output_drift",
                    "message": "help output drifted across repeated runs for {}".format(_token(row.get("bin_name"))),
                    "file_path": "dist/bin/{}".format(_token(row.get("bin_name"))),
                    "rule_id": RULE_HELP_ID,
                }
            )
        if not bool(row.get("contains_examples")) or not bool(row.get("contains_tip")):
            violations.append(
                {
                    "code": "help_output_missing_guidance",
                    "message": "help output is missing examples or narrowed-topic guidance for {}".format(_token(row.get("bin_name"))),
                    "file_path": CLI_REFERENCE_PATH,
                    "rule_id": RULE_HELP_ID,
                }
            )
    if cli_reference_error:
        violations.append(
            {
                "code": "cli_reference_generation_failed",
                "message": "CLI reference generation failed",
                "file_path": CLI_REFERENCE_PATH,
                "rule_id": RULE_HELP_ID,
            }
        )
    elif "## Getting Started" not in cli_reference_text or "diag capture" not in cli_reference_text:
        violations.append(
            {
                "code": "cli_reference_missing_examples",
                "message": "CLI reference is missing required getting-started examples",
                "file_path": CLI_REFERENCE_PATH,
                "rule_id": RULE_HELP_ID,
            }
        )

    for row in refusal_rows:
        if _token(row.get("result")) != "refused":
            violations.append(
                {
                    "code": "refusal_surface_missing_refusal",
                    "message": "refusal surface did not emit a refused payload for {}".format(_token(row.get("surface_id"))),
                    "file_path": "src/appshell/commands/command_engine.py",
                    "rule_id": RULE_REMEDIATION_ID,
                }
            )
        if not _token(row.get("refusal_code")) or not _token(row.get("reason")):
            violations.append(
                {
                    "code": "unstructured_user_facing_error",
                    "message": "user-facing refusal omitted a stable code or short reason for {}".format(_token(row.get("surface_id"))),
                    "file_path": "src/appshell/commands/command_engine.py",
                    "rule_id": RULE_REMEDIATION_ID,
                }
            )
        if not _token(row.get("remediation_hint")):
            violations.append(
                {
                    "code": "refusal_missing_remediation",
                    "message": "refusal payload omitted a remediation hint for {}".format(_token(row.get("surface_id"))),
                    "file_path": "src/appshell/commands/command_engine.py",
                    "rule_id": RULE_REMEDIATION_ID,
                }
            )

    for row in status_rows:
        if not bool(row.get("payload_present")):
            violations.append(
                {
                    "code": "status_payload_not_json",
                    "message": "status surface did not emit a JSON payload for {}".format(_token(row.get("surface_id"))),
                    "file_path": "tools/launcher/launch.py" if "launcher" in _token(row.get("surface_id")) else "tools/setup/setup_cli.py",
                    "rule_id": RULE_REMEDIATION_ID,
                }
            )
        if not _token(row.get("message")) or not bool(row.get("has_summary")):
            violations.append(
                {
                    "code": "status_payload_missing_summary",
                    "message": "status surface is missing message or summary fields for {}".format(_token(row.get("surface_id"))),
                    "file_path": "tools/launcher/launch.py" if "launcher" in _token(row.get("surface_id")) else "tools/setup/setup_cli.py",
                    "rule_id": RULE_REMEDIATION_ID,
                }
            )

    if not bool(tui_probe.get("show_help")) or not list(tui_probe.get("help_lines") or []):
        violations.append(
            {
                "code": "tui_help_missing",
                "message": "TUI help is not visible by default",
                "file_path": "src/appshell/tui/tui_engine.py",
                "rule_id": RULE_HELP_ID,
            }
        )
    for panel_id in ("panel.menu", "panel.console", "panel.logs", "panel.status"):
        if panel_id not in set(str(item) for item in list(tui_probe.get("panel_ids") or [])):
            violations.append(
                {
                    "code": "tui_panel_missing",
                    "message": "TUI surface is missing required panel {}".format(panel_id),
                    "file_path": "src/appshell/tui/tui_engine.py",
                    "rule_id": RULE_HELP_ID,
                }
            )

    quick_actions = set(str(item) for item in list(rendered_probe.get("quick_actions") or []))
    if _token(rendered_probe.get("menu_title")) != "Dominium":
        violations.append(
            {
                "code": "rendered_menu_missing",
                "message": "rendered client menu title is missing",
                "file_path": "src/client/ui/main_menu_surface.py",
                "rule_id": RULE_HELP_ID,
            }
        )
    for token in ("Start", "Seed", "Instance", "Save", "Console"):
        if token not in quick_actions:
            violations.append(
                {
                    "code": "rendered_menu_missing",
                    "message": "rendered client quick action {} is missing".format(token),
                    "file_path": "src/client/ui/main_menu_surface.py",
                    "rule_id": RULE_HELP_ID,
                }
            )
    if not bool(rendered_probe.get("console_overlay_available")):
        violations.append(
            {
                "code": "rendered_menu_missing",
                "message": "rendered client console overlay hint is missing",
                "file_path": "src/client/ui/main_menu_surface.py",
                "rule_id": RULE_HELP_ID,
            }
        )

    report = {
        "report_id": DIST5_REPORT_ID,
        "result": "complete" if not violations else "violation",
        "help_rows": help_rows,
        "refusal_rows": refusal_rows,
        "status_rows": status_rows,
        "tui_probe": tui_probe,
        "rendered_probe": rendered_probe,
        "violation_count": int(len(violations)),
        "violations": sorted(
            [dict(row or {}) for row in violations],
            key=lambda row: (_token(row.get("code")), _token(row.get("file_path")), _token(row.get("message"))),
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_ux_smoke_markdown(report: Mapping[str, object]) -> str:
    payload = dict(report or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-14",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: release UX smoke report regenerated from DIST-5 tooling",
        "",
        "# DIST5 UX Smoke",
        "",
        "## Summary",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- violation_count: `{}`".format(int(payload.get("violation_count", 0) or 0)),
        "- fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Help Surfaces",
        "",
    ]
    for row in list(payload.get("help_rows") or []):
        item = dict(row or {})
        lines.append(
            "- `{}` -> returncode=`{}` stable=`{}` examples=`{}`".format(
                _token(item.get("bin_name")),
                int(item.get("returncode", 0) or 0),
                bool(item.get("stable_across_runs")),
                bool(item.get("contains_examples")),
            )
        )
    lines.extend(["", "## Refusals", ""])
    for row in list(payload.get("refusal_rows") or []):
        item = dict(row or {})
        lines.append(
            "- `{}` -> code=`{}` remediation=`{}`".format(
                _token(item.get("surface_id")),
                _token(item.get("refusal_code")),
                _token(item.get("remediation_hint")),
            )
        )
    lines.extend(["", "## Status Outputs", ""])
    for row in list(payload.get("status_rows") or []):
        item = dict(row or {})
        lines.append(
            "- `{}` -> payload=`{}` summary=`{}`".format(
                _token(item.get("surface_id")),
                bool(item.get("payload_present")),
                bool(item.get("has_summary")),
            )
        )
    lines.extend(
        [
            "",
            "## TUI",
            "",
            "- backend_id: `{}`".format(_token(dict(payload.get("tui_probe") or {}).get("backend_id"))),
            "- show_help: `{}`".format(bool(dict(payload.get("tui_probe") or {}).get("show_help"))),
            "- panels: `{}`".format(", ".join(list(dict(payload.get("tui_probe") or {}).get("panel_ids") or []))),
            "",
            "## Rendered Client",
            "",
            "- menu_title: `{}`".format(_token(dict(payload.get("rendered_probe") or {}).get("menu_title"))),
            "- console_overlay_available: `{}`".format(bool(dict(payload.get("rendered_probe") or {}).get("console_overlay_available"))),
            "- quick_actions: `{}`".format(", ".join(list(dict(payload.get("rendered_probe") or {}).get("quick_actions") or []))),
            "",
            "## Violations",
            "",
        ]
    )
    if not list(payload.get("violations") or []):
        lines.append("- none")
    else:
        for row in list(payload.get("violations") or []):
            item = dict(row or {})
            lines.append(
                "- `{}` [{}] {}".format(
                    _token(item.get("code")),
                    _token(item.get("rule_id")),
                    _token(item.get("message")),
                )
            )
    return "\n".join(lines).rstrip() + "\n"


def render_dist5_final_markdown(report: Mapping[str, object]) -> str:
    payload = dict(report or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-14",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: release UX polish final report regenerated from DIST-5 tooling",
        "",
        "# DIST5 Final",
        "",
        "## Changes Summary",
        "",
        "- help output now includes deterministic grouping, topic guidance, and practical examples",
        "- launcher and setup status surfaces include readable `message` and `summary` fields",
        "- the TUI shows key help, menu, console, logs, and status immediately",
        "- the rendered client menu exposes start, seed, instance/save selection, console, teleport, and inspect hints",
        "",
        "## Known Limitations",
        "",
        "- AppShell status surfaces remain JSON-first; machine output is the default public contract",
        "- optional native launcher/setup adapters remain capability-gated and may fall back to TUI or CLI",
        "- internal fingerprints remain visible in explicit machine-readable outputs",
        "",
        "## Readiness",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- violation_count: `{}`".format(int(payload.get("violation_count", 0) or 0)),
        "- readiness for DIST-6: `{}`".format("ready" if _token(payload.get("result")) == "complete" else "blocked"),
        "",
    ]
    return "\n".join(lines)


def write_ux_smoke_outputs(
    repo_root: str,
    report: Mapping[str, object],
    *,
    doc_path: str = "",
    json_path: str = "",
    final_doc_path: str = "",
) -> dict:
    root = _norm(repo_root)
    doc_target = _write_text(os.path.join(root, _token(doc_path) or DIST5_UX_SMOKE_DOC_PATH), render_ux_smoke_markdown(report))
    json_target = _write_json(os.path.join(root, _token(json_path) or DIST5_UX_SMOKE_JSON_PATH), report)
    final_target = _write_text(os.path.join(root, _token(final_doc_path) or DIST5_FINAL_PATH), render_dist5_final_markdown(report))
    return {
        "doc_path": _repo_rel(doc_target, root),
        "json_path": _repo_rel(json_target, root),
        "final_doc_path": _repo_rel(final_target, root),
    }


def load_ux_smoke_report(repo_root: str) -> dict:
    path = os.path.join(_norm(repo_root), DIST5_UX_SMOKE_JSON_PATH.replace("/", os.sep))
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def ux_smoke_violations(repo_root: str) -> list[dict]:
    report = load_ux_smoke_report(repo_root)
    if not report:
        report = build_ux_smoke_report(repo_root)
    violations = [dict(row or {}) for row in list(report.get("violations") or [])]
    if violations:
        return violations
    if _token(report.get("result")) == "complete":
        return []
    return [
        {
            "code": "ux_smoke_incomplete",
            "message": "DIST-5 UX smoke report is incomplete",
            "file_path": DIST5_UX_SMOKE_JSON_PATH,
            "rule_id": RULE_HELP_ID,
        }
    ]


__all__ = [
    "CLI_REFERENCE_PATH",
    "DIST5_FINAL_PATH",
    "DIST5_REPORT_ID",
    "DIST5_UX_SMOKE_DOC_PATH",
    "DIST5_UX_SMOKE_JSON_PATH",
    "RULE_HELP_ID",
    "RULE_REMEDIATION_ID",
    "UX_POLISH_CRITERIA_PATH",
    "build_ux_smoke_report",
    "load_ux_smoke_report",
    "render_dist5_final_markdown",
    "render_ux_smoke_markdown",
    "ux_smoke_violations",
    "write_ux_smoke_outputs",
]
