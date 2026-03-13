"""Deterministic DIST-4 platform matrix helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Iterable, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.appshell.ui_mode_selector import policy_row_for_product
from src.compat.capability_negotiation import fallback_map_rows_by_capability_id
from src.platform.platform_probe import (
    MODE_TO_CAPABILITY_ID,
    canonical_platform_id,
    load_platform_capability_registry,
    probe_platform_descriptor,
)
from tools.dist.dist_tree_common import DEFAULT_RELEASE_CHANNEL, PRODUCT_IDS, build_dist_tree
from tools.release.ui_mode_resolution_common import build_test_probe, selection_for_product
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


DIST_PLATFORM_MATRIX_REPORT_ID = "dist.platform_matrix.v1"
DIST_PLATFORM_MATRIX_REPORT_PATH = "docs/audit/DIST_PLATFORM_MATRIX_REPORT.md"
DIST_PLATFORM_MATRIX_JSON_PATH = "data/audit/dist_platform_matrix.json"
SUPPORTED_PLATFORMS_DOC_PATH = "docs/release/SUPPORTED_PLATFORMS_v0_0_0_mock.md"
DIST4_FINAL_PATH = "docs/audit/DIST4_FINAL.md"
DEFAULT_PLATFORM_TAGS = ("win64",)
DEFAULT_BUILD_OUTPUT_ROOT = os.path.join("build", "tmp", "dist4_matrix_bundle")
RULE_ID = "INV-DIST-PLATFORM-MATRIX-MUST-EXIST"
FALLBACK_REQUESTS = {
    "client": ("rendered", ("rendered", "tui", "cli")),
    "engine": ("tui", ("tui", "cli")),
    "game": ("tui", ("tui", "cli")),
    "launcher": ("os_native", ("os_native", "tui", "cli")),
    "server": ("tui", ("tui", "cli")),
    "setup": ("os_native", ("os_native", "tui", "cli")),
}
SUPPORTED_PLATFORM_TAG_TO_ID = {
    "linux": "platform.linux_gtk",
    "linux-x86_64": "platform.linux_gtk",
    "macos-classic": "platform.macos_classic",
    "macos-universal": "platform.macos_cocoa",
    "macos_cocoa": "platform.macos_cocoa",
    "posix": "platform.posix_min",
    "posix-min": "platform.posix_min",
    "sdl": "platform.sdl_stub",
    "win64": "platform.winnt",
    "win9x": "platform.win9x",
    "winnt": "platform.winnt",
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/").lstrip("./")


def _repo_rel(path: str, repo_root: str) -> str:
    abs_path = _norm(path)
    root = _norm(repo_root)
    try:
        rel_path = os.path.relpath(abs_path, root)
    except ValueError:
        return _norm_rel(abs_path)
    if rel_path.startswith(".."):
        return _norm_rel(abs_path)
    return _norm_rel(rel_path)


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


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _extract_json_objects(stdout: str) -> list[dict]:
    rows: list[dict] = []
    decoder = json.JSONDecoder()
    remaining = str(stdout or "").lstrip()
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


def _run_bundle_product(bundle_root: str, product_id: str, argv: Sequence[str]) -> dict:
    wrapper_path = os.path.join(_norm(bundle_root), "bin", _token(product_id))
    proc = subprocess.run(
        [sys.executable, wrapper_path] + [str(item) for item in list(argv or [])],
        cwd=_norm(bundle_root),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    stdout_json_rows = _extract_json_objects(proc.stdout)
    stderr_json_rows = _extract_json_objects(proc.stderr)
    event_rows = [
        dict(row)
        for row in stdout_json_rows + stderr_json_rows
        if _token(_as_map(row).get("event_id"))
    ]
    first_json = {}
    for row in stdout_json_rows + stderr_json_rows:
        row_map = _as_map(row)
        if row_map and "event_id" not in row_map:
            first_json = row_map
            break
    return {
        "returncode": int(proc.returncode or 0),
        "stdout": str(proc.stdout or ""),
        "stderr": str(proc.stderr or ""),
        "json_rows": stdout_json_rows + stderr_json_rows,
        "first_json": first_json,
        "event_rows": event_rows,
        "stdout_fingerprint": canonical_sha256({"stdout": str(proc.stdout or "")}),
        "stderr_fingerprint": canonical_sha256({"stderr": str(proc.stderr or "")}),
    }


def _platform_id_for_tag(platform_tag: str) -> str:
    token = _token(platform_tag).lower()
    return canonical_platform_id(SUPPORTED_PLATFORM_TAG_TO_ID.get(token, token or "platform.winnt"))


def _supported_flags_from_descriptor(descriptor: Mapping[str, object]) -> dict[str, bool]:
    platform_descriptor = _as_map(_as_map(_as_map(descriptor).get("extensions")).get("official.platform_descriptor"))
    supported_flags = _as_map(platform_descriptor.get("supported_capability_flags"))
    return {
        capability_id: bool(supported_flags.get(capability_id, False))
        for capability_id in (
            "cap.ui.os_native",
            "cap.ui.rendered",
            "cap.ui.tui",
            "cap.ui.cli",
        )
    }


def _available_modes_from_descriptor(descriptor: Mapping[str, object]) -> dict[str, bool]:
    platform_descriptor = _as_map(_as_map(_as_map(descriptor).get("extensions")).get("official.platform_descriptor"))
    available_modes = _as_map(platform_descriptor.get("available_modes"))
    return {
        mode_id: bool(available_modes.get(mode_id, False))
        for mode_id in ("os_native", "rendered", "tui", "cli")
    }


def _platform_descriptor_from_descriptor(descriptor: Mapping[str, object]) -> dict:
    return _as_map(_as_map(_as_map(descriptor).get("extensions")).get("official.platform_descriptor"))


def _platform_registry_row(bundle_root: str, platform_id: str) -> dict:
    registry_payload, _error = load_platform_capability_registry(bundle_root)
    for row in _as_list(_as_map(registry_payload.get("record")).get("entries")):
        row_map = _as_map(row)
        if canonical_platform_id(_token(row_map.get("platform_id"))) == canonical_platform_id(platform_id):
            return row_map
    return {}


def _bundle_root_from_input(path: str, *, platform_tag: str, channel_id: str) -> str:
    candidate = _norm(path)
    if os.path.isfile(os.path.join(candidate, "install.manifest.json")):
        return candidate
    nested = os.path.join(candidate, "v0.0.0-{}".format(_token(channel_id) or DEFAULT_RELEASE_CHANNEL), _token(platform_tag), "dominium")
    if os.path.isfile(os.path.join(nested, "install.manifest.json")):
        return _norm(nested)
    return candidate


def _context_ids(simulate_tty: str, simulate_gui: str) -> list[str]:
    tty_token = _token(simulate_tty).lower() or "both"
    gui_token = _token(simulate_gui).lower() or "both"
    tty_values = [True] if tty_token == "yes" else [False] if tty_token == "no" else [True, False]
    gui_values = [True] if gui_token == "yes" else [False] if gui_token == "no" else [True, False]
    ordered: list[str] = []
    for tty_present in tty_values:
        for gui_present in gui_values:
            if tty_present:
                context_id = "tty"
            elif gui_present:
                context_id = "gui"
            else:
                context_id = "headless"
            if context_id not in ordered:
                ordered.append(context_id)
    return [context_id for context_id in ("tty", "gui", "headless") if context_id in ordered]


def _context_probe(
    bundle_root: str,
    *,
    product_id: str,
    platform_id: str,
    supported_flags: Mapping[str, object],
    context_id: str,
) -> dict:
    native_supported = bool(_as_map(supported_flags).get("cap.ui.os_native", False))
    rendered_supported = bool(_as_map(supported_flags).get("cap.ui.rendered", False))
    tui_supported = bool(_as_map(supported_flags).get("cap.ui.tui", False))
    token = _token(context_id)
    return build_test_probe(
        bundle_root,
        product_id=product_id,
        platform_id=platform_id,
        tty=(token == "tty"),
        gui=(token == "gui") or (token == "tty" and bool(native_supported or rendered_supported)),
        native=native_supported,
        rendered=rendered_supported,
        tui=tui_supported,
    )


def _policy_expected_mode(policy_row: Mapping[str, object], context_id: str, probe: Mapping[str, object]) -> str:
    token = _token(context_id)
    if token == "gui":
        order = [_token(item) for item in _as_list(_as_map(policy_row).get("gui_mode_order"))]
    elif token == "headless":
        order = [_token(item) for item in _as_list(_as_map(policy_row).get("headless_mode_order"))]
    else:
        order = [_token(item) for item in _as_list(_as_map(policy_row).get("tty_mode_order"))]
    available_modes = _as_map(probe.get("available_modes"))
    for mode_id in order:
        if bool(available_modes.get(mode_id, False)):
            return mode_id
    return ""


def _forced_expected_mode(requested_mode_id: str, available_modes: Mapping[str, object], fallback_order: Sequence[str]) -> str:
    requested = _token(requested_mode_id)
    modes = _as_map(available_modes)
    if bool(modes.get(requested, False)):
        return requested
    for mode_id in list(fallback_order or ()):
        token = _token(mode_id)
        if bool(modes.get(token, False)):
            return token
    return ""


def _event_message_keys(run: Mapping[str, object]) -> list[str]:
    out: list[str] = []
    for row in _as_list(_as_map(run).get("event_rows")):
        message_key = _token(_as_map(row).get("message_key"))
        if message_key and message_key not in out:
            out.append(message_key)
    return out


def _descriptor_reference_probe(bundle_root: str, *, product_id: str, platform_id: str) -> dict:
    return probe_platform_descriptor(
        bundle_root,
        product_id=product_id,
        platform_id=platform_id,
        stdin_tty=True,
        stdout_tty=False,
        stderr_tty=False,
        gui_available=False,
        ncurses_available=True,
    )


def _product_runtime_row(bundle_root: str, *, product_id: str, platform_id: str) -> dict:
    descriptor_run = _run_bundle_product(bundle_root, product_id, ["--descriptor"])
    descriptor_payload = _as_map(descriptor_run.get("first_json"))
    compat_run = _run_bundle_product(bundle_root, product_id, ["compat-status", "--mode", "cli"])
    compat_payload = _as_map(compat_run.get("first_json"))
    mode_selection = _as_map(compat_payload.get("mode_selection"))
    descriptor_supported_flags = _supported_flags_from_descriptor(descriptor_payload)
    descriptor_available_modes = _available_modes_from_descriptor(descriptor_payload)
    platform_descriptor = _platform_descriptor_from_descriptor(descriptor_payload)
    reference_probe = _descriptor_reference_probe(bundle_root, product_id=product_id, platform_id=platform_id)
    reference_supported_flags = _as_map(reference_probe.get("supported_capability_flags"))
    capability_match = {
        capability_id: bool(descriptor_supported_flags.get(capability_id, False)) == bool(reference_supported_flags.get(capability_id, False))
        for capability_id in ("cap.ui.os_native", "cap.ui.rendered", "cap.ui.tui", "cap.ui.cli")
    }
    build_id = _token(_as_map(descriptor_payload.get("extensions")).get("official.build_id"))
    return {
        "product_id": _token(product_id),
        "descriptor_returncode": int(descriptor_run.get("returncode", 0) or 0),
        "compat_returncode": int(compat_run.get("returncode", 0) or 0),
        "descriptor_platform_id": canonical_platform_id(_token(_as_map(descriptor_payload.get("extensions")).get("official.platform_id")) or platform_id),
        "descriptor_build_id": build_id,
        "descriptor_supported_flags": descriptor_supported_flags,
        "descriptor_available_modes": descriptor_available_modes,
        "descriptor_supported_mode_ids": list(_as_list(platform_descriptor.get("supported_mode_ids"))),
        "descriptor_available_mode_ids": list(_as_list(platform_descriptor.get("available_mode_ids"))),
        "descriptor_platform_descriptor_hash": _token(_as_map(descriptor_payload.get("extensions")).get("official.platform_descriptor_hash")),
        "descriptor_fingerprint": _token(descriptor_payload.get("deterministic_fingerprint")),
        "compat_status_fingerprint": _token(compat_payload.get("deterministic_fingerprint")),
        "cli_selected_mode_id": _token(mode_selection.get("selected_mode_id")),
        "cli_context_kind": _token(mode_selection.get("context_kind")),
        "cli_compatibility_mode_id": _token(mode_selection.get("compatibility_mode_id")),
        "cli_event_message_keys": _event_message_keys(compat_run),
        "capability_match": capability_match,
        "capability_match_passed": all(bool(value) for value in capability_match.values()),
        "passed": (
            int(descriptor_run.get("returncode", 0) or 0) == 0
            and int(compat_run.get("returncode", 0) or 0) == 0
            and _token(mode_selection.get("selected_mode_id")) == "cli"
            and all(bool(value) for value in capability_match.values())
        ),
        "deterministic_fingerprint": canonical_sha256(
            {
                "product_id": _token(product_id),
                "descriptor_fingerprint": _token(descriptor_payload.get("deterministic_fingerprint")),
                "compat_status_fingerprint": _token(compat_payload.get("deterministic_fingerprint")),
                "capability_match": capability_match,
            }
        ),
    }


def _context_row(
    bundle_root: str,
    *,
    platform_tag: str,
    platform_id: str,
    product_id: str,
    supported_flags: Mapping[str, object],
    context_id: str,
) -> dict:
    policy_row = policy_row_for_product(bundle_root, product_id)
    probe = _context_probe(
        bundle_root,
        product_id=product_id,
        platform_id=platform_id,
        supported_flags=supported_flags,
        context_id=context_id,
    )
    selection = selection_for_product(
        bundle_root,
        product_id=product_id,
        probe=probe,
    )
    expected_mode_id = _policy_expected_mode(policy_row, context_id, probe)
    selected_mode_id = _token(selection.get("selected_mode_id"))
    passed = _token(selection.get("result")) == "complete" and bool(expected_mode_id) and selected_mode_id == expected_mode_id
    return {
        "platform_tag": _token(platform_tag),
        "platform_id": canonical_platform_id(platform_id),
        "product_id": _token(product_id),
        "context_id": _token(context_id),
        "expected_mode_id": expected_mode_id,
        "selected_mode_id": selected_mode_id,
        "compatibility_mode_id": _token(selection.get("compatibility_mode_id")),
        "available_mode_ids": list(_as_list(probe.get("available_mode_ids"))),
        "supported_mode_ids": list(_as_list(probe.get("supported_mode_ids"))),
        "degrade_chain": [dict(item or {}) for item in _as_list(selection.get("degrade_chain"))],
        "reason": "policy_selection",
        "passed": passed,
        "selection_fingerprint": _token(selection.get("deterministic_fingerprint")),
        "probe_fingerprint": _token(probe.get("deterministic_fingerprint")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "platform_tag": _token(platform_tag),
                "product_id": _token(product_id),
                "context_id": _token(context_id),
                "selected_mode_id": selected_mode_id,
                "expected_mode_id": expected_mode_id,
                "selection_fingerprint": _token(selection.get("deterministic_fingerprint")),
            }
        ),
    }


def _fallback_row(
    bundle_root: str,
    *,
    platform_tag: str,
    platform_id: str,
    product_id: str,
    requested_mode_id: str,
    fallback_order: Sequence[str],
    supported_flags: Mapping[str, object],
) -> dict:
    run = _run_bundle_product(bundle_root, product_id, ["compat-status", "--mode", _token(requested_mode_id)])
    payload = _as_map(run.get("first_json"))
    mode_selection = _as_map(payload.get("mode_selection"))
    context_id = _token(mode_selection.get("context_kind")) or "headless"
    probe = _context_probe(
        bundle_root,
        product_id=product_id,
        platform_id=platform_id,
        supported_flags=supported_flags,
        context_id=context_id,
    )
    selected_mode_id = _token(mode_selection.get("selected_mode_id"))
    expected_mode_id = _forced_expected_mode(requested_mode_id, _as_map(probe.get("available_modes")), fallback_order)
    event_message_keys = _event_message_keys(run)
    degrade_expected = bool(expected_mode_id and expected_mode_id != _token(requested_mode_id))
    degrade_logged = "appshell.mode.degraded" in event_message_keys
    passed = (
        int(run.get("returncode", 0) or 0) == 0
        and bool(expected_mode_id)
        and selected_mode_id == expected_mode_id
        and (not degrade_expected or degrade_logged)
    )
    return {
        "platform_tag": _token(platform_tag),
        "product_id": _token(product_id),
        "requested_mode_id": _token(requested_mode_id),
        "expected_mode_id": expected_mode_id,
        "selected_mode_id": selected_mode_id,
        "context_id": context_id,
        "compatibility_mode_id": _token(mode_selection.get("compatibility_mode_id")),
        "degrade_chain": [dict(item or {}) for item in _as_list(mode_selection.get("degrade_chain"))],
        "degrade_expected": degrade_expected,
        "degrade_logged": degrade_logged,
        "event_message_keys": event_message_keys,
        "available_modes": {key: bool(value) for key, value in sorted(_as_map(probe.get("available_modes")).items())},
        "passed": passed,
        "payload_fingerprint": _token(payload.get("deterministic_fingerprint")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "platform_tag": _token(platform_tag),
                "product_id": _token(product_id),
                "requested_mode_id": _token(requested_mode_id),
                "context_id": context_id,
                "selected_mode_id": selected_mode_id,
                "expected_mode_id": expected_mode_id,
                "payload_fingerprint": _token(payload.get("deterministic_fingerprint")),
            }
        ),
    }


def _platform_input_rows(
    repo_root: str,
    *,
    platform_tags: Sequence[str],
    bundle_roots: Mapping[str, str] | None,
    channel_id: str,
    build_output_root: str,
) -> list[dict]:
    rows: list[dict] = []
    explicit = dict(bundle_roots or {})
    seen_tags: list[str] = []
    for item in list(platform_tags or []) + list(explicit.keys()):
        token = _token(item)
        if token and token not in seen_tags:
            seen_tags.append(token)
    for platform_tag in sorted(seen_tags or list(DEFAULT_PLATFORM_TAGS)):
        if platform_tag in explicit:
            bundle_root = _bundle_root_from_input(explicit[platform_tag], platform_tag=platform_tag, channel_id=channel_id)
            rows.append(
                {
                    "platform_tag": platform_tag,
                    "bundle_root_abs": bundle_root,
                    "source_kind": "provided",
                }
            )
            continue
        report = build_dist_tree(
            repo_root,
            platform_tag=platform_tag,
            channel_id=channel_id,
            output_root=build_output_root,
        )
        rows.append(
            {
                "platform_tag": platform_tag,
                "bundle_root_abs": _norm(report.get("bundle_root_abs")),
                "source_kind": "built",
            }
        )
    return sorted(rows, key=lambda row: (_token(row.get("platform_tag")), _token(row.get("bundle_root_abs"))))


def build_platform_matrix_report(
    repo_root: str,
    *,
    platform_tags: Sequence[str] = DEFAULT_PLATFORM_TAGS,
    bundle_roots: Mapping[str, str] | None = None,
    channel_id: str = DEFAULT_RELEASE_CHANNEL,
    build_output_root: str = DEFAULT_BUILD_OUTPUT_ROOT,
    simulate_tty: str = "both",
    simulate_gui: str = "both",
) -> dict:
    root = _norm(repo_root)
    context_ids = _context_ids(simulate_tty, simulate_gui)
    input_rows = _platform_input_rows(
        root,
        platform_tags=platform_tags,
        bundle_roots=bundle_roots,
        channel_id=channel_id,
        build_output_root=build_output_root,
    )
    platform_rows = []
    failures = []
    registry_rows: list[dict] = []
    if input_rows:
        registry_payload, _error = load_platform_capability_registry(_norm(_as_map(input_rows[0]).get("bundle_root_abs")))
        registry_rows = sorted(
            [_as_map(item) for item in _as_list(_as_map(registry_payload.get("record")).get("entries"))],
            key=lambda item: canonical_platform_id(_token(item.get("platform_id"))),
        )
    for input_row in input_rows:
        platform_tag = _token(input_row.get("platform_tag"))
        bundle_root_abs = _norm(input_row.get("bundle_root_abs"))
        bundle_root_rel = _repo_rel(bundle_root_abs, root)
        platform_id = _platform_id_for_tag(platform_tag)
        registry_row = _platform_registry_row(bundle_root_abs, platform_id)
        product_rows = []
        context_rows = []
        fallback_rows = []
        for product_id in PRODUCT_IDS:
            product_row = _product_runtime_row(bundle_root_abs, product_id=product_id, platform_id=platform_id)
            product_rows.append(product_row)
            descriptor_flags = _as_map(product_row.get("descriptor_supported_flags"))
            descriptor_available_modes = _as_map(product_row.get("descriptor_available_modes"))
            for context_id in context_ids:
                context_row = _context_row(
                    bundle_root_abs,
                    platform_tag=platform_tag,
                    platform_id=platform_id,
                    product_id=product_id,
                    supported_flags=descriptor_flags,
                    context_id=context_id,
                )
                context_rows.append(context_row)
                if not bool(context_row.get("passed")):
                    failures.append(
                        {
                            "code": "mode_selection_mismatch",
                            "file_path": DIST_PLATFORM_MATRIX_JSON_PATH,
                            "message": "{} {} {} selected {} instead of {}".format(
                                product_id,
                                platform_tag,
                                context_id,
                                _token(context_row.get("selected_mode_id")),
                                _token(context_row.get("expected_mode_id")),
                            ),
                            "rule_id": RULE_ID,
                        }
                    )
            requested_mode_id, fallback_order = FALLBACK_REQUESTS.get(product_id, ("cli", ("cli",)))
            fallback_row = _fallback_row(
                bundle_root_abs,
                platform_tag=platform_tag,
                platform_id=platform_id,
                product_id=product_id,
                requested_mode_id=requested_mode_id,
                fallback_order=fallback_order,
                supported_flags=descriptor_flags,
            )
            fallback_rows.append(fallback_row)
            if not bool(fallback_row.get("passed")):
                failures.append(
                    {
                        "code": "fallback_chain_mismatch",
                        "file_path": DIST_PLATFORM_MATRIX_JSON_PATH,
                        "message": "{} {} fallback {} resolved to {} instead of {}".format(
                            product_id,
                            platform_tag,
                            requested_mode_id,
                            _token(fallback_row.get("selected_mode_id")),
                            _token(fallback_row.get("expected_mode_id")),
                        ),
                        "rule_id": RULE_ID,
                    }
                )
            if not bool(product_row.get("passed")):
                failures.append(
                    {
                        "code": "platform_capability_mismatch",
                        "file_path": DIST_PLATFORM_MATRIX_JSON_PATH,
                        "message": "{} {} runtime descriptor or compat-status drifted".format(product_id, platform_tag),
                        "rule_id": RULE_ID,
                    }
                )
        platform_report = {
            "platform_tag": platform_tag,
            "platform_id": platform_id,
            "source_kind": _token(input_row.get("source_kind")),
            "bundle_root": bundle_root_rel,
            "registry_support_tier": _token(registry_row.get("support_tier")),
            "registry_display_name": _token(registry_row.get("display_name")),
            "registry_ui_flags": {
                capability_id: bool(_as_map(registry_row).get(capability_id, False))
                for capability_id in ("cap.ui.os_native", "cap.ui.rendered", "cap.ui.tui", "cap.ui.cli")
            },
            "product_rows": sorted(product_rows, key=lambda row: _token(_as_map(row).get("product_id"))),
            "context_rows": sorted(
                context_rows,
                key=lambda row: (
                    _token(_as_map(row).get("platform_tag")),
                    _token(_as_map(row).get("product_id")),
                    _token(_as_map(row).get("context_id")),
                ),
            ),
            "fallback_rows": sorted(
                fallback_rows,
                key=lambda row: (
                    _token(_as_map(row).get("platform_tag")),
                    _token(_as_map(row).get("product_id")),
                    _token(_as_map(row).get("requested_mode_id")),
                ),
            ),
            "failure_count": int(
                sum(
                    1
                    for row in product_rows + context_rows + fallback_rows
                    if not bool(_as_map(row).get("passed", True))
                )
            ),
            "deterministic_fingerprint": "",
        }
        platform_report["deterministic_fingerprint"] = canonical_sha256(dict(platform_report, deterministic_fingerprint=""))
        platform_rows.append(platform_report)
    report = {
        "report_id": DIST_PLATFORM_MATRIX_REPORT_ID,
        "result": "complete" if not failures else "refused",
        "channel_id": _token(channel_id) or DEFAULT_RELEASE_CHANNEL,
        "context_ids": list(context_ids),
        "registry_rows": registry_rows,
        "platform_rows": sorted(platform_rows, key=lambda row: (_token(_as_map(row).get("platform_tag")), _token(_as_map(row).get("bundle_root")))),
        "failures": sorted(
            [dict(item or {}) for item in list(failures or []) if isinstance(item, Mapping)],
            key=lambda row: (_token(row.get("rule_id")), _token(row.get("code")), _token(row.get("message"))),
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_platform_matrix_report(report: Mapping[str, object]) -> str:
    row = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-14",
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-5 UX polish and archive matrix",
        "",
        "# DIST Platform Matrix Report",
        "",
        "- result: `{}`".format(_token(row.get("result"))),
        "- channel_id: `{}`".format(_token(row.get("channel_id"))),
        "- contexts: `{}`".format(", ".join(_token(item) for item in _as_list(row.get("context_ids"))) or "none"),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "",
        "## Matrix Summary",
        "",
    ]
    for platform_row in _as_list(row.get("platform_rows")):
        item = _as_map(platform_row)
        lines.append(
            "- `{}` `{}` source=`{}` failures=`{}` fingerprint=`{}`".format(
                _token(item.get("platform_tag")),
                _token(item.get("platform_id")),
                _token(item.get("source_kind")),
                int(item.get("failure_count", 0) or 0),
                _token(item.get("deterministic_fingerprint")),
            )
        )
    lines.extend(["", "## Product Runtime Checks", ""])
    for platform_row in _as_list(row.get("platform_rows")):
        item = _as_map(platform_row)
        lines.append("### {}".format(_token(item.get("platform_tag")) or "platform"))
        lines.append("")
        for product_row in _as_list(item.get("product_rows")):
            product = _as_map(product_row)
            lines.append(
                "- `{}` descriptor=`{}` compat_cli=`{}` selected=`{}` capability_match=`{}`".format(
                    _token(product.get("product_id")),
                    int(product.get("descriptor_returncode", 0) or 0),
                    int(product.get("compat_returncode", 0) or 0),
                    _token(product.get("cli_selected_mode_id")),
                    bool(product.get("capability_match_passed")),
                )
            )
        lines.append("")
    lines.extend(["## Simulated Context Selection", ""])
    for platform_row in _as_list(row.get("platform_rows")):
        for context_row in _as_list(_as_map(platform_row).get("context_rows")):
            item = _as_map(context_row)
            lines.append(
                "- `{}` `{}` `{}` expected=`{}` selected=`{}` passed=`{}`".format(
                    _token(item.get("platform_tag")),
                    _token(item.get("product_id")),
                    _token(item.get("context_id")),
                    _token(item.get("expected_mode_id")),
                    _token(item.get("selected_mode_id")),
                    bool(item.get("passed")),
                )
            )
    lines.extend(["", "## Forced Fallback Checks", ""])
    for platform_row in _as_list(row.get("platform_rows")):
        for fallback_row in _as_list(_as_map(platform_row).get("fallback_rows")):
            item = _as_map(fallback_row)
            lines.append(
                "- `{}` `{}` context=`{}` requested=`{}` expected=`{}` selected=`{}` degrade_logged=`{}` passed=`{}`".format(
                    _token(item.get("platform_tag")),
                    _token(item.get("product_id")),
                    _token(item.get("context_id")),
                    _token(item.get("requested_mode_id")),
                    _token(item.get("expected_mode_id")),
                    _token(item.get("selected_mode_id")),
                    bool(item.get("degrade_logged")),
                    bool(item.get("passed")),
                )
            )
    lines.extend(["", "## Failures", ""])
    failures = _as_list(row.get("failures"))
    if not failures:
        lines.append("- none")
    else:
        for item in failures:
            failure = _as_map(item)
            lines.append(
                "- `{}`: {} ({})".format(
                    _token(failure.get("code")),
                    _token(failure.get("message")),
                    _token(failure.get("rule_id")),
                )
            )
    return "\n".join(lines) + "\n"


def render_supported_platforms_doc(report: Mapping[str, object]) -> str:
    row = _as_map(report)
    platform_rows = {canonical_platform_id(_token(_as_map(item).get("platform_id"))): _as_map(item) for item in _as_list(row.get("platform_rows"))}
    registry_rows = sorted(
        [_as_map(item) for item in _as_list(row.get("registry_rows"))],
        key=lambda item: canonical_platform_id(_token(item.get("platform_id"))),
    )
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-14",
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-5 UX polish and archive support notes",
        "",
        "# Supported Platforms v0.0.0 Mock",
        "",
        "This matrix records the shipped UI layers per platform family and the deterministic fallback policy for forcing AppShell modes.",
        "",
        "## Platform Support",
        "",
        "| Platform | Support Tier | Built In DIST-4 | UI Layers | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for registry_row in registry_rows:
        platform_id = canonical_platform_id(_token(registry_row.get("platform_id")))
        built_row = platform_rows.get(platform_id, {})
        ui_layers = [
            layer_id.replace("cap.ui.", "")
            for layer_id in ("cap.ui.os_native", "cap.ui.rendered", "cap.ui.tui", "cap.ui.cli")
            if bool(_as_map(registry_row).get(layer_id, False))
        ]
        notes = "built from `{}`".format(_token(built_row.get("platform_tag"))) if built_row else "not built in current matrix run"
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                platform_id,
                _token(registry_row.get("support_tier")) or "unknown",
                "yes" if built_row else "no",
                ", ".join(ui_layers) or "none",
                notes,
            )
        )
    lines.extend(
        [
            "",
            "## Known Disabled Capabilities",
            "",
            "- OS-native GUI adapters are only selected when the platform row and shipped adapter markers both declare support.",
            "- Rendered UI is currently only expected for client bundles that ship the rendered host markers.",
            "- TUI is preferred for interactive server, engine, and game contexts when available; CLI remains the universal fallback.",
            "",
            "## Forcing a Mode",
            "",
            "- `bin/client compat-status --mode rendered`",
            "- `bin/setup compat-status --mode os_native`",
            "- `bin/server compat-status --mode tui`",
            "- `bin/launcher compat-status --mode cli`",
            "",
        ]
    )
    return "\n".join(lines)


def build_dist4_final_report(reports: Sequence[Mapping[str, object]]) -> dict:
    normalized = sorted([_as_map(item) for item in list(reports or []) if isinstance(item, Mapping)], key=lambda row: _token(row.get("deterministic_fingerprint")))
    payload = {
        "report_id": "dist.platform_matrix.final.v1",
        "result": "complete" if normalized and all(_token(row.get("result")) == "complete" for row in normalized) else "refused",
        "platforms": sorted(
            {
                _token(_as_map(platform_row).get("platform_tag"))
                for report in normalized
                for platform_row in _as_list(_as_map(report).get("platform_rows"))
                if _token(_as_map(platform_row).get("platform_tag"))
            }
        ),
        "failure_count": int(sum(len(_as_list(_as_map(report).get("failures"))) for report in normalized)),
        "report_fingerprints": [
            _token(row.get("deterministic_fingerprint"))
            for row in normalized
            if _token(row.get("deterministic_fingerprint"))
        ],
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def render_dist4_final(final_report: Mapping[str, object], reports: Sequence[Mapping[str, object]]) -> str:
    row = _as_map(final_report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-14",
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-5 UX polish and release archive platform verification",
        "",
        "# DIST4 Final",
        "",
        "- result: `{}`".format(_token(row.get("result"))),
        "- platforms: `{}`".format(", ".join(_token(item) for item in _as_list(row.get("platforms"))) or "none"),
        "- failure_count: `{}`".format(int(row.get("failure_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "",
        "## Matrix Summary",
        "",
    ]
    for report in sorted([_as_map(item) for item in list(reports or []) if isinstance(item, Mapping)], key=lambda item: _token(item.get("deterministic_fingerprint"))):
        for platform_row in _as_list(report.get("platform_rows")):
            item = _as_map(platform_row)
            lines.append(
                "- `{}` `{}` result=`{}` failures=`{}`".format(
                    _token(item.get("platform_tag")),
                    _token(item.get("platform_id")),
                    _token(report.get("result")),
                    int(item.get("failure_count", 0) or 0),
                )
            )
    lines.extend(["", "## Observed Fallback Chains", ""])
    observed_rows = []
    for report in list(reports or []):
        for platform_row in _as_list(_as_map(report).get("platform_rows")):
            observed_rows.extend(_as_list(_as_map(platform_row).get("fallback_rows")))
    for item in sorted([_as_map(row) for row in observed_rows], key=lambda row: (_token(row.get("platform_tag")), _token(row.get("product_id")))):
        lines.append(
            "- `{}` `{}` `{}` -> `{}` context=`{}` logged=`{}`".format(
                _token(item.get("platform_tag")),
                _token(item.get("product_id")),
                _token(item.get("requested_mode_id")),
                _token(item.get("selected_mode_id")),
                _token(item.get("context_id")),
                bool(item.get("degrade_logged")),
            )
        )
    lines.extend(["", "## Failures", ""])
    failures = []
    for report in list(reports or []):
        failures.extend(_as_list(_as_map(report).get("failures")))
    if not failures:
        lines.append("- none")
    else:
        for item in sorted([_as_map(row) for row in failures], key=lambda row: (_token(row.get("code")), _token(row.get("message")))):
            lines.append("- `{}`: {}".format(_token(item.get("code")), _token(item.get("message"))))
    lines.extend(["", "## Readiness", "", "- DIST-5 UX polish: {}".format("ready" if _token(row.get("result")) == "complete" else "blocked"), ""])
    return "\n".join(lines) + "\n"


def write_platform_matrix_outputs(
    repo_root: str,
    report: Mapping[str, object],
    *,
    report_path: str = "",
    doc_path: str = "",
    supported_doc_path: str = "",
    final_doc_path: str = "",
) -> dict:
    root = _norm(repo_root)
    report_rel = _token(report_path) or DIST_PLATFORM_MATRIX_JSON_PATH
    doc_rel = _token(doc_path) or DIST_PLATFORM_MATRIX_REPORT_PATH
    supported_rel = _token(supported_doc_path) or SUPPORTED_PLATFORMS_DOC_PATH
    final_rel = _token(final_doc_path) or DIST4_FINAL_PATH
    report_abs = report_rel if os.path.isabs(report_rel) else os.path.join(root, report_rel.replace("/", os.sep))
    doc_abs = doc_rel if os.path.isabs(doc_rel) else os.path.join(root, doc_rel.replace("/", os.sep))
    supported_abs = supported_rel if os.path.isabs(supported_rel) else os.path.join(root, supported_rel.replace("/", os.sep))
    final_abs = final_rel if os.path.isabs(final_rel) else os.path.join(root, final_rel.replace("/", os.sep))
    _write_json(report_abs, report)
    _write_text(doc_abs, render_platform_matrix_report(report))
    _write_text(supported_abs, render_supported_platforms_doc(report))
    final_report = build_dist4_final_report([report])
    _write_text(final_abs, render_dist4_final(final_report, [report]))
    return {
        "report_path": _repo_rel(report_abs, root),
        "doc_path": _repo_rel(doc_abs, root),
        "supported_doc_path": _repo_rel(supported_abs, root),
        "final_doc_path": _repo_rel(final_abs, root),
        "final_report": final_report,
    }


def load_dist_platform_matrix_report(repo_root: str) -> dict:
    return _read_json(os.path.join(_norm(repo_root), DIST_PLATFORM_MATRIX_JSON_PATH.replace("/", os.sep)))


def platform_matrix_violations(repo_root: str) -> list[dict]:
    payload = load_dist_platform_matrix_report(repo_root)
    if not payload:
        return [
            {
                "code": "dist_platform_matrix_missing",
                "file_path": DIST_PLATFORM_MATRIX_JSON_PATH,
                "message": "DIST-4 platform matrix report is missing",
                "rule_id": RULE_ID,
            }
        ]
    if _token(payload.get("result")) == "complete":
        return []
    rows = []
    for item in _as_list(payload.get("failures")):
        row = _as_map(item)
        rows.append(
            {
                "code": _token(row.get("code")) or "dist_platform_matrix_failure",
                "file_path": _token(row.get("file_path")) or DIST_PLATFORM_MATRIX_JSON_PATH,
                "message": _token(row.get("message")) or "DIST-4 platform matrix failed",
                "rule_id": _token(row.get("rule_id")) or RULE_ID,
            }
        )
    return sorted(rows, key=lambda row: (_token(row.get("rule_id")), _token(row.get("code")), _token(row.get("message"))))


__all__ = [
    "DEFAULT_BUILD_OUTPUT_ROOT",
    "DEFAULT_PLATFORM_TAGS",
    "DIST4_FINAL_PATH",
    "DIST_PLATFORM_MATRIX_JSON_PATH",
    "DIST_PLATFORM_MATRIX_REPORT_PATH",
    "RULE_ID",
    "SUPPORTED_PLATFORMS_DOC_PATH",
    "build_dist4_final_report",
    "build_platform_matrix_report",
    "load_dist_platform_matrix_report",
    "platform_matrix_violations",
    "render_dist4_final",
    "render_platform_matrix_report",
    "render_supported_platforms_doc",
    "write_platform_matrix_outputs",
]
