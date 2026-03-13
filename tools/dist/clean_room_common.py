"""Deterministic DIST-3 clean-room harness helpers."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Iterable, Mapping, Sequence

from tools.dist.dist_tree_common import DEFAULT_OUTPUT_ROOT, DEFAULT_PLATFORM_TAG, DEFAULT_RELEASE_CHANNEL
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


CLEAN_ROOM_REPORT_ID = "dist.clean_room.v1"
CLEAN_ROOM_FINAL_REPORT_ID = "dist.clean_room.final.v1"
DEFAULT_RELEASE_TAG = "v0.0.0-{}".format(DEFAULT_RELEASE_CHANNEL)
DEFAULT_PLATFORM = DEFAULT_PLATFORM_TAG
DEFAULT_SEED = "456"
DEFAULT_MODE_POLICY = "cli"
DEFAULT_WORK_ROOT = os.path.join("build", "tmp", "dist3_clean_room")
DEFAULT_REPORT_DOC_PATH = "docs/audit/CLEAN_ROOM_{}.md"
DEFAULT_REPORT_JSON_PATH = "data/audit/clean_room_{}.json"
DEFAULT_FINAL_DOC_PATH = "docs/audit/DIST3_FINAL.md"
RULE_CLEAN_ROOM = "INV-CLEAN-ROOM-MUST-PASS-BEFORE-ARCHIVE"
LAST_REVIEWED = "2026-03-14"

WINDOWS_ABSOLUTE_RE = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z]:[\\/][^\s\"'<>|]+)")
UNC_ABSOLUTE_RE = re.compile(r"(?<![A-Za-z]:)(\\\\[^\\/\s\"'<>|]+[\\/][^\s\"'<>|]+)")
UNIX_ABSOLUTE_RE = re.compile(r"(?<![A-Za-z0-9_])(/(?:Users|home|tmp|private|var|opt)/[^\s\"'<>|]+)")


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(str(path or "")))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/").lstrip("./")


def _repo_rel_or_abs(repo_root: str, path: str) -> str:
    abs_path = _norm(path)
    root = _norm(repo_root) if _token(repo_root) else ""
    if root:
        try:
            if os.path.commonpath([os.path.normcase(root), os.path.normcase(abs_path)]) == os.path.normcase(root):
                return _norm_rel(os.path.relpath(abs_path, root))
        except ValueError:
            pass
    return _norm_rel(abs_path)


def _platform_slug(platform_tag: str) -> str:
    token = _token(platform_tag) or DEFAULT_PLATFORM
    return "".join(char if char.isalnum() else "_" for char in token)


def _default_bundle_root(dist_root: str, platform_tag: str) -> str:
    root = _norm(dist_root or DEFAULT_OUTPUT_ROOT)
    if os.path.isfile(os.path.join(root, "install.manifest.json")):
        return root
    return os.path.join(root, DEFAULT_RELEASE_TAG, _token(platform_tag) or DEFAULT_PLATFORM, "dominium")


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


def _report_doc_rel(platform_tag: str) -> str:
    return DEFAULT_REPORT_DOC_PATH.format(_platform_slug(platform_tag))


def _report_json_rel(platform_tag: str) -> str:
    return DEFAULT_REPORT_JSON_PATH.format(_platform_slug(platform_tag))


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


def _walk_strings(value: object, *, prefix: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key in sorted(value):
            next_prefix = str(key) if not prefix else "{}.{}".format(prefix, key)
            yield from _walk_strings(value[key], prefix=next_prefix)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            next_prefix = "{}[{}]".format(prefix, index) if prefix else "[{}]".format(index)
            yield from _walk_strings(item, prefix=next_prefix)
        return
    if isinstance(value, str):
        yield (prefix or "<root>", value)


def _find_scalar_values(value: object, *, keys: set[str]) -> list[str]:
    values: list[str] = []
    if isinstance(value, Mapping):
        for key in sorted(value):
            item = value[key]
            if str(key) in keys:
                token = _token(item)
                if token:
                    values.append(token)
            values.extend(_find_scalar_values(item, keys=keys))
        return values
    if isinstance(value, list):
        for item in value:
            values.extend(_find_scalar_values(item, keys=keys))
    return values


def _is_path_within_root(path: str, root: str) -> bool:
    abs_path = _norm(path)
    abs_root = _norm(root)
    try:
        return os.path.commonpath([os.path.normcase(abs_root), os.path.normcase(abs_path)]) == os.path.normcase(abs_root)
    except ValueError:
        return False


def _sanitize_text(text: str, bundle_root: str) -> str:
    value = str(text or "")
    abs_root = _norm(bundle_root)
    variants = sorted(
        {
            abs_root,
            abs_root.replace("\\", "/"),
            abs_root.replace("/", "\\"),
        },
        key=len,
        reverse=True,
    )
    for token in variants:
        if token:
            value = value.replace(token, "<bundle_root>")
    return value


def _sanitize_value(value: object, bundle_root: str) -> object:
    if isinstance(value, Mapping):
        return {str(key): _sanitize_value(value[key], bundle_root) for key in sorted(value)}
    if isinstance(value, list):
        return [_sanitize_value(item, bundle_root) for item in value]
    if isinstance(value, str):
        return _sanitize_text(value, bundle_root)
    return value


def _text_absolute_path_hits(text: str, bundle_root: str, *, location: str) -> list[dict]:
    hits: list[dict] = []
    text_value = str(text or "")
    for matched in WINDOWS_ABSOLUTE_RE.findall(text_value):
        hits.append(
            {
                "location": location,
                "kind": "windows",
                "value": _sanitize_text(_token(matched), bundle_root),
                "external": not _is_path_within_root(_token(matched), bundle_root),
            }
        )
    for match in UNC_ABSOLUTE_RE.finditer(text_value):
        matched = _token(match.group(1) if match.lastindex else match.group(0))
        start = int(match.start(1) if match.lastindex else match.start(0))
        boundary = max(text_value.rfind(token, 0, start) for token in (" ", "\n", "\r", "\t", "\"", "'", "<", ">", "|"))
        prefix = text_value[boundary + 1 : start]
        if re.search(r"[A-Za-z]:\\\\", prefix):
            continue
        hits.append(
            {
                "location": location,
                "kind": "unc",
                "value": _sanitize_text(matched, bundle_root),
                "external": True,
            }
        )
    for matched in UNIX_ABSOLUTE_RE.findall(text_value):
        hits.append(
            {
                "location": location,
                "kind": "unix",
                "value": _sanitize_text(_token(matched), bundle_root),
                "external": not _is_path_within_root(_token(matched), bundle_root),
            }
        )
    return hits


def absolute_path_hits(value: object, bundle_root: str, *, location: str = "payload") -> list[dict]:
    hits: list[dict] = []
    if isinstance(value, Mapping) or isinstance(value, list):
        for field_path, field_value in _walk_strings(value):
            hits.extend(_text_absolute_path_hits(field_value, bundle_root, location="{}.{}".format(location, field_path)))
        return sorted(hits, key=lambda row: (_token(row.get("location")), _token(row.get("kind")), _token(row.get("value"))))
    return sorted(
        _text_absolute_path_hits(str(value or ""), bundle_root, location=location),
        key=lambda row: (_token(row.get("location")), _token(row.get("kind")), _token(row.get("value"))),
    )


def build_clean_room_step_plan(seed: str, mode_policy: str) -> list[dict]:
    return [
        {"step_id": "setup_install_status", "kind": "product", "product_id": "setup", "argv": ["install", "status"]},
        {"step_id": "vpath_probe", "kind": "inline_python", "label": "virtual path probe"},
        {
            "step_id": "setup_verify",
            "kind": "product",
            "product_id": "setup",
            "argv": ["verify", "--root", ".", "--release-manifest", "manifests/release_manifest.json"],
        },
        {"step_id": "launcher_instances_list", "kind": "product", "product_id": "launcher", "argv": ["instances", "list"]},
        {"step_id": "launcher_compat_status", "kind": "product", "product_id": "launcher", "argv": ["compat-status"]},
        {"step_id": "launcher_start", "kind": "product", "product_id": "launcher", "argv": ["launcher", "start", "--seed", str(seed)]},
        {"step_id": "launcher_status", "kind": "product", "product_id": "launcher", "argv": ["launcher", "status"]},
        {"step_id": "launcher_attach_all", "kind": "product", "product_id": "launcher", "argv": ["launcher", "attach", "--all"]},
        {"step_id": "teleport_chain", "kind": "inline_python", "label": "teleport chain"},
        {"step_id": "tool_session", "kind": "inline_python", "label": "tool scan/edit/logic session"},
        {"step_id": "diag_capture", "kind": "inline_python", "label": "diag capture"},
        {"step_id": "replay_verify", "kind": "inline_python", "label": "diag replay verify"},
        {"step_id": "launcher_stop", "kind": "product", "product_id": "launcher", "argv": ["launcher", "stop"]},
    ]


def _mode_override(mode_policy: str) -> list[str]:
    policy = _token(mode_policy).lower() or DEFAULT_MODE_POLICY
    if policy == "gui":
        return ["--mode", "rendered"]
    if policy == "tui":
        return ["--mode", "tui"]
    return ["--mode", "cli"]


def _run_process(
    command: Sequence[str],
    *,
    cwd: str,
    env: Mapping[str, str],
    stdin_text: str = "",
) -> dict:
    proc = subprocess.run(
        [str(item) for item in list(command or [])],
        cwd=_norm(cwd),
        check=False,
        capture_output=True,
        input=str(stdin_text or ""),
        text=True,
        encoding="utf-8",
        env=dict(env),
    )
    stdout = str(proc.stdout or "")
    stderr = str(proc.stderr or "")
    json_rows = _extract_json_objects(stdout)
    return {
        "returncode": int(proc.returncode or 0),
        "stdout": stdout,
        "stderr": stderr,
        "json_rows": json_rows,
        "first_json": dict(json_rows[0]) if json_rows else {},
    }


def _run_bundle_product(bundle_root: str, product_id: str, argv: Sequence[str], *, env: Mapping[str, str], mode_policy: str) -> dict:
    wrapper_path = os.path.join(_norm(bundle_root), "bin", _token(product_id))
    command = [sys.executable, wrapper_path] + _mode_override(mode_policy) + [str(item) for item in list(argv or [])]
    return _run_process(command, cwd=bundle_root, env=env)


def _run_inline_python(bundle_root: str, script_text: str, *, env: Mapping[str, str]) -> dict:
    return _run_process([sys.executable, "-"], cwd=bundle_root, env=env, stdin_text=script_text)


def _inline_vpath_probe_script(mode_policy: str) -> str:
    del mode_policy
    return "\n".join(
        [
            "import json",
            "import os",
            "from src.appshell.paths import vpath_init",
            "payload = vpath_init({",
            "    'repo_root': '.',",
            "    'product_id': 'launcher',",
            "    'raw_args': [],",
            "    'executable_path': os.path.join(os.getcwd(), 'launcher'),",
            "})",
            "print(json.dumps({",
            "    'result': str(payload.get('result', '')).strip(),",
            "    'install_discovery': dict(payload.get('install_discovery') or {}),",
            "    'roots': dict(payload.get('roots') or {}),",
            "    'search_roots': dict(payload.get('search_roots') or {}),",
            "    'warnings': list(payload.get('warnings') or []),",
            "    'deterministic_fingerprint': str(payload.get('deterministic_fingerprint', '')).strip(),",
            "}, indent=2, sort_keys=True))",
        ]
    )


def _inline_teleport_script(seed: str) -> str:
    return "\n".join(
        [
            "import json",
            "from src.client.ui.teleport_controller import build_teleport_plan",
            "from src.worldgen.mw.sol_anchor import resolve_sol_anchor_cell_key",
            "from src.worldgen.mw.system_query_engine import list_systems_in_cell",
            "from tools.mvp.runtime_bundle import build_default_universe_identity",
            "",
            "seed = {!r}".format(str(seed)),
            "identity = build_default_universe_identity(repo_root='.', seed=seed, authority_mode='dev')",
            "anchor = resolve_sol_anchor_cell_key()",
            "rows = []",
            "primary = list_systems_in_cell(universe_identity=identity, geo_cell_key=anchor, refinement_level=1, cache_enabled=True)",
            "rows.extend([dict(row) for row in list(primary.get('systems') or []) if isinstance(row, dict)])",
            "base_index = [int(item) for item in list(anchor.get('index_tuple') or [0, 0, 0])]",
            "base_index.extend([0] * max(0, 3 - len(base_index)))",
            "for dx in (-1, 0, 1):",
            "    for dy in (-1, 0, 1):",
            "        cell_key = dict(anchor)",
            "        cell_key['index_tuple'] = [int(base_index[0] + dx), int(base_index[1] + dy), int(base_index[2])]",
            "        listing = list_systems_in_cell(universe_identity=identity, geo_cell_key=cell_key, refinement_level=1, cache_enabled=True)",
            "        rows.extend([dict(row) for row in list(listing.get('systems') or []) if isinstance(row, dict)])",
            "deduped = {}",
            "for row in rows:",
            "    object_id = str(dict(row).get('object_id', '')).strip()",
            "    if object_id:",
            "        deduped[object_id] = dict(row)",
            "candidate_rows = [dict(deduped[key]) for key in sorted(deduped.keys())]",
            "commands = ['sol', 'earth', 'random_star', 'earth']",
            "results = []",
            "for index, command in enumerate(commands):",
            "    plan = build_teleport_plan(",
            "        repo_root='.',",
            "        command=command,",
            "        universe_seed=seed,",
            "        authority_mode='dev',",
            "        teleport_counter=index,",
            "        candidate_system_rows=candidate_rows,",
            "    )",
            "    results.append({",
            "        'command': command,",
            "        'result': str(plan.get('result', '')).strip(),",
            "        'target_kind': str(plan.get('target_kind', '')).strip(),",
            "        'target_object_id': str(plan.get('target_object_id', '')).strip(),",
            "        'fingerprint': str(plan.get('deterministic_fingerprint', '')).strip(),",
            "    })",
            "print(json.dumps({",
            "    'result': 'complete' if all(row['result'] == 'complete' for row in results) else 'refused',",
            "    'commands': results,",
            "    'candidate_count': len(candidate_rows),",
            "}, indent=2, sort_keys=True))",
        ]
    )


def _inline_tool_session_script() -> str:
    return "\n".join(
        [
            "import json",
            "from tools.embodiment.emb1_probe import build_tool_session_report",
            "payload = build_tool_session_report('.')",
            "print(json.dumps(payload, indent=2, sort_keys=True))",
        ]
    )


def _inline_diag_capture_script(seed: str) -> str:
    return "\n".join(
        [
            "import json",
            "from tools.diag.diag0_probe import capture_diag0_bundle",
            "payload = capture_diag0_bundle('.', out_dir='exports/diag0', tick_window=16, include_views=True)",
            "payload['seed'] = {!r}".format(str(seed)),
            "print(json.dumps(payload, indent=2, sort_keys=True))",
        ]
    )


def _inline_replay_script() -> str:
    return "\n".join(
        [
            "import json",
            "from tools.diag.diag0_probe import replay_diag0_bundle",
            "payload = replay_diag0_bundle('.', bundle_path='exports/diag0', tick_window=16)",
            "print(json.dumps(payload, indent=2, sort_keys=True))",
        ]
    )


def _prepare_clean_room_env(bundle_root: str) -> dict:
    root = _norm(bundle_root)
    env_root = os.path.join(root, "_clean_room_env")
    home_dir = os.path.join(env_root, "home")
    config_dir = os.path.join(env_root, "config")
    data_dir = os.path.join(env_root, "data")
    temp_dir = os.path.join(env_root, "temp")
    for path in (home_dir, config_dir, data_dir, temp_dir):
        os.makedirs(path, exist_ok=True)
    env_map = {}
    for key in (
        "COMSPEC",
        "NUMBER_OF_PROCESSORS",
        "OS",
        "PATHEXT",
        "PATH",
        "PROCESSOR_ARCHITECTURE",
        "PROCESSOR_IDENTIFIER",
        "PROCESSOR_LEVEL",
        "PROCESSOR_REVISION",
        "SYSTEMDRIVE",
        "SYSTEMROOT",
        "WINDIR",
    ):
        value = _token(os.environ.get(key))
        if value:
            env_map[key] = value
    env_map["HOME"] = home_dir
    env_map["USERPROFILE"] = home_dir
    env_map["APPDATA"] = config_dir
    env_map["LOCALAPPDATA"] = data_dir
    env_map["XDG_CONFIG_HOME"] = config_dir
    env_map["XDG_DATA_HOME"] = data_dir
    env_map["TMP"] = temp_dir
    env_map["TEMP"] = temp_dir
    return env_map


def _classify_hits_from_step(raw: Mapping[str, object], payload: object, bundle_root: str) -> dict:
    stdout_hits = absolute_path_hits(_token(raw.get("stdout")), bundle_root, location="stdout")
    stderr_hits = absolute_path_hits(_token(raw.get("stderr")), bundle_root, location="stderr")
    payload_hits = absolute_path_hits(payload, bundle_root, location="payload")
    rows = sorted(stdout_hits + stderr_hits + payload_hits, key=lambda row: (_token(row.get("location")), _token(row.get("kind")), _token(row.get("value"))))
    return {
        "rows": rows,
        "external_rows": [dict(row) for row in rows if bool(dict(row).get("external"))],
    }


def _step_summary(raw: Mapping[str, object], payload: object, bundle_root: str, *, step_id: str, command: str) -> dict:
    sanitized_payload = _sanitize_value(payload, bundle_root)
    sanitized_stdout = _sanitize_text(_token(raw.get("stdout")), bundle_root)
    sanitized_stderr = _sanitize_text(_token(raw.get("stderr")), bundle_root)
    hit_summary = _classify_hits_from_step(raw, payload, bundle_root)
    result_token = ""
    if isinstance(payload, Mapping):
        result_token = _token(dict(payload).get("result"))
        if not result_token and "product_id" in dict(payload):
            result_token = "descriptor"
    return {
        "step_id": _token(step_id),
        "command": _token(command),
        "returncode": int(raw.get("returncode", 0) or 0),
        "result": result_token,
        "payload": sanitized_payload,
        "stdout_fingerprint": canonical_sha256({"stdout": sanitized_stdout}),
        "stderr_fingerprint": canonical_sha256({"stderr": sanitized_stderr}),
        "payload_fingerprint": canonical_sha256({"payload": sanitized_payload}),
        "absolute_path_hits": hit_summary["rows"],
        "external_path_hits": hit_summary["external_rows"],
    }


def _assert_within_bundle(path_value: str, bundle_root: str) -> bool:
    token = _token(path_value)
    if not token:
        return True
    if token.startswith("<bundle_root>"):
        return True
    return _is_path_within_root(token, bundle_root)


def _scan_generated_outputs(bundle_root: str) -> list[dict]:
    rows: list[dict] = []
    for rel_prefix in ("store/runtime", "store/logs", "store/ipc", "exports"):
        abs_root = os.path.join(_norm(bundle_root), rel_prefix.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for current_root, dirnames, filenames in os.walk(abs_root):
            dirnames[:] = sorted(dirnames)
            rel_root = os.path.relpath(current_root, _norm(bundle_root))
            rel_root_norm = "" if rel_root in (".", "") else _norm_rel(rel_root)
            for name in sorted(filenames):
                rel_path = name if not rel_root_norm else "{}/{}".format(rel_root_norm, name)
                suffix = os.path.splitext(name)[1].lower()
                if suffix not in {".json", ".txt", ".md", ".log"} and name not in {"README", "LICENSE"}:
                    continue
                abs_path = os.path.join(current_root, name)
                try:
                    text = open(abs_path, "r", encoding="utf-8").read()
                except OSError:
                    continue
                for row in absolute_path_hits(text, bundle_root, location=rel_path):
                    if bool(dict(row).get("external")):
                        rows.append(dict(row))
    return sorted(rows, key=lambda row: (_token(row.get("location")), _token(row.get("kind")), _token(row.get("value"))))


def _reset_clean_room_runtime_roots(bundle_root: str) -> None:
    runtime_dirs = (
        "store/runtime",
        "store/logs",
        "store/ipc",
        "store/exports",
        "exports",
    )
    for rel_path in runtime_dirs:
        abs_path = os.path.join(_norm(bundle_root), rel_path.replace("/", os.sep))
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        os.makedirs(abs_path, exist_ok=True)


def _initial_report(
    source_bundle_root: str,
    *,
    repo_root: str,
    platform_tag: str,
    seed: str,
    mode_policy: str,
) -> dict:
    return {
        "report_id": CLEAN_ROOM_REPORT_ID,
        "result": "refused",
        "platform_tag": _token(platform_tag) or DEFAULT_PLATFORM,
        "seed": _token(seed) or DEFAULT_SEED,
        "mode_policy": _token(mode_policy).lower() or DEFAULT_MODE_POLICY,
        "source_bundle_root": _repo_rel_or_abs(repo_root, source_bundle_root),
        "step_plan": build_clean_room_step_plan(seed, mode_policy),
        "steps": [],
        "assertions": {},
        "errors": [],
        "warnings": [],
        "key_hashes": {},
        "deterministic_fingerprint": "",
    }


def _error(code: str, message: str, remediation: str, *, path: str = "", rule_id: str = RULE_CLEAN_ROOM) -> dict:
    return {
        "code": _token(code),
        "path": _token(path),
        "message": _token(message),
        "remediation": _token(remediation),
        "rule_id": _token(rule_id) or RULE_CLEAN_ROOM,
    }


def build_clean_room_report(
    source_bundle_root: str,
    *,
    platform_tag: str = DEFAULT_PLATFORM,
    seed: str = DEFAULT_SEED,
    mode_policy: str = DEFAULT_MODE_POLICY,
    repo_root: str = "",
    work_root: str = DEFAULT_WORK_ROOT,
) -> dict:
    repo_root_abs = _norm(repo_root) if _token(repo_root) else os.getcwd()
    source_root_abs = _default_bundle_root(source_bundle_root, platform_tag)
    report = _initial_report(source_root_abs, repo_root=repo_root_abs, platform_tag=platform_tag, seed=seed, mode_policy=mode_policy)
    if not os.path.isdir(source_root_abs):
        report["errors"] = [
            _error(
                "refusal.dist.missing_artifact",
                "source distribution bundle root is missing",
                "Run the DIST-1 assembly tool or provide a valid portable bundle root.",
                path=_repo_rel_or_abs(repo_root_abs, source_root_abs),
            )
        ]
        report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
        return report

    work_parent = _norm(os.path.join(repo_root_abs, work_root))
    os.makedirs(work_parent, exist_ok=True)
    started = False
    temp_root = tempfile.mkdtemp(prefix="dominium_dist3_", dir=work_parent)
    try:
        copied_bundle_root = os.path.join(temp_root, "dominium")
        shutil.copytree(source_root_abs, copied_bundle_root)
        _reset_clean_room_runtime_roots(copied_bundle_root)
        env_map = _prepare_clean_room_env(copied_bundle_root)
        step_outputs: list[dict] = []

        def run_step(step_id: str, raw: Mapping[str, object], payload: object, command: str) -> dict:
            step = _step_summary(raw, payload, copied_bundle_root, step_id=step_id, command=command)
            step_outputs.append(step)
            return step

        try:
            install_raw = _run_bundle_product(copied_bundle_root, "setup", ["install", "status"], env=env_map, mode_policy=mode_policy)
            install_payload = dict(install_raw.get("first_json") or {})
            install_step = run_step("setup_install_status", install_raw, install_payload, "setup install status")
            install_discovery = dict(install_payload.get("install_discovery") or {})
            if not install_discovery:
                install_discovery = dict(dict(install_payload.get("details") or {}).get("install_discovery") or {})
            if int(install_step.get("returncode", 0)) != 0 or _token(install_step.get("result")) != "complete":
                raise RuntimeError("setup_install_status")
            if _token(install_discovery.get("mode")).lower() != "portable":
                report["errors"].append(
                    _error(
                        "refusal.clean_room.portable_root_not_detected",
                        "portable adjacency was not selected during install discovery",
                        "Ensure install.manifest.json is adjacent to the copied portable bundle executables.",
                        path="install.manifest.json",
                    )
                )
                raise RuntimeError("setup_install_status")

            vpath_raw = _run_inline_python(copied_bundle_root, _inline_vpath_probe_script(mode_policy), env=env_map)
            vpath_payload = dict(vpath_raw.get("first_json") or {})
            vpath_step = run_step("vpath_probe", vpath_raw, vpath_payload, "inline:vpath_probe")
            if int(vpath_step.get("returncode", 0)) != 0 or _token(vpath_step.get("result")) != "complete":
                raise RuntimeError("vpath_probe")
            roots = dict(vpath_payload.get("roots") or {})
            if not roots or not all(_assert_within_bundle(str(value), copied_bundle_root) for value in roots.values()):
                report["errors"].append(
                    _error(
                        "refusal.clean_room.external_store_access",
                        "virtual roots resolved outside the copied bundle",
                        "Resolve portable adjacency through the copied install.manifest.json and keep all VROOTs inside the bundle.",
                        path="vpath.roots",
                    )
                )
                raise RuntimeError("vpath_probe")

            verify_raw = _run_bundle_product(
                copied_bundle_root,
                "setup",
                ["verify", "--root", ".", "--release-manifest", "manifests/release_manifest.json"],
                env=env_map,
                mode_policy=mode_policy,
            )
            verify_payload = dict(verify_raw.get("first_json") or {})
            verify_step = run_step("setup_verify", verify_raw, verify_payload, "setup verify --root . --release-manifest manifests/release_manifest.json")
            if int(verify_step.get("returncode", 0)) != 0 or _token(verify_step.get("result")) != "complete":
                raise RuntimeError("setup_verify")

            instances_raw = _run_bundle_product(copied_bundle_root, "launcher", ["instances", "list"], env=env_map, mode_policy=mode_policy)
            instances_payload = dict(instances_raw.get("first_json") or {})
            instances_step = run_step("launcher_instances_list", instances_raw, instances_payload, "launcher instances list")
            if int(instances_step.get("returncode", 0)) != 0 or _token(instances_step.get("result")) != "complete":
                raise RuntimeError("launcher_instances_list")

            compat_raw = _run_bundle_product(copied_bundle_root, "launcher", ["compat-status"], env=env_map, mode_policy=mode_policy)
            compat_payload = dict(compat_raw.get("first_json") or {})
            compat_step = run_step("launcher_compat_status", compat_raw, compat_payload, "launcher compat-status")
            if int(compat_step.get("returncode", 0)) != 0 or _token(compat_step.get("result")) != "complete":
                raise RuntimeError("launcher_compat_status")

            start_raw = _run_bundle_product(copied_bundle_root, "launcher", ["launcher", "start", "--seed", str(seed)], env=env_map, mode_policy=mode_policy)
            start_payload = dict(start_raw.get("first_json") or {})
            start_step = run_step("launcher_start", start_raw, start_payload, "launcher start --seed {}".format(_token(seed)))
            if int(start_step.get("returncode", 0)) != 0 or _token(start_step.get("result")) != "complete":
                raise RuntimeError("launcher_start")
            started = True

            status_raw = _run_bundle_product(copied_bundle_root, "launcher", ["launcher", "status"], env=env_map, mode_policy=mode_policy)
            status_payload = dict(status_raw.get("first_json") or {})
            status_step = run_step("launcher_status", status_raw, status_payload, "launcher status")
            if int(status_step.get("returncode", 0)) != 0 or _token(status_step.get("result")) != "complete":
                raise RuntimeError("launcher_status")

            attach_raw = _run_bundle_product(copied_bundle_root, "launcher", ["launcher", "attach", "--all"], env=env_map, mode_policy=mode_policy)
            attach_payload = dict(attach_raw.get("first_json") or {})
            attach_step = run_step("launcher_attach_all", attach_raw, attach_payload, "launcher attach --all")
            if int(attach_step.get("returncode", 0)) != 0 or _token(attach_step.get("result")) != "complete":
                raise RuntimeError("launcher_attach_all")

            teleport_raw = _run_inline_python(copied_bundle_root, _inline_teleport_script(seed), env=env_map)
            teleport_payload = dict(teleport_raw.get("first_json") or {})
            teleport_step = run_step("teleport_chain", teleport_raw, teleport_payload, "inline:teleport_chain")
            if int(teleport_step.get("returncode", 0)) != 0 or _token(teleport_step.get("result")) != "complete":
                raise RuntimeError("teleport_chain")

            tool_raw = _run_inline_python(copied_bundle_root, _inline_tool_session_script(), env=env_map)
            tool_payload = dict(tool_raw.get("first_json") or {})
            tool_step = run_step("tool_session", tool_raw, tool_payload, "inline:tool_session")
            if int(tool_step.get("returncode", 0)) != 0:
                raise RuntimeError("tool_session")

            diag_raw = _run_inline_python(copied_bundle_root, _inline_diag_capture_script(seed), env=env_map)
            diag_payload = dict(diag_raw.get("first_json") or {})
            diag_step = run_step("diag_capture", diag_raw, diag_payload, "inline:diag_capture")
            if int(diag_step.get("returncode", 0)) != 0 or _token(diag_step.get("result")) != "complete":
                raise RuntimeError("diag_capture")

            replay_raw = _run_inline_python(copied_bundle_root, _inline_replay_script(), env=env_map)
            replay_payload = dict(replay_raw.get("first_json") or {})
            replay_step = run_step("replay_verify", replay_raw, replay_payload, "inline:replay_verify")
            if int(replay_step.get("returncode", 0)) != 0 or _token(replay_step.get("result")) != "complete":
                raise RuntimeError("replay_verify")

            stop_raw = _run_bundle_product(copied_bundle_root, "launcher", ["launcher", "stop"], env=env_map, mode_policy=mode_policy)
            stop_payload = dict(stop_raw.get("first_json") or {})
            stop_step = _step_summary(stop_raw, stop_payload, copied_bundle_root, step_id="launcher_stop", command="launcher stop")
            step_outputs.append(stop_step)
            if int(stop_step.get("returncode", 0)) != 0 or _token(stop_step.get("result")) != "complete":
                raise RuntimeError("launcher_stop")
            started = False
        except RuntimeError as exc:
            failed_step = str(exc).strip()
            if not report["errors"]:
                report["errors"].append(
                    _error(
                        "refusal.clean_room.step_failed",
                        "clean-room step '{}' failed".format(failed_step),
                        "Inspect the clean-room step output and rerun the harness after fixing the portable bundle or runtime path.",
                        path=failed_step,
                    )
                )
            if started:
                stop_raw = _run_bundle_product(copied_bundle_root, "launcher", ["launcher", "stop"], env=env_map, mode_policy=mode_policy)
                stop_payload = dict(stop_raw.get("first_json") or {})
                step_outputs.append(_step_summary(stop_raw, stop_payload, copied_bundle_root, step_id="launcher_stop_cleanup", command="launcher stop"))

        report["steps"] = step_outputs
        generated_output_hits = _scan_generated_outputs(copied_bundle_root)
        if generated_output_hits:
            report["errors"].append(
                _error(
                    "refusal.clean_room.external_store_access",
                    "generated clean-room outputs contain external absolute paths",
                    "Keep all runtime, log, IPC, and export outputs inside the copied bundle root.",
                    path="generated_outputs",
                )
            )

        all_external_hits = []
        for step in step_outputs:
            all_external_hits.extend(list(dict(step).get("external_path_hits") or []))
        all_external_hits.extend(generated_output_hits)

        install_step_payload = dict(step_outputs[0].get("payload") or {}) if step_outputs else {}
        install_discovery = dict(install_step_payload.get("install_discovery") or {})
        if not install_discovery:
            install_discovery = dict(dict(install_step_payload.get("details") or {}).get("install_discovery") or {})
        vpath_step_payload = dict(step_outputs[1].get("payload") or {}) if len(step_outputs) > 1 else {}
        roots = dict(vpath_step_payload.get("roots") or {})
        attach_payload = {}
        status_payload = {}
        diag_payload = {}
        replay_payload = {}
        stop_payload = {}
        tool_payload = {}
        teleport_payload = {}
        for step in step_outputs:
            step_id = _token(step.get("step_id"))
            if step_id == "launcher_attach_all":
                attach_payload = dict(step.get("payload") or {})
            elif step_id == "launcher_status":
                status_payload = dict(step.get("payload") or {})
            elif step_id == "diag_capture":
                diag_payload = dict(step.get("payload") or {})
            elif step_id == "replay_verify":
                replay_payload = dict(step.get("payload") or {})
            elif step_id == "launcher_stop":
                stop_payload = dict(step.get("payload") or {})
            elif step_id == "tool_session":
                tool_payload = dict(step.get("payload") or {})
            elif step_id == "teleport_chain":
                teleport_payload = dict(step.get("payload") or {})

        attachments = list(attach_payload.get("attachments") or [])
        negotiation_hashes = sorted(
            set(
                _find_scalar_values(
                    [attach_payload, status_payload, stop_payload],
                    keys={"negotiation_record_hash", "negotiation_hash"},
                )
            )
        )
        negotiation_present = bool(attachments) and bool(negotiation_hashes)
        all_step_success = bool(step_outputs) and all(int(dict(step).get("returncode", 1)) == 0 for step in step_outputs)
        portable_detected = _token(install_discovery.get("mode")).lower() == "portable"
        vroots_inside_bundle = bool(roots) and all(_assert_within_bundle(str(value), copied_bundle_root) for value in roots.values())
        replay_step_ran = any(_token(dict(step).get("step_id")) == "replay_verify" for step in step_outputs)
        replay_validates = (not replay_step_ran) or (
            _token(replay_payload.get("result")) == "complete"
            and bool(dict(replay_payload.get("replay_result") or {}).get("hash_match", False))
        )
        tool_flow_valid = all(
            _token(dict(tool_payload.get(name) or {}).get("result")) == "complete"
            for name in ("scan", "mine", "fill", "probe", "trace", "teleport")
        )
        teleport_valid = _token(teleport_payload.get("result")) == "complete" and [
            _token(dict(row).get("command")) for row in list(teleport_payload.get("commands") or [])
        ] == ["sol", "earth", "random_star", "earth"]

        report["assertions"] = {
            "portable_root_detected": portable_detected,
            "virtual_paths_within_bundle": vroots_inside_bundle,
            "pack_verification_passed": any(_token(dict(step).get("step_id")) == "setup_verify" and _token(dict(step).get("result")) == "complete" for step in step_outputs),
            "negotiation_records_present": negotiation_present,
            "no_external_absolute_paths": not all_external_hits,
            "replay_validates_determinism": replay_validates,
            "exit_codes_all_success": all_step_success,
            "tool_session_complete": tool_flow_valid,
            "teleport_chain_complete": teleport_valid,
        }
        report["key_hashes"] = {
            "diag_bundle_hash": _token(diag_payload.get("bundle_hash")).lower(),
            "replay_bundle_hash": _token(replay_payload.get("bundle_hash")).lower(),
            "replay_result_fingerprint": _token(dict(replay_payload.get("replay_result") or {}).get("deterministic_fingerprint")).lower(),
            "tool_session_fingerprint": _token(tool_payload.get("deterministic_fingerprint")).lower(),
            "teleport_chain_fingerprint": canonical_sha256({"commands": list(teleport_payload.get("commands") or [])}) if teleport_payload else "",
        }

        if not report["errors"] and all(bool(value) for value in report["assertions"].values()):
            report["result"] = "complete"
        else:
            report["result"] = "refused"
            if not portable_detected:
                report["errors"].append(
                    _error(
                        "refusal.clean_room.portable_root_not_detected",
                        "portable install discovery did not resolve through adjacency",
                        "Ensure the copied bundle retains install.manifest.json adjacent to the portable binaries.",
                        path="install.manifest.json",
                    )
                )
            if not vroots_inside_bundle:
                report["errors"].append(
                    _error(
                        "refusal.clean_room.external_store_access",
                        "virtual roots escaped the copied bundle",
                        "Use portable adjacency and virtual roots only within the copied bundle.",
                        path="vpath.roots",
                    )
                )
            if all_external_hits:
                report["errors"].append(
                    _error(
                        "refusal.clean_room.absolute_path_leak",
                        "external absolute paths were emitted during the clean-room run",
                        "Remove external path references and keep all runtime output inside the copied bundle.",
                        path="stdout/stderr",
                    )
                )
            if replay_step_ran and not replay_validates:
                report["errors"].append(
                    _error(
                        "refusal.clean_room.replay_failed",
                        "DIAG replay verification failed in the clean-room bundle",
                        "Capture a new deterministic repro bundle and inspect the replay mismatch payload.",
                        path="exports/diag0",
                    )
                )

        report["warnings"] = sorted(
            set(
                _token(item)
                for item in list(install_discovery.get("warnings") or []) + list(vpath_step_payload.get("warnings") or [])
                if _token(item)
            )
        )
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
    report["errors"] = sorted(
        [dict(item) for item in list(report.get("errors") or []) if isinstance(item, Mapping)],
        key=lambda row: (_token(row.get("rule_id")), _token(row.get("code")), _token(row.get("path")), _token(row.get("message"))),
    )
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_clean_room_report(report: Mapping[str, object]) -> str:
    row = dict(report or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-4 platform clean-room matrix",
        "",
        "# Clean Room - {}".format(_token(row.get("platform_tag")) or DEFAULT_PLATFORM),
        "",
        "- result: `{}`".format(_token(row.get("result"))),
        "- source_bundle_root: `{}`".format(_token(row.get("source_bundle_root"))),
        "- seed: `{}`".format(_token(row.get("seed"))),
        "- mode_policy: `{}`".format(_token(row.get("mode_policy"))),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "",
        "## Assertions",
        "",
    ]
    for key in sorted(dict(row.get("assertions") or {})):
        lines.append("- `{}`: `{}`".format(key, bool(dict(row.get("assertions") or {}).get(key))))
    lines.extend(["", "## Steps", ""])
    for step in list(row.get("steps") or []):
        item = dict(step or {})
        lines.append(
            "- `{}` returncode=`{}` result=`{}` payload_fingerprint=`{}`".format(
                _token(item.get("step_id")),
                int(item.get("returncode", 0) or 0),
                _token(item.get("result")),
                _token(item.get("payload_fingerprint")),
            )
        )
    lines.extend(["", "## Key Hashes", ""])
    for key in sorted(dict(row.get("key_hashes") or {})):
        lines.append("- `{}`: `{}`".format(key, _token(dict(row.get("key_hashes") or {}).get(key))))
    lines.extend(["", "## Errors", ""])
    errors = list(row.get("errors") or [])
    if not errors:
        lines.append("- none")
    else:
        for item in errors:
            error_row = dict(item or {})
            lines.append(
                "- `{}` `{}`: {}. remediation: {}".format(
                    _token(error_row.get("code")),
                    _token(error_row.get("path")),
                    _token(error_row.get("message")),
                    _token(error_row.get("remediation")),
                )
            )
    lines.extend(["", "## Warnings", ""])
    warnings = list(row.get("warnings") or [])
    if not warnings:
        lines.append("- none")
    else:
        for item in warnings:
            lines.append("- `{}`".format(_token(item)))
    return "\n".join(lines) + "\n"


def build_dist3_final_report(reports: Sequence[Mapping[str, object]]) -> dict:
    normalized = sorted([dict(item or {}) for item in list(reports or []) if isinstance(item, Mapping)], key=lambda row: (_token(row.get("platform_tag")), _token(row.get("source_bundle_root"))))
    payload = {
        "report_id": CLEAN_ROOM_FINAL_REPORT_ID,
        "result": "complete" if normalized and all(_token(row.get("result")) == "complete" for row in normalized) else "refused",
        "platforms": [_token(row.get("platform_tag")) for row in normalized],
        "report_fingerprints": {_token(row.get("platform_tag")): _token(row.get("deterministic_fingerprint")) for row in normalized},
        "failure_count": int(sum(len(list(dict(row).get("errors") or [])) for row in normalized)),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def render_dist3_final(report: Mapping[str, object], reports: Sequence[Mapping[str, object]]) -> str:
    row = dict(report or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-4 platform matrix and archive verification",
        "",
        "# DIST3 Final",
        "",
        "- result: `{}`".format(_token(row.get("result"))),
        "- platforms: `{}`".format(", ".join(_token(item) for item in list(row.get("platforms") or [])) or "none"),
        "- failure_count: `{}`".format(int(row.get("failure_count") or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "",
        "## Per-Platform Results",
        "",
    ]
    for item in sorted([dict(value or {}) for value in list(reports or []) if isinstance(value, Mapping)], key=lambda current: _token(current.get("platform_tag"))):
        lines.append(
            "- `{}` result=`{}` source=`{}` fingerprint=`{}`".format(
                _token(item.get("platform_tag")),
                _token(item.get("result")),
                _token(item.get("source_bundle_root")),
                _token(item.get("deterministic_fingerprint")),
            )
        )
    lines.extend(["", "## Readiness", "", "- DIST-4 platform matrix: {}".format("ready" if _token(row.get("result")) == "complete" else "blocked"), ""])
    return "\n".join(lines) + "\n"


def write_clean_room_outputs(
    repo_root: str,
    report: Mapping[str, object],
    *,
    report_path: str = "",
    doc_path: str = "",
) -> dict:
    root = _norm(repo_root) if _token(repo_root) else os.getcwd()
    platform_tag = _token(dict(report or {}).get("platform_tag")) or DEFAULT_PLATFORM
    report_rel = report_path or _report_json_rel(platform_tag)
    doc_rel = doc_path or _report_doc_rel(platform_tag)
    report_abs = report_rel if os.path.isabs(report_rel) else os.path.join(root, report_rel.replace("/", os.sep))
    doc_abs = doc_rel if os.path.isabs(doc_rel) else os.path.join(root, doc_rel.replace("/", os.sep))
    _write_json(report_abs, report)
    _write_text(doc_abs, render_clean_room_report(report))
    return {
        "report_path": _repo_rel_or_abs(root, report_abs),
        "doc_path": _repo_rel_or_abs(root, doc_abs),
    }


def write_dist3_final_outputs(
    repo_root: str,
    reports: Sequence[Mapping[str, object]],
    *,
    final_doc_path: str = DEFAULT_FINAL_DOC_PATH,
) -> dict:
    root = _norm(repo_root) if _token(repo_root) else os.getcwd()
    final = build_dist3_final_report(reports)
    doc_abs = final_doc_path if os.path.isabs(final_doc_path) else os.path.join(root, final_doc_path.replace("/", os.sep))
    _write_text(doc_abs, render_dist3_final(final, reports))
    return {
        "final_doc_path": _repo_rel_or_abs(root, doc_abs),
        "final_report": final,
    }


def load_clean_room_report(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM) -> dict:
    path = os.path.join(_norm(repo_root), _report_json_rel(platform_tag).replace("/", os.sep))
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def clean_room_violations(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM) -> list[dict]:
    payload = load_clean_room_report(repo_root, platform_tag=platform_tag)
    if not payload:
        return [
            {
                "code": "clean_room_report_missing",
                "file_path": _report_json_rel(platform_tag),
                "message": "clean-room machine report is missing",
                "rule_id": RULE_CLEAN_ROOM,
            }
        ]
    if _token(payload.get("result")) == "complete":
        return []
    violations = []
    for item in list(payload.get("errors") or []):
        row = dict(item or {})
        violations.append(
            {
                "code": _token(row.get("code")) or "clean_room_error",
                "file_path": _token(row.get("path")) or _report_json_rel(platform_tag),
                "message": _token(row.get("message")) or "clean-room validation failed",
                "rule_id": _token(row.get("rule_id")) or RULE_CLEAN_ROOM,
            }
        )
    return sorted(violations, key=lambda row: (_token(row.get("rule_id")), _token(row.get("code")), _token(row.get("file_path")), _token(row.get("message"))))


__all__ = [
    "CLEAN_ROOM_REPORT_ID",
    "DEFAULT_FINAL_DOC_PATH",
    "DEFAULT_MODE_POLICY",
    "DEFAULT_PLATFORM",
    "DEFAULT_SEED",
    "DEFAULT_WORK_ROOT",
    "RULE_CLEAN_ROOM",
    "absolute_path_hits",
    "build_clean_room_report",
    "build_clean_room_step_plan",
    "build_dist3_final_report",
    "clean_room_violations",
    "load_clean_room_report",
    "render_clean_room_report",
    "render_dist3_final",
    "write_clean_room_outputs",
    "write_dist3_final_outputs",
]
