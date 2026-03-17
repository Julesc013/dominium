"""Derived PERFORMANCE-ENVELOPE-0 helpers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from typing import Mapping, Sequence

from tools.dist.dist_tree_common import build_dist_tree
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "PERFORMANCE_ENVELOPE0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "performance", "PERFORMANCE_ENVELOPE_v0_0_0_mock.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "PERFORMANCE_ENVELOPE_BASELINE.md")
REPORT_DOC_REL = os.path.join("docs", "audit", "PERFORMANCE_REPORT_{}.md")
REPORT_JSON_REL = os.path.join("data", "perf", "perf_report_{}.json")

RULE_BASELINE = "INV-PERFORMANCE-BASELINE-RECORDED"
RULE_CI = "INV-STARTUP-MEASURED-IN-CI"

DEFAULT_PLATFORM_TAG = "win64"
DEFAULT_RELEASE_CHANNEL = "mock"
DEFAULT_RELEASE_TAG = "v0.0.0-mock"
DEFAULT_FULL_OUTPUT_ROOT = os.path.join("build", "tmp", "performance_envelope_dist")
DEFAULT_SERVER_OUTPUT_ROOT = os.path.join("build", "tmp", "performance_envelope_server_dist")
DEFAULT_RUNTIME_ROOT = os.path.join("build", "tmp", "performance_envelope_runtime")
LAST_REVIEWED = "2026-03-14"

PRODUCT_STARTUP_COMMANDS = {
    "setup": ["help"],
    "client": ["compat-status"],
    "server": ["compat-status"],
    "launcher": ["compat-status"],
}

DECLARED_TARGETS_BY_PLATFORM = {
    DEFAULT_PLATFORM_TAG: {
        "setup_startup_seconds": 5.0,
        "client_startup_seconds": 5.0,
        "server_startup_seconds": 5.0,
        "clean_room_seconds": 15.0,
        "idle_server_cpu_percent": 1.0,
        "idle_client_cpu_percent": 1.0,
        "client_memory_mb": 128,
        "server_memory_mb": 128,
        "portable_full_bundle_mb": 64,
        "minimal_server_profile_mb": 48,
        "base_pack_bundle_mb": 4,
        "full_component_count": 24,
        "pack_lock_kb": 8,
        "store_lookup_latency_ms": 10,
    }
}

MB = 1024 * 1024
KB = 1024


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


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
    with open(_norm(path), "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return dict(payload or {}) if isinstance(payload, Mapping) else {}


def _read_text(path: str) -> str:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _repo_rel(repo_root: str, path: str) -> str:
    root = _norm(repo_root)
    target = _norm(path)
    try:
        return _norm_rel(os.path.relpath(target, root))
    except ValueError:
        return _norm_rel(target)


def _platform_slug(platform_tag: str) -> str:
    token = _token(platform_tag) or DEFAULT_PLATFORM_TAG
    return "".join(char if char.isalnum() else "_" for char in token)


def _report_doc_rel(platform_tag: str) -> str:
    return REPORT_DOC_REL.format(_platform_slug(platform_tag))


def _report_json_rel(platform_tag: str) -> str:
    return REPORT_JSON_REL.format(_platform_slug(platform_tag))


def _bundle_root(output_root: str, platform_tag: str) -> str:
    return os.path.join(
        _norm(output_root),
        DEFAULT_RELEASE_TAG,
        _token(platform_tag) or DEFAULT_PLATFORM_TAG,
        "dominium",
    )


def _ensure_bundle(
    repo_root: str,
    *,
    platform_tag: str,
    output_root: str,
    install_profile_id: str,
) -> str:
    candidates = []
    if _token(install_profile_id) == "install.profile.full":
        candidates.extend(
            [
                os.path.join(_norm(repo_root), "build", "tmp", "dist3_bundle_c", DEFAULT_RELEASE_TAG, _token(platform_tag) or DEFAULT_PLATFORM_TAG, "dominium"),
                os.path.join(_norm(repo_root), "dist", DEFAULT_RELEASE_TAG, _token(platform_tag) or DEFAULT_PLATFORM_TAG, "dominium"),
            ]
        )
    candidates.append(_bundle_root(output_root, platform_tag))
    for candidate in candidates:
        if os.path.isfile(os.path.join(candidate, "install.manifest.json")) and os.path.isfile(
            os.path.join(candidate, "manifests", "release_manifest.json")
        ):
            return candidate
    bundle_root = _bundle_root(output_root, platform_tag)
    build_dist_tree(
        repo_root,
        platform_tag=_token(platform_tag) or DEFAULT_PLATFORM_TAG,
        channel_id=DEFAULT_RELEASE_CHANNEL,
        output_root=_norm(output_root),
        install_profile_id=_token(install_profile_id),
    )
    return bundle_root


def _ps_quote(value: str) -> str:
    return "'" + str(value or "").replace("'", "''") + "'"


def _ps_array(values: Sequence[str]) -> str:
    return "@({})".format(", ".join(_ps_quote(str(item)) for item in list(values or [])))


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


def _powershell_json(script: str) -> dict:
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    stdout = str(proc.stdout or "").strip()
    if int(proc.returncode) != 0:
        raise RuntimeError(str(proc.stderr or stdout or "PowerShell probe failed").strip())
    try:
        payload = json.loads(stdout or "{}")
    except ValueError as exc:
        raise RuntimeError("PowerShell probe returned invalid JSON") from exc
    return dict(payload or {}) if isinstance(payload, Mapping) else {}


def _prepare_probe_bundle(bundle_root: str, runtime_root: str, probe_id: str) -> str:
    def _remove_readonly(func, path, exc_info):
        del exc_info
        try:
            os.chmod(path, 0o666)
        except OSError:
            pass
        func(path)

    base_target = os.path.join(_norm(runtime_root), "probes", _token(probe_id))
    for index in range(0, 32):
        target = base_target if index == 0 else "{}_{:02d}".format(base_target, index)
        try:
            if os.path.isdir(target):
                shutil.rmtree(target, onerror=_remove_readonly)
            elif os.path.exists(target):
                os.chmod(target, 0o666)
                os.remove(target)
        except OSError:
            pass
        if os.path.exists(target):
            continue
        try:
            shutil.copytree(_norm(bundle_root), target)
            return target
        except FileExistsError:
            continue
    raise RuntimeError("unable to allocate probe bundle path for {}".format(_token(probe_id)))


def _measure_python_command(
    argv: Sequence[str],
    *,
    cwd: str,
    capture_json: bool = False,
) -> dict:
    output_json = os.path.join(_norm(cwd), "measurement.stdout.json") if capture_json else ""
    script = "\n".join(
        [
            "$ErrorActionPreference = 'Stop'",
            "function HashFile([string]$Path) {",
            "  if (-not (Test-Path $Path)) { return '' }",
            "  $stream = [System.IO.File]::OpenRead($Path)",
            "  try {",
            "    $sha = [System.Security.Cryptography.SHA256]::Create()",
            "    try {",
            "      return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()",
            "    } finally {",
            "      $sha.Dispose()",
            "    }",
            "  } finally {",
            "    $stream.Dispose()",
            "  }",
            "}",
            "$env:PYTHONHASHSEED = '0'",
            "Get-ChildItem env:DOMINIUM_* -ErrorAction SilentlyContinue | Remove-Item -ErrorAction SilentlyContinue",
            "$stdoutPath = [System.IO.Path]::GetTempFileName()",
            "$stderrPath = [System.IO.Path]::GetTempFileName()",
            "try {",
            "  $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()",
            "  $proc = Start-Process -FilePath {} -ArgumentList {} -WorkingDirectory {} -PassThru -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath".format(
                _ps_quote(sys.executable),
                _ps_array([str(item) for item in list(argv or [])]),
                _ps_quote(_norm(cwd)),
            ),
            "  $maxWorkingSet = [int64]0",
            "  $maxPagedMemory = [int64]0",
            "  $maxVirtualMemory = [int64]0",
            "  $proc.Refresh()",
            "  if ($proc.WorkingSet64 -gt $maxWorkingSet) { $maxWorkingSet = [int64]$proc.WorkingSet64 }",
            "  if ($proc.PagedMemorySize64 -gt $maxPagedMemory) { $maxPagedMemory = [int64]$proc.PagedMemorySize64 }",
            "  if ($proc.VirtualMemorySize64 -gt $maxVirtualMemory) { $maxVirtualMemory = [int64]$proc.VirtualMemorySize64 }",
            "  while (-not $proc.HasExited) {",
            "    $proc.Refresh()",
            "    if ($proc.WorkingSet64 -gt $maxWorkingSet) { $maxWorkingSet = [int64]$proc.WorkingSet64 }",
            "    if ($proc.PagedMemorySize64 -gt $maxPagedMemory) { $maxPagedMemory = [int64]$proc.PagedMemorySize64 }",
            "    if ($proc.VirtualMemorySize64 -gt $maxVirtualMemory) { $maxVirtualMemory = [int64]$proc.VirtualMemorySize64 }",
            "  }",
            "  $proc.WaitForExit()",
            "  $stopwatch.Stop()",
            "  $proc.Refresh()",
            "  if ($proc.WorkingSet64 -gt $maxWorkingSet) { $maxWorkingSet = [int64]$proc.WorkingSet64 }",
            "  if ($proc.PagedMemorySize64 -gt $maxPagedMemory) { $maxPagedMemory = [int64]$proc.PagedMemorySize64 }",
            "  if ($proc.VirtualMemorySize64 -gt $maxVirtualMemory) { $maxVirtualMemory = [int64]$proc.VirtualMemorySize64 }",
            "  if ($proc.PeakWorkingSet64 -gt $maxWorkingSet) { $maxWorkingSet = [int64]$proc.PeakWorkingSet64 }",
            "  if ($proc.PeakPagedMemorySize64 -gt $maxPagedMemory) { $maxPagedMemory = [int64]$proc.PeakPagedMemorySize64 }",
            "  if ($proc.PeakVirtualMemorySize64 -gt $maxVirtualMemory) { $maxVirtualMemory = [int64]$proc.PeakVirtualMemorySize64 }",
            "  $stdoutText = if (Test-Path $stdoutPath) { [System.IO.File]::ReadAllText($stdoutPath) } else { '' }",
            "  $stderrText = if (Test-Path $stderrPath) { [System.IO.File]::ReadAllText($stderrPath) } else { '' }",
        ]
    )
    if capture_json and output_json:
        script += "\n  [System.IO.File]::WriteAllText({}, $stdoutText, [System.Text.Encoding]::UTF8)".format(_ps_quote(output_json))
    script += "\n".join(
        [
            "",
            "  $payload = @{",
            "    exit_code = [int]$proc.ExitCode",
            "    elapsed_ms = [int][Math]::Round($stopwatch.Elapsed.TotalMilliseconds)",
            "    total_processor_ms = [int][Math]::Round($proc.TotalProcessorTime.TotalMilliseconds)",
            "    peak_working_set_bytes = [int64]$maxWorkingSet",
            "    peak_paged_memory_bytes = [int64]$maxPagedMemory",
            "    peak_virtual_memory_bytes = [int64]$maxVirtualMemory",
            "    stdout_sha256 = HashFile $stdoutPath",
            "    stderr_sha256 = HashFile $stderrPath",
            "    stdout_line_count = if ($stdoutText) { @($stdoutText -split \"`r?`n\").Count } else { 0 }",
            "    stderr_line_count = if ($stderrText) { @($stderrText -split \"`r?`n\").Count } else { 0 }",
            "  }",
            "  $payload | ConvertTo-Json -Compress -Depth 8",
            "} finally {",
            "  Remove-Item $stdoutPath -ErrorAction SilentlyContinue",
            "  Remove-Item $stderrPath -ErrorAction SilentlyContinue",
            "}",
        ]
    )
    payload = _powershell_json(script)
    if capture_json and output_json and os.path.isfile(output_json):
        payload["stdout_json_objects"] = _extract_json_objects(_read_text(output_json))
        try:
            os.remove(output_json)
        except OSError:
            pass
    return payload


def _measure_bundle_product(
    bundle_root: str,
    runtime_root: str,
    *,
    product_id: str,
    argv: Sequence[str],
) -> dict:
    probe_root = _prepare_probe_bundle(bundle_root, runtime_root, "{}_{}".format(_token(product_id), canonical_sha256(list(argv or []))[:12]))
    metrics = _measure_python_command(
        [os.path.join(probe_root, "bin", _token(product_id))] + [str(item) for item in list(argv or [])],
        cwd=probe_root,
    )
    return {
        "product_id": _token(product_id),
        "argv": [str(item) for item in list(argv or [])],
        "probe_root": _norm_rel(os.path.relpath(probe_root, _norm(runtime_root))),
        **dict(metrics),
    }


def _measure_clean_room(repo_root: str, bundle_root: str, runtime_root: str, platform_tag: str) -> dict:
    report_path = os.path.join(_norm(runtime_root), "clean_room_report.json")
    doc_path = os.path.join(_norm(runtime_root), "clean_room_report.md")
    final_doc_path = os.path.join(_norm(runtime_root), "clean_room_final.md")
    metrics = _measure_python_command(
        [
            os.path.join(_norm(repo_root), "tools", "dist", "tool_run_clean_room.py"),
            "--repo-root",
            _norm(repo_root),
            "--dist-root",
            _norm(bundle_root),
            "--platform-tag",
            _token(platform_tag) or DEFAULT_PLATFORM_TAG,
            "--seed",
            "456",
            "--mode-policy",
            "cli",
            "--work-root",
            os.path.join(_norm(runtime_root), "clean_room_work"),
            "--report-path",
            report_path,
            "--doc-path",
            doc_path,
            "--final-doc-path",
            final_doc_path,
        ],
        cwd=_norm(repo_root),
        capture_json=True,
    )
    report = _read_json(report_path) if os.path.isfile(report_path) else dict((_as_list(metrics.get("stdout_json_objects")) or [{}])[0] or {})
    return {
        **dict(metrics),
        "clean_room_report": report,
        "clean_room_report_path": _norm_rel(os.path.relpath(report_path, _norm(repo_root))),
        "clean_room_doc_path": _norm_rel(os.path.relpath(doc_path, _norm(repo_root))),
    }


def _measure_store_lookup_latency(target_path: str) -> dict:
    script = "\n".join(
        [
            "$ErrorActionPreference = 'Stop'",
            "$path = {}".format(_ps_quote(_norm(target_path))),
            "$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()",
            "$bytes = [System.IO.File]::ReadAllBytes($path)",
            "$stopwatch.Stop()",
            "$payload = @{",
            "  elapsed_ms = [int][Math]::Round($stopwatch.Elapsed.TotalMilliseconds)",
            "  byte_count = [int]$bytes.Length",
            "}",
            "$payload | ConvertTo-Json -Compress -Depth 4",
        ]
    )
    return _powershell_json(script)


def _sum_file_sizes(root: str) -> int:
    total = 0
    for current_root, _, filenames in os.walk(_norm(root)):
        for name in filenames:
            path = os.path.join(current_root, name)
            if os.path.isfile(path):
                total += int(os.path.getsize(path))
    return int(total)


def _count_component_descriptors(install_manifest: Mapping[str, object]) -> int:
    extensions = _as_map(install_manifest.get("extensions"))
    rows = _as_list(extensions.get("official.selected_component_descriptors"))
    return len(rows)


def _full_install_profile_components(repo_root: str, install_manifest: Mapping[str, object]) -> tuple[int, list[str]]:
    extensions = _as_map(install_manifest.get("extensions"))
    selected_rows = _as_list(extensions.get("official.selected_component_descriptors"))
    selected_ids = sorted(
        _token(_as_map(row).get("component_id"))
        for row in selected_rows
        if _token(_as_map(row).get("component_id"))
    )
    if selected_ids:
        return len(selected_ids), selected_ids

    report_path = os.path.join(_norm(repo_root), "data", "audit", "install_profile_report.json")
    if not os.path.isfile(report_path):
        return 0, []
    payload = _read_json(report_path)
    rows = sorted(_as_list(payload.get("profiles")), key=lambda row: _token(_as_map(row).get("install_profile_id")))
    full_row = next(
        (
            _as_map(row)
            for row in rows
            if _token(_as_map(row).get("install_profile_id")) == "install.profile.full"
        ),
        {},
    )
    full_ids = sorted(_token(value) for value in _as_list(full_row.get("selected_components")) if _token(value))
    return len(full_ids), full_ids


def _component_graph_counts(repo_root: str) -> dict:
    registry_path = os.path.join(_norm(repo_root), "data", "registries", "component_graph_registry.json")
    payload = _read_json(registry_path)
    record = _as_map(payload.get("record"))
    graphs = sorted(_as_list(record.get("graphs")), key=lambda row: _token(_as_map(row).get("graph_id")))
    graph = _as_map(graphs[0] if graphs else {})
    return {
        "graph_id": _token(graph.get("graph_id")),
        "component_count": len(_as_list(graph.get("components"))),
        "edge_count": len(_as_list(graph.get("edges"))),
    }


def _server_config_note(repo_root: str) -> dict:
    payload = _read_json(os.path.join(_norm(repo_root), "data", "registries", "server_config_registry.json"))
    rows = sorted(_as_list(_as_map(payload.get("record")).get("server_configs")), key=lambda row: _token(_as_map(row).get("server_id")))
    default_row = next((dict(row or {}) for row in rows if _token(_as_map(row).get("server_id")) == "server.mvp_default"), dict(rows[0] or {}) if rows else {})
    return {
        "server_config_id": _token(default_row.get("server_id")),
        "proof_anchor_interval_ticks": int(default_row.get("proof_anchor_interval_ticks", 0) or 0),
        "tick_rate_hz": "",
        "note": "default tick rate is not explicitly pinned in the current release surface; only proof anchor cadence is declared",
    }


def _derive_targets(report: Mapping[str, object]) -> dict:
    platform_tag = _token(_as_map(report).get("platform_tag")) or DEFAULT_PLATFORM_TAG
    return dict(DECLARED_TARGETS_BY_PLATFORM.get(platform_tag, DECLARED_TARGETS_BY_PLATFORM[DEFAULT_PLATFORM_TAG]))


def build_performance_report(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    root = _norm(repo_root)
    runtime_root = os.path.join(root, DEFAULT_RUNTIME_ROOT)
    os.makedirs(runtime_root, exist_ok=True)

    full_bundle_root = _ensure_bundle(
        root,
        platform_tag=_token(platform_tag) or DEFAULT_PLATFORM_TAG,
        output_root=os.path.join(root, DEFAULT_FULL_OUTPUT_ROOT),
        install_profile_id="install.profile.full",
    )
    server_bundle_root = _ensure_bundle(
        root,
        platform_tag=_token(platform_tag) or DEFAULT_PLATFORM_TAG,
        output_root=os.path.join(root, DEFAULT_SERVER_OUTPUT_ROOT),
        install_profile_id="install.profile.server",
    )
    release_manifest_path = os.path.join(full_bundle_root, "manifests", "release_manifest.json")
    release_manifest_hash_before = canonical_sha256(_read_json(release_manifest_path))

    startup_probe_root = _prepare_probe_bundle(full_bundle_root, runtime_root, "startup_probe")
    startup = {}
    for product_id in ("setup", "client", "server", "launcher"):
        startup[product_id] = {
            "product_id": product_id,
            "argv": list(PRODUCT_STARTUP_COMMANDS[product_id]),
            "probe_root": _norm_rel(os.path.relpath(startup_probe_root, _norm(runtime_root))),
            **_measure_python_command(
                [os.path.join(startup_probe_root, "bin", product_id)] + list(PRODUCT_STARTUP_COMMANDS[product_id]),
                cwd=startup_probe_root,
            ),
        }
    clean_room = _measure_clean_room(root, full_bundle_root, runtime_root, _token(platform_tag) or DEFAULT_PLATFORM_TAG)
    startup["clean_room"] = {
        "elapsed_ms": int(clean_room.get("elapsed_ms", 0) or 0),
        "exit_code": int(clean_room.get("exit_code", 1) or 1),
        "report_result": _token(_as_map(clean_room.get("clean_room_report")).get("result")),
        "report_fingerprint": _token(_as_map(clean_room.get("clean_room_report")).get("deterministic_fingerprint")),
        "replay_fingerprint": _token(_as_map(clean_room.get("clean_room_report")).get("replay_fingerprint")),
    }

    loopback_probe_root = _prepare_probe_bundle(full_bundle_root, runtime_root, "loopback_idle")
    launcher_start = _measure_python_command(
        [os.path.join(loopback_probe_root, "bin", "launcher"), "launcher", "start", "--seed", "456"],
        cwd=loopback_probe_root,
    )
    launcher_status = _measure_python_command(
        [os.path.join(loopback_probe_root, "bin", "launcher"), "launcher", "status"],
        cwd=loopback_probe_root,
        capture_json=True,
    )
    launcher_stop = _measure_python_command(
        [os.path.join(loopback_probe_root, "bin", "launcher"), "launcher", "stop"],
        cwd=loopback_probe_root,
    )
    install_manifest = _read_json(os.path.join(full_bundle_root, "install.manifest.json"))
    component_graph_counts = _component_graph_counts(root)
    full_component_count, full_component_ids = _full_install_profile_components(root, install_manifest)

    store_lookup_target = ""
    pack_roots = []
    packs_root = os.path.join(full_bundle_root, "store", "packs")
    for current_root, _, filenames in os.walk(packs_root):
        for name in sorted(filenames):
            store_lookup_target = os.path.join(current_root, name)
            break
        if store_lookup_target:
            break
    for entry in sorted(os.listdir(packs_root)):
        category_root = os.path.join(packs_root, entry)
        if not os.path.isdir(category_root):
            continue
        for pack_name in sorted(os.listdir(category_root)):
            pack_root = os.path.join(category_root, pack_name)
            if os.path.isdir(pack_root):
                pack_roots.append(pack_root)

    storage = {
        "portable_full_bundle_bytes": _sum_file_sizes(full_bundle_root),
        "minimal_server_bundle_bytes": _sum_file_sizes(server_bundle_root),
        "store_bytes": _sum_file_sizes(os.path.join(full_bundle_root, "store")),
        "base_pack_bundle_bytes": _sum_file_sizes(packs_root),
        "default_pack_lock_bytes": int(os.path.getsize(os.path.join(full_bundle_root, "store", "locks", "pack_lock.mvp_default.json"))),
        "store_hash_lookup_latency": _measure_store_lookup_latency(store_lookup_target) if store_lookup_target else {"elapsed_ms": 0, "byte_count": 0},
        "pack_count": len(pack_roots),
        "pack_sizes": [
            {
                "pack_root": _repo_rel(root, pack_root),
                "size_bytes": _sum_file_sizes(pack_root),
            }
            for pack_root in sorted(pack_roots)
        ],
    }

    memory = {
        "setup": {
            "peak_working_set_bytes": int(_as_map(startup.get("setup")).get("peak_working_set_bytes", 0) or 0),
            "peak_paged_memory_bytes": int(_as_map(startup.get("setup")).get("peak_paged_memory_bytes", 0) or 0),
        },
        "client": {
            "peak_working_set_bytes": int(_as_map(startup.get("client")).get("peak_working_set_bytes", 0) or 0),
            "peak_paged_memory_bytes": int(_as_map(startup.get("client")).get("peak_paged_memory_bytes", 0) or 0),
        },
        "server": {
            "peak_working_set_bytes": int(_as_map(startup.get("server")).get("peak_working_set_bytes", 0) or 0),
            "peak_paged_memory_bytes": int(_as_map(startup.get("server")).get("peak_paged_memory_bytes", 0) or 0),
        },
        "launcher": {
            "peak_working_set_bytes": int(_as_map(startup.get("launcher")).get("peak_working_set_bytes", 0) or 0),
            "peak_paged_memory_bytes": int(_as_map(startup.get("launcher")).get("peak_paged_memory_bytes", 0) or 0),
        },
        "loopback_idle": {
            "launcher_start_elapsed_ms": int(launcher_start.get("elapsed_ms", 0) or 0),
            "launcher_status_elapsed_ms": int(launcher_status.get("elapsed_ms", 0) or 0),
            "launcher_stop_elapsed_ms": int(launcher_stop.get("elapsed_ms", 0) or 0),
            "client_idle_cpu_percent": 0.0,
            "server_idle_cpu_percent": 0.0,
            "note": "loopback_supervisor_children_exit_after_startup_probe",
            "status_records": _as_list(launcher_status.get("stdout_json_objects")),
        },
    }

    graph = {
        **component_graph_counts,
        "install_profile_full_component_count": full_component_count,
        "install_profile_full_component_ids": full_component_ids,
    }

    release_manifest_hash_after = canonical_sha256(_read_json(release_manifest_path))
    clean_room_report = _as_map(clean_room.get("clean_room_report"))
    report = {
        "report_id": "performance.envelope.v1",
        "platform_tag": _token(platform_tag) or DEFAULT_PLATFORM_TAG,
        "tier1_target": {
            "os_id": "os.winnt",
            "arch_id": "arch.x86_64",
            "abi_id": "abi.msvc",
        },
        "bundle_roots": {
            "portable_full": _repo_rel(root, full_bundle_root),
            "server_profile": _repo_rel(root, server_bundle_root),
        },
        "startup": startup,
        "memory": memory,
        "storage": storage,
        "graph": graph,
        "runtime_policy": {
            "startup_proxy_note": "client/server startup is measured through governed CLI-safe bootstrap commands; rendered first-paint timing remains provisional in v0.0.0-mock",
            "server_timing_note": _server_config_note(root),
        },
        "determinism_guards": {
            "release_manifest_hash_before": release_manifest_hash_before,
            "release_manifest_hash_after": release_manifest_hash_after,
            "release_manifest_hash_unchanged": release_manifest_hash_before == release_manifest_hash_after,
            "clean_room_result": _token(clean_room_report.get("result")),
            "clean_room_fingerprint": _token(clean_room_report.get("deterministic_fingerprint")),
            "replay_fingerprint": _token(_as_map(clean_room_report.get("key_hashes")).get("replay_result_fingerprint"))
            or _token(clean_room_report.get("replay_fingerprint")),
        },
        "violations": [],
        "declared_targets": {},
        "observed_metric_fingerprint": "",
        "deterministic_fingerprint": "",
    }
    report["declared_targets"] = _derive_targets(report)
    report["observed_metric_fingerprint"] = canonical_sha256(
        {
            "graph": graph,
            "memory": memory,
            "startup": {
                key: {
                    "elapsed_ms": int(_as_map(value).get("elapsed_ms", 0) or 0),
                    "exit_code": int(_as_map(value).get("exit_code", 0) or 0),
                }
                for key, value in sorted(startup.items())
            },
            "storage": storage,
        }
    )

    if not bool(_as_map(report.get("determinism_guards")).get("release_manifest_hash_unchanged")):
        report["violations"].append(
            {
                "rule_id": RULE_BASELINE,
                "code": "release_manifest_hash_changed",
                "message": "performance measurement must not mutate the canonical release manifest payload",
                "file_path": _report_json_rel(_token(platform_tag) or DEFAULT_PLATFORM_TAG),
            }
        )

    report["result"] = "complete" if not _as_list(report.get("violations")) else "refused"
    report["deterministic_fingerprint"] = canonical_sha256(
        {
            "declared_targets": report["declared_targets"],
            "determinism_guards": {
                "clean_room_result": _token(_as_map(report.get("determinism_guards")).get("clean_room_result")),
                "release_manifest_hash_after": _token(_as_map(report.get("determinism_guards")).get("release_manifest_hash_after")),
                "release_manifest_hash_before": _token(_as_map(report.get("determinism_guards")).get("release_manifest_hash_before")),
                "release_manifest_hash_unchanged": bool(_as_map(report.get("determinism_guards")).get("release_manifest_hash_unchanged")),
            },
            "graph": graph,
            "platform_tag": report["platform_tag"],
            "report_id": report["report_id"],
            "runtime_policy": report["runtime_policy"],
            "storage_shape": {
                "pack_count": storage["pack_count"],
                "pack_sizes": list(storage["pack_sizes"]),
            },
            "tier1_target": report["tier1_target"],
            "violations": report["violations"],
        }
    )
    return report


def _render_size_mb(byte_count: object) -> str:
    return "{:.2f}".format(float(int(byte_count or 0)) / float(MB))


def _render_size_kb(byte_count: object) -> str:
    return "{:.2f}".format(float(int(byte_count or 0)) / float(KB))


def render_performance_report(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    startup = _as_map(payload.get("startup"))
    memory = _as_map(payload.get("memory"))
    storage = _as_map(payload.get("storage"))
    graph = _as_map(payload.get("graph"))
    guards = _as_map(payload.get("determinism_guards"))
    clean_room = _as_map(startup.get("clean_room"))
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: PERFORMANCE/CI",
        "Replacement Target: channel-specific performance budgets and regression history after DIST-7 packaging",
        "",
        "# Performance Report {}".format(_token(payload.get("platform_tag")).upper()),
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- report_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "- observed_metric_fingerprint: `{}`".format(_token(payload.get("observed_metric_fingerprint"))),
        "",
        "## Startup",
        "",
        "- setup_help_ms: `{}`".format(int(_as_map(startup.get("setup")).get("elapsed_ms", 0) or 0)),
        "- client_compat_status_ms: `{}`".format(int(_as_map(startup.get("client")).get("elapsed_ms", 0) or 0)),
        "- server_compat_status_ms: `{}`".format(int(_as_map(startup.get("server")).get("elapsed_ms", 0) or 0)),
        "- launcher_compat_status_ms: `{}`".format(int(_as_map(startup.get("launcher")).get("elapsed_ms", 0) or 0)),
        "- clean_room_elapsed_ms: `{}`".format(int(clean_room.get("elapsed_ms", 0) or 0)),
        "- clean_room_result: `{}`".format(_token(clean_room.get("report_result"))),
        "",
        "## Memory",
        "",
        "- client_peak_working_set_mb: `{}`".format(_render_size_mb(_as_map(memory.get("client")).get("peak_working_set_bytes", 0))),
        "- server_peak_working_set_mb: `{}`".format(_render_size_mb(_as_map(memory.get("server")).get("peak_working_set_bytes", 0))),
        "- setup_peak_working_set_mb: `{}`".format(_render_size_mb(_as_map(memory.get("setup")).get("peak_working_set_bytes", 0))),
        "- launcher_peak_working_set_mb: `{}`".format(_render_size_mb(_as_map(memory.get("launcher")).get("peak_working_set_bytes", 0))),
        "- idle_proxy_note: `{}`".format(_token(_as_map(memory.get("loopback_idle")).get("note"))),
        "",
        "## Storage",
        "",
        "- portable_full_bundle_mb: `{}`".format(_render_size_mb(storage.get("portable_full_bundle_bytes", 0))),
        "- minimal_server_bundle_mb: `{}`".format(_render_size_mb(storage.get("minimal_server_bundle_bytes", 0))),
        "- store_mb: `{}`".format(_render_size_mb(storage.get("store_bytes", 0))),
        "- base_pack_bundle_mb: `{}`".format(_render_size_mb(storage.get("base_pack_bundle_bytes", 0))),
        "- default_pack_lock_kb: `{}`".format(_render_size_kb(storage.get("default_pack_lock_bytes", 0))),
        "- store_lookup_latency_ms: `{}`".format(int(_as_map(storage.get("store_hash_lookup_latency")).get("elapsed_ms", 0) or 0)),
        "",
        "## Graph And Determinism",
        "",
        "- component_graph_component_count: `{}`".format(int(graph.get("component_count", 0) or 0)),
        "- install_profile_full_component_count: `{}`".format(int(graph.get("install_profile_full_component_count", 0) or 0)),
        "- clean_room_fingerprint: `{}`".format(_token(guards.get("clean_room_fingerprint"))),
        "- replay_fingerprint: `{}`".format(_token(guards.get("replay_fingerprint"))),
        "- release_manifest_hash_unchanged: `{}`".format("true" if bool(guards.get("release_manifest_hash_unchanged")) else "false"),
    ]
    return "\n".join(lines) + "\n"


def render_performance_retro_audit(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    startup = _as_map(payload.get("startup"))
    memory = _as_map(payload.get("memory"))
    storage = _as_map(payload.get("storage"))
    graph = _as_map(payload.get("graph"))
    runtime_policy = _as_map(payload.get("runtime_policy"))
    tick_note = _as_map(runtime_policy.get("server_timing_note"))
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: PERFORMANCE/CI",
        "Replacement Target: release-pinned platform performance baselines with retained historical measurements",
        "",
        "# PERFORMANCE-ENVELOPE-0 Retro Audit",
        "",
        "## Primary Platform",
        "",
        "- Tier 1 baseline target: `os.winnt + arch.x86_64 + abi.msvc`",
        "",
        "## Startup Baseline",
        "",
        "- setup startup proxy (`bin/setup help`): `{}` ms".format(int(_as_map(startup.get("setup")).get("elapsed_ms", 0) or 0)),
        "- client startup proxy (`bin/client compat-status`): `{}` ms".format(int(_as_map(startup.get("client")).get("elapsed_ms", 0) or 0)),
        "- server startup proxy (`bin/server compat-status`): `{}` ms".format(int(_as_map(startup.get("server")).get("elapsed_ms", 0) or 0)),
        "- clean-room end-to-end: `{}` ms".format(int(_as_map(startup.get("clean_room")).get("elapsed_ms", 0) or 0)),
        "- clean-room result: `{}`".format(_token(_as_map(startup.get("clean_room")).get("report_result"))),
        "",
        "## Resource Baseline",
        "",
        "- client peak working set: `{}` MB".format(_render_size_mb(_as_map(memory.get("client")).get("peak_working_set_bytes", 0))),
        "- server peak working set: `{}` MB".format(_render_size_mb(_as_map(memory.get("server")).get("peak_working_set_bytes", 0))),
        "- idle client CPU proxy: `0%`",
        "- idle server CPU proxy: `0%`",
        "- idle proxy note: `{}`".format(_token(_as_map(memory.get("loopback_idle")).get("note"))),
        "",
        "## Storage Baseline",
        "",
        "- portable full bundle: `{}` MB".format(_render_size_mb(storage.get("portable_full_bundle_bytes", 0))),
        "- minimal server profile: `{}` MB".format(_render_size_mb(storage.get("minimal_server_bundle_bytes", 0))),
        "- store footprint: `{}` MB".format(_render_size_mb(storage.get("store_bytes", 0))),
        "- base pack bundle: `{}` MB".format(_render_size_mb(storage.get("base_pack_bundle_bytes", 0))),
        "- default pack lock: `{}` KB".format(_render_size_kb(storage.get("default_pack_lock_bytes", 0))),
        "",
        "## Graph And Store Shape",
        "",
        "- default install.profile.full component count: `{}`".format(int(graph.get("install_profile_full_component_count", 0) or 0)),
        "- component graph size: `{}` components / `{}` edges".format(int(graph.get("component_count", 0) or 0), int(graph.get("edge_count", 0) or 0)),
        "- store hash lookup latency proxy: `{}` ms".format(int(_as_map(storage.get("store_hash_lookup_latency")).get("elapsed_ms", 0) or 0)),
        "",
        "## Tick And Idle Notes",
        "",
        "- server config id: `{}`".format(_token(tick_note.get("server_config_id"))),
        "- proof_anchor_interval_ticks: `{}`".format(int(tick_note.get("proof_anchor_interval_ticks", 0) or 0)),
        "- default tick rate: unpinned in current release metadata",
        "- note: {}".format(_token(tick_note.get("note"))),
    ]
    return "\n".join(lines) + "\n"


def render_performance_doctrine(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    targets = _as_map(payload.get("declared_targets"))
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: PERFORMANCE/CI",
        "Replacement Target: release-series performance budgets with per-target historical regression lanes",
        "",
        "# Performance Envelope v0.0.0-mock",
        "",
        "## Scope",
        "",
        "- Applies to standalone portable bundles, installed mode, singleplayer, and local server/client loopback on Tier 1 win64.",
        "- This envelope is declarative guardrail policy, not an optimization or scheduling feature.",
        "",
        "## Startup Targets",
        "",
        "- Setup cold startup proxy (`bin/setup help`) <= `{}` s".format(targets.get("setup_startup_seconds")),
        "- Client startup to governed main-menu equivalent proxy (`bin/client compat-status`) <= `{}` s".format(targets.get("client_startup_seconds")),
        "- Server startup proxy (`bin/server compat-status`) <= `{}` s".format(targets.get("server_startup_seconds")),
        "- Clean-room end-to-end acceptance lane <= `{}` s".format(targets.get("clean_room_seconds")),
        "",
        "## Idle Resource Targets",
        "",
        "- Idle server CPU proxy <= `{}` %".format(targets.get("idle_server_cpu_percent")),
        "- Idle client CPU proxy <= `{}` %".format(targets.get("idle_client_cpu_percent")),
        "- Client peak working set <= `{}` MB".format(targets.get("client_memory_mb")),
        "- Server peak working set <= `{}` MB".format(targets.get("server_memory_mb")),
        "",
        "## Storage Targets",
        "",
        "- Portable full bundle <= `{}` MB".format(targets.get("portable_full_bundle_mb")),
        "- Minimal server profile <= `{}` MB".format(targets.get("minimal_server_profile_mb")),
        "- Base pack bundle <= `{}` MB".format(targets.get("base_pack_bundle_mb")),
        "",
        "## Graph And Store Targets",
        "",
        "- Default install.profile.full component count <= `{}`".format(targets.get("full_component_count")),
        "- Default pack lock size <= `{}` KB".format(targets.get("pack_lock_kb")),
        "- Store hash lookup latency proxy <= `{}` ms on local SSD baseline".format(targets.get("store_lookup_latency_ms")),
        "",
        "## Determinism Guarantees",
        "",
        "- Performance probes must not modify canonical release manifests or semantic fingerprints.",
        "- Bundle execution used for measurement must run against disposable probe copies.",
        "- Hashes and proof/replay anchors remain governed by RELEASE, DIST, and DIAG contracts; this envelope only observes them.",
        "",
        "## Known Limits",
        "",
        "- v0.0.0-mock does not expose a stable GUI first-paint benchmark surface, so client startup is measured through the governed compat-status proxy.",
        "- Loopback supervisor children exit after the startup probe in the current mock lane, so idle CPU is recorded as an explicit proxy value rather than a long-lived resident sample.",
    ]
    return "\n".join(lines) + "\n"


def render_performance_baseline(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    targets = _as_map(payload.get("declared_targets"))
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: PERFORMANCE/CI",
        "Replacement Target: release-series performance baselines with retained regression history and per-target budgets",
        "",
        "# Performance Envelope Baseline",
        "",
        "## Baseline Metrics For Tier 1 Platform",
        "",
        "- platform_tag: `{}`".format(_token(payload.get("platform_tag"))),
        "- report_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "- portable_full_bundle_mb: `{}`".format(_render_size_mb(_as_map(payload.get("storage")).get("portable_full_bundle_bytes", 0))),
        "- clean_room_elapsed_ms: `{}`".format(int(_as_map(_as_map(payload.get("startup")).get("clean_room")).get("elapsed_ms", 0) or 0)),
        "",
        "## Declared Targets",
        "",
    ]
    for key in sorted(targets):
        lines.append("- `{}` = `{}`".format(key, targets[key]))
    lines.extend(
        [
            "",
            "## Known Risks",
            "",
            "- GUI first-paint timing is still proxied through CLI-safe surfaces in v0.0.0-mock.",
            "- Idle CPU sampling is a loopback proxy because supervised children exit after startup in the current mock runtime.",
            "- Store lookup latency is a local SSD file-open/read proxy rather than a dedicated long-running store service benchmark.",
            "",
            "## Readiness",
            "",
            "- ARCHIVE-POLICY-0: ready",
            "- DIST-7 packaging guardrail inputs: ready",
        ]
    )
    return "\n".join(lines) + "\n"


def write_performance_outputs(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM_TAG) -> dict:
    root = _norm(repo_root)
    report = build_performance_report(root, platform_tag=_token(platform_tag) or DEFAULT_PLATFORM_TAG)
    report_json_path = _write_json(os.path.join(root, _report_json_rel(_token(platform_tag) or DEFAULT_PLATFORM_TAG)), report)
    report_doc_path = _write_text(os.path.join(root, _report_doc_rel(_token(platform_tag) or DEFAULT_PLATFORM_TAG)), render_performance_report(report))
    retro_doc_path = _write_text(os.path.join(root, RETRO_AUDIT_DOC_REL), render_performance_retro_audit(report))
    doctrine_doc_path = _write_text(os.path.join(root, DOCTRINE_DOC_REL), render_performance_doctrine(report))
    baseline_doc_path = _write_text(os.path.join(root, BASELINE_DOC_REL), render_performance_baseline(report))
    return {
        "report": report,
        "report_json_path": _repo_rel(root, report_json_path),
        "report_doc_path": _repo_rel(root, report_doc_path),
        "retro_audit_doc_path": _repo_rel(root, retro_doc_path),
        "doctrine_doc_path": _repo_rel(root, doctrine_doc_path),
        "baseline_doc_path": _repo_rel(root, baseline_doc_path),
    }


def performance_envelope_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    violations = []
    required_paths = (
        (RETRO_AUDIT_DOC_REL, "PERFORMANCE-ENVELOPE-0 retro audit is required", RULE_BASELINE),
        (DOCTRINE_DOC_REL, "performance envelope doctrine is required", RULE_BASELINE),
        (BASELINE_DOC_REL, "performance envelope baseline is required", RULE_BASELINE),
        (_report_doc_rel(DEFAULT_PLATFORM_TAG), "platform performance markdown report is required", RULE_BASELINE),
        (_report_json_rel(DEFAULT_PLATFORM_TAG), "platform performance JSON report is required", RULE_BASELINE),
        ("tools/perf/performance_envelope_common.py", "performance envelope helper is required", RULE_BASELINE),
        ("tools/perf/tool_measure_startup.py", "startup measurement tool is required", RULE_BASELINE),
        ("tools/perf/tool_measure_memory.py", "memory measurement tool is required", RULE_BASELINE),
        ("tools/perf/tool_measure_store_size.py", "store-size measurement tool is required", RULE_BASELINE),
        ("tools/perf/tool_run_performance_envelope.py", "performance envelope runner is required", RULE_BASELINE),
        ("tools/auditx/analyzers/e535_performance_regression_smell.py", "performance regression analyzer is required", RULE_BASELINE),
    )
    for rel_path, message, rule_id in required_paths:
        if os.path.isfile(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        violations.append({"rule_id": rule_id, "code": "missing_required_file", "message": message, "file_path": rel_path})

    doctrine_text = _read_text(os.path.join(root, DOCTRINE_DOC_REL)).lower()
    for token, message in (
        ("# performance envelope v0.0.0-mock", "performance doctrine must declare the canonical title"),
        ("## startup targets", "performance doctrine must declare startup targets"),
        ("## idle resource targets", "performance doctrine must declare idle resource targets"),
        ("## storage targets", "performance doctrine must declare storage targets"),
        ("## graph and store targets", "performance doctrine must declare graph/store targets"),
        ("## determinism guarantees", "performance doctrine must declare determinism guarantees"),
    ):
        if token in doctrine_text:
            continue
        violations.append({"rule_id": RULE_BASELINE, "code": "missing_doctrine_section", "message": message, "file_path": DOCTRINE_DOC_REL})

    ci_text = _read_text(os.path.join(root, ".github", "workflows", "ci.yml")).lower()
    if "tools/perf/tool_run_performance_envelope.py" not in ci_text:
        violations.append(
            {
                "rule_id": RULE_CI,
                "code": "ci_step_missing",
                "message": "ci must invoke tools/perf/tool_run_performance_envelope.py",
                "file_path": ".github/workflows/ci.yml",
            }
        )

    if os.path.isfile(os.path.join(root, _report_json_rel(DEFAULT_PLATFORM_TAG).replace("/", os.sep))):
        report = _read_json(os.path.join(root, _report_json_rel(DEFAULT_PLATFORM_TAG)))
        if _token(report.get("result")) != "complete":
            violations.append(
                {
                    "rule_id": RULE_BASELINE,
                    "code": "report_incomplete",
                    "message": "performance report must complete successfully before the baseline is accepted",
                    "file_path": _report_json_rel(DEFAULT_PLATFORM_TAG),
                }
            )
        guards = _as_map(report.get("determinism_guards"))
        if not bool(guards.get("release_manifest_hash_unchanged")):
            violations.append(
                {
                    "rule_id": RULE_BASELINE,
                    "code": "release_manifest_hash_changed",
                    "message": "performance measurement must not mutate the canonical release manifest payload",
                    "file_path": _report_json_rel(DEFAULT_PLATFORM_TAG),
                }
            )
        graph = _as_map(report.get("graph"))
        if int(graph.get("component_count", 0) or 0) <= 0:
            violations.append(
                {
                    "rule_id": RULE_BASELINE,
                    "code": "component_graph_missing_metrics",
                    "message": "performance report must record the component graph size",
                    "file_path": _report_json_rel(DEFAULT_PLATFORM_TAG),
                }
            )
        if int(graph.get("install_profile_full_component_count", 0) or 0) <= 0:
            violations.append(
                {
                    "rule_id": RULE_BASELINE,
                    "code": "install_profile_missing_metrics",
                    "message": "performance report must record the full install-profile component count",
                    "file_path": _report_json_rel(DEFAULT_PLATFORM_TAG),
                }
            )
        timing_note = _as_map(_as_map(report.get("runtime_policy")).get("server_timing_note"))
        if int(timing_note.get("proof_anchor_interval_ticks", 0) or 0) <= 0:
            violations.append(
                {
                    "rule_id": RULE_BASELINE,
                    "code": "server_timing_missing",
                    "message": "performance report must record the declared proof anchor interval",
                    "file_path": _report_json_rel(DEFAULT_PLATFORM_TAG),
                }
            )
        memory = _as_map(report.get("memory"))
        for product_id in ("client", "server", "setup"):
            if int(_as_map(memory.get(product_id)).get("peak_working_set_bytes", 0) or 0) > 0:
                continue
            violations.append(
                {
                    "rule_id": RULE_BASELINE,
                    "code": "memory_measurement_missing",
                    "message": "performance report must record a non-zero working-set sample for {}".format(product_id),
                    "file_path": _report_json_rel(DEFAULT_PLATFORM_TAG),
                }
            )
        if not _token(_as_map(_as_map(report.get("startup")).get("clean_room")).get("report_fingerprint")):
            violations.append(
                {
                    "rule_id": RULE_BASELINE,
                    "code": "clean_room_report_missing",
                    "message": "performance report must retain the clean-room report fingerprint",
                    "file_path": _report_json_rel(DEFAULT_PLATFORM_TAG),
                }
            )
    return sorted(
        [dict(row or {}) for row in violations],
        key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))),
    )


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "LAST_REVIEWED",
    "REPORT_DOC_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_BASELINE",
    "RULE_CI",
    "build_performance_report",
    "performance_envelope_violations",
    "render_performance_baseline",
    "render_performance_doctrine",
    "render_performance_report",
    "render_performance_retro_audit",
    "write_performance_outputs",
]
