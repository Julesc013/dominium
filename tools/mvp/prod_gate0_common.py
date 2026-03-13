"""Deterministic reporting and enforcement helpers for PROD-GATE-0."""

from __future__ import annotations

import io
import importlib
import json
import os
import shutil
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from typing import Callable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.lib.install import registry_add_install, validate_install_manifest  # noqa: E402
from tools.appshell.appshell4_probe import run_ipc_attach_probe  # noqa: E402
from tools.release.ui_mode_resolution_common import build_test_probe, selection_for_product  # noqa: E402
from tools.setup.setup_cli import install_manifest_payload  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


PRODUCT_BOOT_MATRIX_DOC_PATH = "docs/mvp/PRODUCT_BOOT_MATRIX.md"
PRODUCT_BOOT_MATRIX_REPORT_PATH = "docs/audit/PRODUCT_BOOT_MATRIX_REPORT.md"
PRODUCT_BOOT_MATRIX_JSON_PATH = "data/audit/product_boot_matrix.json"
PROD_GATE_FINAL_PATH = "docs/audit/PROD_GATE_FINAL.md"
PRODUCT_BOOT_MATRIX_TOOL_PATH = "tools/mvp/tool_run_product_boot_matrix.py"
PRODUCT_BOOT_MATRIX_REPORT_ID = "mvp.product_boot_matrix.v1"
PRODUCT_BOOT_MATRIX_WORK_ROOT_REL = os.path.join("build", "mvp", "prod_gate0")
PRODUCT_REGISTRY_REL = os.path.join("data", "registries", "product_registry.json")
DIST_MANIFEST_REL = os.path.join("dist", "manifest.json")
SEMANTIC_CONTRACT_REGISTRY_REL = os.path.join("data", "registries", "semantic_contract_registry.json")
PORTABLE_INSTALL_ID = "install.prod_gate0.portable"
INSTALLED_INSTALL_ID = "install.prod_gate0.installed"
DEFAULT_PRODUCT_VERSION = "0.0.0"
COMMAND_ORDER = ("descriptor", "help", "compat-status", "validate")
MODE_SCENARIO_ORDER = ("tty", "gui", "headless", "requested_context")

PRODUCT_RUNTIME_ROWS = (
    {
        "product_id": "client",
        "display_name": "Client",
        "kind": "client",
        "entry_module": "tools.mvp.runtime_entry",
        "entry_function": "client_main",
        "invocation_handler": "direct",
        "portable_executable_name": "client",
        "installed_executable_name": "client",
        "manifest_binary_names": ("dominium_client", "client"),
        "required_commands": ("--descriptor", "help", "compat-status", "validate --all --profile FAST"),
        "expected_refusal_codes": ("refusal.install.not_found", "refusal.compat.feature_disabled"),
    },
    {
        "product_id": "engine",
        "display_name": "Engine",
        "kind": "engine",
        "entry_module": "tools.appshell.product_stub_cli",
        "entry_function": "main",
        "invocation_handler": "stub",
        "portable_executable_name": "engine",
        "installed_executable_name": "engine",
        "manifest_binary_names": ("dominium_engine", "engine"),
        "required_commands": ("--descriptor", "help", "compat-status", "validate --all --profile FAST"),
        "expected_refusal_codes": ("refusal.install.not_found", "refusal.compat.feature_disabled"),
    },
    {
        "product_id": "game",
        "display_name": "Game",
        "kind": "game",
        "entry_module": "tools.appshell.product_stub_cli",
        "entry_function": "main",
        "invocation_handler": "stub",
        "portable_executable_name": "game",
        "installed_executable_name": "game",
        "manifest_binary_names": ("dominium_game", "game"),
        "required_commands": ("--descriptor", "help", "compat-status", "validate --all --profile FAST"),
        "expected_refusal_codes": ("refusal.install.not_found", "refusal.compat.feature_disabled"),
    },
    {
        "product_id": "launcher",
        "display_name": "Launcher",
        "kind": "launcher",
        "entry_module": "tools.launcher.launch",
        "entry_function": "main",
        "invocation_handler": "direct",
        "portable_executable_name": "launcher",
        "installed_executable_name": "launcher",
        "manifest_binary_names": ("dominium_launcher", "launcher"),
        "required_commands": ("--descriptor", "help", "compat-status", "validate --all --profile FAST"),
        "expected_refusal_codes": ("refusal.install.not_found", "refusal.compat.feature_disabled"),
    },
    {
        "product_id": "server",
        "display_name": "Server",
        "kind": "server",
        "entry_module": "src.server.server_main",
        "entry_function": "main",
        "invocation_handler": "direct",
        "portable_executable_name": "server",
        "installed_executable_name": "server",
        "manifest_binary_names": ("dominium_server", "server"),
        "required_commands": ("--descriptor", "help", "compat-status", "validate --all --profile FAST"),
        "expected_refusal_codes": ("refusal.install.not_found", "refusal.compat.feature_disabled"),
    },
    {
        "product_id": "setup",
        "display_name": "Setup",
        "kind": "setup",
        "entry_module": "tools.setup.setup_cli",
        "entry_function": "main",
        "invocation_handler": "direct",
        "portable_executable_name": "setup",
        "installed_executable_name": "setup",
        "manifest_binary_names": ("dominium_setup", "setup"),
        "required_commands": ("--descriptor", "help", "compat-status", "validate --all --profile FAST"),
        "expected_refusal_codes": ("refusal.install.not_found", "refusal.compat.feature_disabled"),
    },
    {
        "product_id": "tool.attach_console_stub",
        "display_name": "Tools",
        "kind": "tool",
        "entry_module": "tools.appshell.product_stub_cli",
        "entry_function": "main",
        "invocation_handler": "stub",
        "portable_executable_name": "tool_attach_console_stub",
        "installed_executable_name": "tool_attach_console_stub",
        "manifest_binary_names": ("tool_attach_console_stub",),
        "required_commands": ("--descriptor", "help", "compat-status", "validate --all --profile FAST"),
        "expected_refusal_codes": ("refusal.install.not_found", "refusal.compat.feature_disabled"),
    },
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _int_value(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _safe_rel(path: str, base: str) -> str:
    try:
        rel_path = os.path.relpath(_norm(path), _norm(base)).replace("\\", "/")
    except ValueError:
        return _norm(path).replace("\\", "/")
    return rel_path if not rel_path.startswith("../") else _norm(path).replace("\\", "/")


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    abs_path = _norm(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload or {}), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_text(path: str, text: str) -> None:
    abs_path = _norm(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text))


def _canonical_fingerprint(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(payload or {}, deterministic_fingerprint=""))


def _load_product_registry(repo_root: str) -> dict[str, dict]:
    payload, error = _read_json(os.path.join(repo_root, PRODUCT_REGISTRY_REL.replace("/", os.sep)))
    if error:
        return {}
    rows = list(_as_map(payload.get("record")).get("products") or [])
    return {
        _token(dict(row or {}).get("product_id")): dict(row or {})
        for row in rows
        if _token(dict(row or {}).get("product_id"))
    }


def _dist_versions(repo_root: str) -> dict:
    payload, _error = _read_json(os.path.join(repo_root, DIST_MANIFEST_REL.replace("/", os.sep)))
    compatibility_version = _token(payload.get("compatibility_version")) or "1.0.0"
    return {
        "engine_version": _token(payload.get("engine_version")) or DEFAULT_PRODUCT_VERSION,
        "game_version": _token(payload.get("client_version")) or _token(payload.get("server_version")) or DEFAULT_PRODUCT_VERSION,
        "launcher_version": _token(payload.get("launcher_version")) or DEFAULT_PRODUCT_VERSION,
        "setup_version": _token(payload.get("setup_version")) or DEFAULT_PRODUCT_VERSION,
        "protocol_network": compatibility_version,
        "protocol_save": compatibility_version,
        "protocol_mod": compatibility_version,
        "protocol_replay": compatibility_version,
        "trust_tier": "official",
    }


def _store_root_payload(root_path: str, mode_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "store_id": "store.{}".format(_token(mode_id) or "default"),
        "store_mode": _token(mode_id) or "default",
        "root_path": ".",
        "extensions": {},
    }


def _fixture_binary_content(product_id: str, executable_name: str) -> str:
    return "# PROD-GATE-0 fixture executable\nproduct_id={}\nexecutable={}\n".format(
        _token(product_id),
        _token(executable_name),
    )


def _ensure_fixture_binary(path: str, *, product_id: str, executable_name: str) -> None:
    _write_text(path, _fixture_binary_content(product_id, executable_name))


def _prepare_mode_store_dirs(root_path: str) -> None:
    for rel_path in ("packs", "profiles", "locks", "instances", "saves", "exports", "logs", "runtime"):
        os.makedirs(os.path.join(root_path, rel_path), exist_ok=True)


def _portable_top_level_names(row: Mapping[str, object]) -> tuple[str, ...]:
    names = [_token(row.get("portable_executable_name"))]
    for name in list(row.get("manifest_binary_names") or []):
        token = _token(name)
        if token and token not in names:
            names.append(token)
    return tuple(name for name in names if name)


def _populate_fixture_binaries(root_path: str) -> None:
    bin_root = os.path.join(root_path, "bin")
    os.makedirs(bin_root, exist_ok=True)
    for row in PRODUCT_RUNTIME_ROWS:
        product_id = _token(row.get("product_id"))
        for executable_name in list(row.get("manifest_binary_names") or []):
            token = _token(executable_name)
            if token:
                _ensure_fixture_binary(os.path.join(bin_root, token), product_id=product_id, executable_name=token)
        if product_id == "tool.attach_console_stub":
            continue
        for executable_name in _portable_top_level_names(row):
            _ensure_fixture_binary(os.path.join(root_path, executable_name), product_id=product_id, executable_name=executable_name)


def _semantic_contract_registry_payload(repo_root: str) -> dict:
    payload, _error = _read_json(os.path.join(repo_root, SEMANTIC_CONTRACT_REGISTRY_REL.replace("/", os.sep)))
    return payload


def _prepare_install_fixture(
    repo_root: str,
    *,
    root_path: str,
    install_id: str,
    install_mode: str,
    store_root: str,
) -> dict:
    shutil.rmtree(root_path, ignore_errors=True)
    os.makedirs(root_path, exist_ok=True)
    _populate_fixture_binaries(root_path)
    _prepare_mode_store_dirs(store_root)
    _write_json(os.path.join(store_root, "store.root.json"), _store_root_payload(store_root, install_mode))
    _write_json(os.path.join(root_path, "semantic_contract_registry.json"), _semantic_contract_registry_payload(repo_root))
    manifest_payload = install_manifest_payload(
        install_id=install_id,
        install_root=root_path,
        store_root=store_root,
        mode=install_mode,
        created_at="2000-01-01T00:00:00Z",
        build_number=0,
        versions=_dist_versions(repo_root),
        stage_root=root_path,
    )
    validation = validate_install_manifest(
        repo_root=repo_root,
        install_manifest_path=os.path.join(root_path, "install.manifest.json"),
        manifest_payload=manifest_payload,
    )
    if _token(validation.get("result")) != "complete":
        raise ValueError("fixture install manifest validation failed for {} ({})".format(install_id, _token(validation.get("refusal_code"))))
    _write_json(os.path.join(root_path, "install.manifest.json"), manifest_payload)
    return manifest_payload


def _prepare_fixture_layout(repo_root: str, *, work_root: str = "") -> dict:
    work_root = _norm(work_root) if _token(work_root) else os.path.join(repo_root, PRODUCT_BOOT_MATRIX_WORK_ROOT_REL.replace("/", os.sep))
    portable_root = os.path.join(work_root, "portable")
    installed_root = os.path.join(work_root, "installed")
    installed_store_root = os.path.join(installed_root, "store")
    registry_roots = (
        os.path.join(work_root, "config_posix", "dominium"),
        os.path.join(work_root, "config_win", "Dominium"),
    )
    registry_path = os.path.join(registry_roots[0], "install_registry.json")
    portable_manifest = _prepare_install_fixture(
        repo_root,
        root_path=portable_root,
        install_id=PORTABLE_INSTALL_ID,
        install_mode="portable",
        store_root=portable_root,
    )
    installed_manifest = _prepare_install_fixture(
        repo_root,
        root_path=installed_root,
        install_id=INSTALLED_INSTALL_ID,
        install_mode="linked",
        store_root=installed_store_root,
    )
    for registry_root in registry_roots:
        shutil.rmtree(os.path.dirname(registry_root), ignore_errors=True)
        os.makedirs(registry_root, exist_ok=True)
    result = registry_add_install(
        repo_root=repo_root,
        registry_path=registry_path,
        install_manifest_path=os.path.join(installed_root, "install.manifest.json"),
    )
    if _token(result.get("result")) != "complete":
        raise ValueError("fixture install registry add failed ({})".format(_token(result.get("refusal_code"))))
    with open(registry_path, "r", encoding="utf-8") as handle:
        registry_payload = json.load(handle)
    for registry_root in registry_roots[1:]:
        _write_json(os.path.join(registry_root, "install_registry.json"), registry_payload)
    return {
        "work_root": _norm(work_root),
        "portable_root": _norm(portable_root),
        "portable_manifest_path": _norm(os.path.join(portable_root, "install.manifest.json")),
        "portable_manifest": portable_manifest,
        "installed_root": _norm(installed_root),
        "installed_manifest_path": _norm(os.path.join(installed_root, "install.manifest.json")),
        "installed_manifest": installed_manifest,
        "installed_store_root": _norm(installed_store_root),
        "install_registry_path": _norm(registry_path),
        "installed_env": {
            "APPDATA": _norm(os.path.join(work_root, "config_win")),
            "XDG_CONFIG_HOME": _norm(os.path.join(work_root, "config_posix")),
            "HOME": _norm(work_root),
        },
    }


def _entry_callable(row: Mapping[str, object]) -> Callable[[list[str] | None], int]:
    module = importlib.import_module(_token(row.get("entry_module")))
    return getattr(module, _token(row.get("entry_function")))


def _descriptor_value(payload: Mapping[str, object], *path_tokens: str) -> str:
    current: object = payload
    for token in path_tokens:
        current = _as_map(current).get(token)
    return _token(current)


def _json_or_empty(text: str) -> dict:
    token = str(text or "").strip()
    if not token.startswith("{") or not token.endswith("}"):
        return {}
    try:
        payload = json.loads(token)
    except ValueError:
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _parse_json_lines(text: str) -> list[dict]:
    rows: list[dict] = []
    for line in str(text or "").splitlines():
        token = line.strip()
        if not token.startswith("{") or not token.endswith("}"):
            continue
        try:
            payload = json.loads(token)
        except ValueError:
            continue
        if isinstance(payload, dict):
            rows.append(dict(payload))
    return rows


@contextmanager
def _patched_probe_payload(probe_payload: Mapping[str, object] | None):
    if probe_payload is None:
        yield
        return
    import src.appshell.ui_mode_selector as ui_mode_selector
    import src.compat.capability_negotiation as capability_negotiation
    import src.compat.descriptor.descriptor_engine as descriptor_engine
    import src.platform.platform_probe as platform_probe

    replacements = {
        (ui_mode_selector, "probe_platform_descriptor"): ui_mode_selector.probe_platform_descriptor,
        (capability_negotiation, "probe_platform_descriptor"): capability_negotiation.probe_platform_descriptor,
        (descriptor_engine, "probe_platform_descriptor"): descriptor_engine.probe_platform_descriptor,
        (platform_probe, "probe_platform_descriptor"): platform_probe.probe_platform_descriptor,
    }

    def _replacement(*_args, **_kwargs):
        return dict(probe_payload or {})

    try:
        for module, attr in replacements:
            setattr(module, attr, _replacement)
        yield
    finally:
        for (module, attr), original in replacements.items():
            setattr(module, attr, original)


@contextmanager
def _patched_sys_argv(executable_path: str, argv: list[str]):
    original_argv = list(sys.argv)
    try:
        sys.argv = [str(executable_path)] + list(argv or [])
        yield
    finally:
        sys.argv = original_argv


@contextmanager
def _patched_environ(env_updates: Mapping[str, object] | None):
    if not env_updates:
        yield
        return
    original = dict(os.environ)
    try:
        for key, value in dict(env_updates or {}).items():
            token = _token(value)
            if token:
                os.environ[str(key)] = token
            elif str(key) in os.environ:
                del os.environ[str(key)]
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


def _invoke_product(
    repo_root: str,
    *,
    row: Mapping[str, object],
    executable_path: str,
    argv: list[str],
    probe_payload: Mapping[str, object] | None = None,
    env_updates: Mapping[str, object] | None = None,
) -> dict:
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    callable_main = _entry_callable(row)
    invocation_args = list(argv)
    if _token(row.get("invocation_handler")) == "stub":
        invocation_args = ["--product-id", _token(row.get("product_id")), "--"] + list(argv)
    with _patched_probe_payload(probe_payload):
        with _patched_environ(env_updates):
            with _patched_sys_argv(executable_path, invocation_args):
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    exit_code = int(callable_main(invocation_args))
    stdout_text = stdout_buffer.getvalue()
    stderr_text = stderr_buffer.getvalue()
    return {
        "exit_code": int(exit_code),
        "stdout": stdout_text,
        "stdout_json": _json_or_empty(stdout_text),
        "stderr": stderr_text,
        "stderr_events": _parse_json_lines(stderr_text),
        "stdout_fingerprint": canonical_sha256({"stdout": stdout_text}),
        "stderr_fingerprint": canonical_sha256({"stderr_events": _parse_json_lines(stderr_text)}),
    }


def _scenario_probe(
    repo_root: str,
    *,
    product_id: str,
    scenario_id: str,
    cap_row: Mapping[str, object],
    simulate_tty: str,
    simulate_gui: str,
) -> dict | None:
    feature_capabilities = {
        _token(item)
        for item in (
            list(cap_row.get("feature_capabilities") or [])
            or list(cap_row.get("default_feature_capabilities") or [])
        )
        if _token(item)
    }
    supports_native = "cap.ui.os_native" in feature_capabilities
    supports_rendered = "cap.ui.rendered" in feature_capabilities
    supports_tui = "cap.ui.tui" in feature_capabilities
    platform_id = "linux"
    if scenario_id == "tty":
        return build_test_probe(
            repo_root,
            product_id=product_id,
            platform_id=platform_id,
            tty=True,
            gui=False,
            native=False,
            rendered=supports_rendered,
            tui=supports_tui,
        )
    if scenario_id == "gui":
        return build_test_probe(
            repo_root,
            product_id=product_id,
            platform_id=platform_id,
            tty=False,
            gui=True,
            native=bool(supports_native and _token(product_id) in {"launcher", "setup"}),
            rendered=supports_rendered,
            tui=supports_tui,
        )
    if scenario_id == "headless":
        return build_test_probe(
            repo_root,
            product_id=product_id,
            platform_id=platform_id,
            tty=False,
            gui=False,
            native=False,
            rendered=False,
            tui=False,
        )
    tty_override = {"yes": True, "no": False}.get(_token(simulate_tty).lower())
    gui_override = {"yes": True, "no": False}.get(_token(simulate_gui).lower())
    if tty_override is None and gui_override is None:
        return None
    tty_value = bool(True if tty_override is None else tty_override)
    gui_value = bool(False if gui_override is None else gui_override)
    return build_test_probe(
        repo_root,
        product_id=product_id,
        platform_id=platform_id,
        tty=tty_value,
        gui=gui_value,
        native=bool(gui_value and supports_native and _token(product_id) in {"launcher", "setup"}),
        rendered=bool(gui_value and supports_rendered),
        tui=supports_tui,
    )


def _expected_selection(repo_root: str, *, product_id: str, probe_payload: Mapping[str, object]) -> dict:
    return selection_for_product(
        repo_root,
        product_id=product_id,
        requested_mode_id="",
        probe=dict(probe_payload),
    )


def _message_keys(stderr_events: list[Mapping[str, object]]) -> list[str]:
    return [_token(dict(row or {}).get("message_key")) for row in stderr_events if _token(dict(row or {}).get("message_key"))]


def _command_args(repo_root: str, *, invocation_kind: str, fixture_layout: Mapping[str, object], command_id: str) -> tuple[list[str], str]:
    args = ["--repo-root", repo_root]
    if command_id == "descriptor":
        args.append("--descriptor")
    elif command_id == "help":
        args.append("help")
    elif command_id == "compat-status":
        args.append("compat-status")
    elif command_id == "validate":
        args += ["validate", "--all", "--profile", "FAST"]
    return args, " ".join(args)


def _portable_executable_path(fixture_layout: Mapping[str, object], row: Mapping[str, object]) -> str:
    return os.path.join(_token(fixture_layout.get("portable_root")), _token(row.get("portable_executable_name")))


def _installed_executable_path(fixture_layout: Mapping[str, object], row: Mapping[str, object]) -> str:
    return os.path.join(_token(fixture_layout.get("installed_root")), "bin", _token(row.get("installed_executable_name")))


def _command_summary(command_id: str, result: Mapping[str, object]) -> dict:
    stdout_json = _as_map(result.get("stdout_json"))
    stderr_events = list(result.get("stderr_events") or [])
    exit_code = _int_value(result.get("exit_code"), default=1)
    summary = {
        "command_id": _token(command_id),
        "exit_code": exit_code,
        "stdout_fingerprint": _token(result.get("stdout_fingerprint")),
        "stderr_fingerprint": _token(result.get("stderr_fingerprint")),
        "stderr_message_keys": [token for token in _message_keys(stderr_events) if token],
        "result": _token(stdout_json.get("result")),
        "refusal_code": _token(stdout_json.get("refusal_code")),
    }
    if _token(command_id) == "descriptor":
        summary["descriptor_product_id"] = _descriptor_value(stdout_json, "descriptor", "product_id")
        summary["descriptor_hash"] = _descriptor_value(stdout_json, "descriptor_hash")
    elif _token(command_id) == "compat-status":
        summary["selected_mode_id"] = _descriptor_value(stdout_json, "mode_selection", "selected_mode_id")
        summary["compatibility_mode_id"] = _descriptor_value(stdout_json, "mode_selection", "compatibility_mode_id")
        summary["install_mode"] = _descriptor_value(stdout_json, "install_discovery", "mode")
        summary["install_result"] = _descriptor_value(stdout_json, "install_discovery", "result")
        summary["install_resolution_source"] = _descriptor_value(stdout_json, "install_discovery", "resolution_source")
        summary["degrade_step_count"] = int(len(list(_as_map(stdout_json.get("mode_selection")).get("degrade_chain") or [])))
    elif _token(command_id) == "validate":
        summary["validation_profile"] = _descriptor_value(stdout_json, "profile")
        summary["validation_report_id"] = _descriptor_value(stdout_json, "report_id")
    elif _token(command_id) == "help":
        help_lines = str(result.get("stdout", "")).splitlines()
        summary["help_first_line"] = help_lines[0].strip() if help_lines else ""
    summary["passed"] = bool(exit_code == 0)
    return summary


def _build_command_rows(repo_root: str, fixture_layout: Mapping[str, object]) -> list[dict]:
    rows: list[dict] = []
    for product_row in PRODUCT_RUNTIME_ROWS:
        for invocation_kind in ("portable", "installed"):
            executable_path = _portable_executable_path(fixture_layout, product_row) if invocation_kind == "portable" else _installed_executable_path(fixture_layout, product_row)
            env_updates = _as_map(fixture_layout.get("installed_env")) if invocation_kind == "installed" else {}
            for command_id in COMMAND_ORDER:
                if command_id == "validate" and invocation_kind != "portable":
                    continue
                argv, argv_text = _command_args(repo_root, invocation_kind=invocation_kind, fixture_layout=fixture_layout, command_id=command_id)
                result = _invoke_product(
                    repo_root,
                    row=product_row,
                    executable_path=executable_path,
                    argv=argv,
                    probe_payload=None,
                    env_updates=env_updates,
                )
                rows.append(
                    {
                        "product_id": _token(product_row.get("product_id")),
                        "display_name": _token(product_row.get("display_name")),
                        "invocation_kind": invocation_kind,
                        "executable_path": _safe_rel(executable_path, repo_root),
                        "argv": argv_text,
                        **_command_summary(command_id, result),
                    }
                )
    return sorted(
        rows,
        key=lambda row: (
            _token(row.get("product_id")),
            _token(row.get("invocation_kind")),
            COMMAND_ORDER.index(_token(row.get("command_id"))) if _token(row.get("command_id")) in COMMAND_ORDER else 999,
        ),
    )


def _build_mode_rows(
    repo_root: str,
    *,
    fixture_layout: Mapping[str, object],
    product_registry: Mapping[str, object],
    simulate_tty: str,
    simulate_gui: str,
) -> list[dict]:
    rows: list[dict] = []
    scenario_ids = ["tty", "gui", "headless"]
    custom_probe = _scenario_probe(
        repo_root,
        product_id="client",
        scenario_id="requested_context",
        cap_row=_as_map(product_registry.get("client")),
        simulate_tty=simulate_tty,
        simulate_gui=simulate_gui,
    )
    if custom_probe is not None:
        scenario_ids.append("requested_context")
    for product_row in PRODUCT_RUNTIME_ROWS:
        product_id = _token(product_row.get("product_id"))
        capability_row = _as_map(product_registry.get(product_id))
        for invocation_kind in ("portable", "installed"):
            executable_path = _portable_executable_path(fixture_layout, product_row) if invocation_kind == "portable" else _installed_executable_path(fixture_layout, product_row)
            env_updates = _as_map(fixture_layout.get("installed_env")) if invocation_kind == "installed" else {}
            for scenario_id in scenario_ids:
                probe_payload = _scenario_probe(
                    repo_root,
                    product_id=product_id,
                    scenario_id=scenario_id,
                    cap_row=capability_row,
                    simulate_tty=simulate_tty,
                    simulate_gui=simulate_gui,
                )
                if probe_payload is None:
                    continue
                expected = _expected_selection(repo_root, product_id=product_id, probe_payload=probe_payload)
                argv, argv_text = _command_args(repo_root, invocation_kind=invocation_kind, fixture_layout=fixture_layout, command_id="compat-status")
                result = _invoke_product(
                    repo_root,
                    row=product_row,
                    executable_path=executable_path,
                    argv=argv,
                    probe_payload=probe_payload,
                    env_updates=env_updates,
                )
                stdout_json = _as_map(result.get("stdout_json"))
                mode_selection = _as_map(stdout_json.get("mode_selection"))
                stderr_keys = _message_keys(list(result.get("stderr_events") or []))
                expected_degrade = list(expected.get("degrade_chain") or [])
                observed_degrade = list(mode_selection.get("degrade_chain") or [])
                rows.append(
                    {
                        "product_id": product_id,
                        "display_name": _token(product_row.get("display_name")),
                        "invocation_kind": invocation_kind,
                        "scenario_id": scenario_id,
                        "argv": argv_text,
                        "exit_code": _int_value(result.get("exit_code"), default=1),
                        "expected_selected_mode_id": _token(expected.get("selected_mode_id")),
                        "observed_selected_mode_id": _token(mode_selection.get("selected_mode_id")),
                        "expected_compatibility_mode_id": _token(expected.get("compatibility_mode_id")),
                        "observed_compatibility_mode_id": _token(mode_selection.get("compatibility_mode_id")),
                        "expected_degrade_step_count": int(len(expected_degrade)),
                        "observed_degrade_step_count": int(len(observed_degrade)),
                        "mode_matches_expected": _token(expected.get("selected_mode_id")) == _token(mode_selection.get("selected_mode_id")),
                        "compat_matches_expected": _token(expected.get("compatibility_mode_id")) == _token(mode_selection.get("compatibility_mode_id")),
                        "install_mode": _descriptor_value(stdout_json, "install_discovery", "mode"),
                        "install_result": _descriptor_value(stdout_json, "install_discovery", "result"),
                        "log_selected_mode": "appshell.mode.selected" in stderr_keys,
                        "log_degraded_mode": "appshell.mode.degraded" in stderr_keys,
                        "probe_fingerprint": _token(_as_map(expected.get("probe")).get("deterministic_fingerprint")),
                        "selection_fingerprint": _token(expected.get("deterministic_fingerprint")),
                        "observed_stdout_fingerprint": _token(result.get("stdout_fingerprint")),
                        "observed_stderr_fingerprint": _token(result.get("stderr_fingerprint")),
                        "passed": bool(
                            _int_value(result.get("exit_code"), default=1) == 0
                            and _token(mode_selection.get("selected_mode_id")) == _token(expected.get("selected_mode_id"))
                            and _token(mode_selection.get("compatibility_mode_id")) == _token(expected.get("compatibility_mode_id"))
                            and _descriptor_value(stdout_json, "install_discovery", "result") == "complete"
                            and ("appshell.mode.selected" in stderr_keys)
                            and (("appshell.mode.degraded" in stderr_keys) if expected_degrade else True)
                        ),
                    }
                )
    return sorted(
        rows,
        key=lambda row: (
            _token(row.get("product_id")),
            _token(row.get("invocation_kind")),
            MODE_SCENARIO_ORDER.index(_token(row.get("scenario_id"))) if _token(row.get("scenario_id")) in MODE_SCENARIO_ORDER else 999,
        ),
    )


def _build_ipc_rows(repo_root: str, product_registry: Mapping[str, object]) -> list[dict]:
    rows: list[dict] = []
    for product_row in PRODUCT_RUNTIME_ROWS:
        product_id = _token(product_row.get("product_id"))
        capability_row = _as_map(product_registry.get(product_id))
        feature_capabilities = {
            _token(item)
            for item in (
                list(capability_row.get("feature_capabilities") or [])
                or list(capability_row.get("default_feature_capabilities") or [])
            )
            if _token(item)
        }
        if "cap.ipc.attach_console" not in feature_capabilities:
            continue
        probe = run_ipc_attach_probe(
            repo_root,
            product_id=product_id,
            local_product_id="tool.attach_console_stub",
            suffix="prod_gate0.{}".format(product_id.replace(".", "_")),
        )
        rows.append(
            {
                "product_id": product_id,
                "display_name": _token(product_row.get("display_name")),
                "result": _token(probe.get("result")),
                "compatibility_mode_id": _token(probe.get("compatibility_mode_id")),
                "negotiation_record_hash": _token(probe.get("negotiation_record_hash")),
                "endpoint_count": int(len(list(_as_map(probe.get("discovered_report")).get("endpoints") or []))),
                "attach_result": _descriptor_value(probe, "attach", "result"),
                "passed": _token(probe.get("result")) == "complete",
                "probe_fingerprint": _token(probe.get("deterministic_fingerprint")),
            }
        )
    return sorted(rows, key=lambda row: (_token(row.get("product_id")), _token(row.get("result"))))


def _build_failures(command_rows: list[Mapping[str, object]], mode_rows: list[Mapping[str, object]], ipc_rows: list[Mapping[str, object]]) -> list[dict]:
    failures: list[dict] = []
    for row in command_rows:
        row_map = dict(row or {})
        command_id = _token(row_map.get("command_id"))
        if bool(row_map.get("passed")):
            if command_id == "compat-status":
                expected_install_mode = "portable" if _token(row_map.get("invocation_kind")) == "portable" else "installed"
                if _token(row_map.get("install_result")) != "complete" or _token(row_map.get("install_mode")) != expected_install_mode:
                    failures.append(
                        {
                            "product_id": _token(row_map.get("product_id")),
                            "surface": "compat-status",
                            "message": "install discovery did not resolve expected '{}' mode".format(expected_install_mode),
                        }
                    )
            elif command_id == "descriptor" and _token(row_map.get("descriptor_product_id")) != _token(row_map.get("product_id")):
                failures.append(
                    {
                        "product_id": _token(row_map.get("product_id")),
                        "surface": "descriptor",
                        "message": "descriptor did not emit the expected product_id",
                    }
                )
            elif command_id == "help" and not _token(row_map.get("help_first_line")):
                failures.append(
                    {
                        "product_id": _token(row_map.get("product_id")),
                        "surface": "help",
                        "message": "help did not emit any content",
                    }
                )
            elif command_id == "validate" and _token(row_map.get("validation_profile")) != "FAST":
                failures.append(
                    {
                        "product_id": _token(row_map.get("product_id")),
                        "surface": "validate",
                        "message": "validate --all did not execute the FAST profile",
                    }
                )
            continue
        failures.append(
            {
                "product_id": _token(row_map.get("product_id")),
                "surface": command_id,
                "message": "command exited with code {}".format(_int_value(row_map.get("exit_code"), default=1)),
            }
        )
    for row in mode_rows:
        row_map = dict(row or {})
        if bool(row_map.get("passed")):
            continue
        failures.append(
            {
                "product_id": _token(row_map.get("product_id")),
                "surface": "mode_selection",
                "message": "{} {} did not match expected mode selection".format(_token(row_map.get("invocation_kind")), _token(row_map.get("scenario_id"))),
            }
        )
    for row in ipc_rows:
        row_map = dict(row or {})
        if bool(row_map.get("passed")):
            continue
        failures.append(
            {
                "product_id": _token(row_map.get("product_id")),
                "surface": "ipc",
                "message": "IPC attach smoke failed",
            }
        )
    unique = {
        (_token(row.get("product_id")), _token(row.get("surface")), _token(row.get("message"))): dict(row)
        for row in failures
    }
    return sorted(unique.values(), key=lambda row: (_token(row.get("product_id")), _token(row.get("surface")), _token(row.get("message"))))


def build_product_boot_matrix_report(
    repo_root: str,
    *,
    simulate_tty: str = "auto",
    simulate_gui: str = "auto",
    install_root: str = "",
) -> dict:
    repo_root_abs = _norm(repo_root)
    fixture_layout = _prepare_fixture_layout(repo_root_abs, work_root=install_root)
    product_registry = _load_product_registry(repo_root_abs)
    command_rows = _build_command_rows(repo_root_abs, fixture_layout)
    mode_rows = _build_mode_rows(
        repo_root_abs,
        fixture_layout=fixture_layout,
        product_registry=product_registry,
        simulate_tty=simulate_tty,
        simulate_gui=simulate_gui,
    )
    ipc_rows = _build_ipc_rows(repo_root_abs, product_registry)
    failures = _build_failures(command_rows, mode_rows, ipc_rows)
    report = {
        "result": "complete" if not failures else "refused",
        "report_id": PRODUCT_BOOT_MATRIX_REPORT_ID,
        "simulate_tty": _token(simulate_tty) or "auto",
        "simulate_gui": _token(simulate_gui) or "auto",
        "fixture_layout": {
            "portable_root": _safe_rel(_token(fixture_layout.get("portable_root")), repo_root_abs),
            "installed_root": _safe_rel(_token(fixture_layout.get("installed_root")), repo_root_abs),
            "install_registry_path": _safe_rel(_token(fixture_layout.get("install_registry_path")), repo_root_abs),
        },
        "product_rows": [dict(row) for row in PRODUCT_RUNTIME_ROWS],
        "command_rows": command_rows,
        "mode_rows": mode_rows,
        "ipc_rows": ipc_rows,
        "failures": failures,
        "metrics": {
            "product_count": int(len(PRODUCT_RUNTIME_ROWS)),
            "command_run_count": int(len(command_rows)),
            "mode_run_count": int(len(mode_rows)),
            "ipc_run_count": int(len(ipc_rows)),
            "failure_count": int(len(failures)),
            "degrade_count": int(sum(1 for row in mode_rows if int(row.get("observed_degrade_step_count", 0) or 0) > 0)),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = _canonical_fingerprint(report)
    return report


def load_or_run_product_boot_matrix_report(repo_root: str, *, prefer_cached: bool = True) -> dict:
    report_path = os.path.join(_norm(repo_root), PRODUCT_BOOT_MATRIX_JSON_PATH.replace("/", os.sep))
    if prefer_cached and os.path.isfile(report_path):
        payload, error = _read_json(report_path)
        if not error and _token(payload.get("report_id")) == PRODUCT_BOOT_MATRIX_REPORT_ID:
            return payload
    return build_product_boot_matrix_report(_norm(repo_root))


def product_boot_matrix_violations(repo_root: str) -> list[dict]:
    report = load_or_run_product_boot_matrix_report(repo_root, prefer_cached=True)
    violations: list[dict] = []
    if _token(report.get("report_id")) != PRODUCT_BOOT_MATRIX_REPORT_ID:
        violations.append(
            {
                "code": "product_boot_matrix_report_id_mismatch",
                "file_path": PRODUCT_BOOT_MATRIX_JSON_PATH,
                "message": "product boot matrix report must declare report_id={}".format(PRODUCT_BOOT_MATRIX_REPORT_ID),
                "rule_id": "INV-PROD-GATE-0-MUST-PASS-BEFORE-RELEASE",
            }
        )
        return violations
    if _token(report.get("result")) != "complete":
        violations.append(
            {
                "code": "product_boot_matrix_not_complete",
                "file_path": PRODUCT_BOOT_MATRIX_JSON_PATH,
                "message": "product boot matrix gate must report result=complete",
                "rule_id": "INV-PROD-GATE-0-MUST-PASS-BEFORE-RELEASE",
            }
        )
    for row in list(report.get("failures") or []):
        row_map = dict(row or {})
        violations.append(
            {
                "code": "product_boot_failure",
                "file_path": PRODUCT_BOOT_MATRIX_JSON_PATH,
                "message": "{}: {}".format(_token(row_map.get("product_id")), _token(row_map.get("message"))),
                "rule_id": "INV-PROD-GATE-0-MUST-PASS-BEFORE-RELEASE",
            }
        )
    return sorted(violations, key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))))


def _expected_mode_lookup(report: Mapping[str, object], product_id: str, scenario_id: str) -> str:
    for row in list(report.get("mode_rows") or []):
        row_map = dict(row or {})
        if _token(row_map.get("product_id")) == _token(product_id) and _token(row_map.get("scenario_id")) == _token(scenario_id):
            return _token(row_map.get("expected_selected_mode_id"))
    return ""


def render_product_boot_matrix_doc(report: Mapping[str, object]) -> str:
    lines = [
        "Status: CANONICAL",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: RELEASE/MVP",
        "Replacement Target: release-pinned standalone product boot contract",
        "",
        "# Product Boot Matrix",
        "",
        "This matrix defines the minimum standalone product behaviors required for `PROD-GATE-0`.",
        "",
        "## Matrix",
        "",
        "| Product | Portable Invocation | Installed Invocation | TTY Expected Mode | GUI Expected Mode | Required Commands | Expected Refusal Codes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in PRODUCT_RUNTIME_ROWS:
        product_id = _token(row.get("product_id"))
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("display_name")),
                _token(row.get("portable_executable_name")),
                "{} (installed registry discovery)".format(_token(row.get("installed_executable_name"))),
                _expected_mode_lookup(report, product_id, "tty") or "cli",
                _expected_mode_lookup(report, product_id, "gui") or "cli",
                "<br>".join(_token(item) for item in list(row.get("required_commands") or [])),
                "<br>".join(_token(item) for item in list(row.get("expected_refusal_codes") or [])),
            )
        )
    lines.extend(
        (
            "",
            "## Notes",
            "",
            "- Product mode selection must route through `src/appshell/ui_mode_selector.py` with platform capabilities sourced from `src/platform/platform_probe.py`.",
            "- `compat-status` must expose both `mode_selection` and `install_discovery` for every product.",
            "- Portable runs resolve from `install.manifest.json` adjacent to the product executable.",
            "- Installed runs resolve through `install_registry.json` without bypassing virtual paths, negotiation, or validation surfaces.",
        )
    )
    return "\n".join(lines) + "\n"


def render_product_boot_matrix_report(report: Mapping[str, object]) -> str:
    command_rows = list(report.get("command_rows") or [])
    mode_rows = list(report.get("mode_rows") or [])
    ipc_rows = list(report.get("ipc_rows") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: regenerated product boot matrix report for release",
        "",
        "# Product Boot Matrix Report",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Summary",
        "",
        "- result: `{}`".format(_token(report.get("result"))),
        "- products: `{}`".format(int(_as_map(report.get("metrics")).get("product_count", 0) or 0)),
        "- command runs: `{}`".format(int(_as_map(report.get("metrics")).get("command_run_count", 0) or 0)),
        "- mode runs: `{}`".format(int(_as_map(report.get("metrics")).get("mode_run_count", 0) or 0)),
        "- ipc runs: `{}`".format(int(_as_map(report.get("metrics")).get("ipc_run_count", 0) or 0)),
        "- failures: `{}`".format(int(_as_map(report.get("metrics")).get("failure_count", 0) or 0)),
        "",
        "## Command Surface",
        "",
        "| Product | Invocation | Command | Exit | Result | Install Mode | Selected Mode |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in command_rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("product_id")),
                _token(row.get("invocation_kind")),
                _token(row.get("command_id")),
                int(row.get("exit_code", 0) or 0),
                _token(row.get("result")) or ("pass" if bool(row.get("passed")) else "fail"),
                _token(row.get("install_mode")),
                _token(row.get("selected_mode_id")),
            )
        )
    lines.extend(
        (
            "",
            "## Mode Assertions",
            "",
            "| Product | Invocation | Scenario | Expected | Observed | Compat | Degrade | Pass |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        )
    )
    for row in mode_rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("product_id")),
                _token(row.get("invocation_kind")),
                _token(row.get("scenario_id")),
                _token(row.get("expected_selected_mode_id")),
                _token(row.get("observed_selected_mode_id")),
                _token(row.get("observed_compatibility_mode_id")),
                int(row.get("observed_degrade_step_count", 0) or 0),
                "yes" if bool(row.get("passed")) else "no",
            )
        )
    lines.extend(
        (
            "",
            "## IPC Assertions",
            "",
            "| Product | Result | Compat | Endpoint Count | Pass |",
            "| --- | --- | --- | --- | --- |",
        )
    )
    if ipc_rows:
        for row in ipc_rows:
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                    _token(row.get("product_id")),
                    _token(row.get("result")),
                    _token(row.get("compatibility_mode_id")),
                    int(row.get("endpoint_count", 0) or 0),
                    "yes" if bool(row.get("passed")) else "no",
                )
            )
    else:
        lines.append("| `none` | `-` | `-` | `0` | `yes` |")
    lines.extend(("", "## Failures", ""))
    failures = list(report.get("failures") or [])
    if failures:
        for row in failures:
            lines.append("- `{}` `{}`: {}".format(_token(row.get("product_id")), _token(row.get("surface")), _token(row.get("message"))))
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_prod_gate_final(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: release-pinned standalone product boot gate summary",
        "",
        "# PROD Gate Final",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Pass/Fail By Product",
        "",
        "| Product | Descriptor | Help | Compat | Validate | IPC |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for product_row in PRODUCT_RUNTIME_ROWS:
        product_id = _token(product_row.get("product_id"))
        command_rows = [dict(row or {}) for row in list(report.get("command_rows") or []) if _token(dict(row or {}).get("product_id")) == product_id]
        ipc_row = next((dict(row or {}) for row in list(report.get("ipc_rows") or []) if _token(dict(row or {}).get("product_id")) == product_id), {})
        by_command = {}
        for row in command_rows:
            command_id = _token(row.get("command_id"))
            by_command[command_id] = bool(row.get("passed")) if command_id not in by_command else bool(by_command[command_id] and bool(row.get("passed")))
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                product_id,
                "pass" if bool(by_command.get("descriptor")) else "fail",
                "pass" if bool(by_command.get("help")) else "fail",
                "pass" if bool(by_command.get("compat-status")) else "fail",
                "pass" if bool(by_command.get("validate")) else "fail",
                "n/a" if not ipc_row else ("pass" if bool(ipc_row.get("passed")) else "fail"),
            )
        )
    lines.extend(
        (
            "",
            "## Mode Selections Observed",
            "",
            "| Product | Portable TTY | Portable GUI | Installed TTY | Installed GUI |",
            "| --- | --- | --- | --- | --- |",
        )
    )
    for product_row in PRODUCT_RUNTIME_ROWS:
        product_id = _token(product_row.get("product_id"))
        lookup = {}
        for row in list(report.get("mode_rows") or []):
            row_map = dict(row or {})
            if _token(row_map.get("product_id")) != product_id:
                continue
            lookup[(_token(row_map.get("invocation_kind")), _token(row_map.get("scenario_id")))] = _token(row_map.get("observed_selected_mode_id"))
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                product_id,
                lookup.get(("portable", "tty"), ""),
                lookup.get(("portable", "gui"), ""),
                lookup.get(("installed", "tty"), ""),
                lookup.get(("installed", "gui"), ""),
            )
        )
    degrade_rows = [dict(row or {}) for row in list(report.get("mode_rows") or []) if int(dict(row or {}).get("observed_degrade_step_count", 0) or 0) > 0]
    lines.extend(("", "## Degradations Observed", ""))
    if degrade_rows:
        for row in degrade_rows:
            lines.append(
                "- `{}` `{}` `{}` degraded by `{}` step(s).".format(
                    _token(row.get("product_id")),
                    _token(row.get("invocation_kind")),
                    _token(row.get("scenario_id")),
                    int(row.get("observed_degrade_step_count", 0) or 0),
                )
            )
    else:
        lines.append("- none")
    lines.extend(
        (
            "",
            "## Readiness",
            "",
            "- Ready for IPC-UNIFY-0 and supervisor hardening when this gate remains green alongside RepoX, AuditX, and TestX.",
        )
    )
    return "\n".join(lines) + "\n"


def render_product_boot_matrix_bundle(report: Mapping[str, object]) -> dict[str, str]:
    return {
        PRODUCT_BOOT_MATRIX_DOC_PATH: render_product_boot_matrix_doc(report),
        PRODUCT_BOOT_MATRIX_REPORT_PATH: render_product_boot_matrix_report(report),
        PROD_GATE_FINAL_PATH: render_prod_gate_final(report),
    }


def write_product_boot_matrix_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    root = _norm(repo_root)
    written: dict[str, str] = {}
    for rel_path, text in render_product_boot_matrix_bundle(report).items():
        abs_path = os.path.join(root, rel_path.replace("/", os.sep))
        _write_text(abs_path, text)
        written[rel_path] = abs_path.replace("\\", "/")
    report_abs = os.path.join(root, PRODUCT_BOOT_MATRIX_JSON_PATH.replace("/", os.sep))
    _write_json(report_abs, report)
    written[PRODUCT_BOOT_MATRIX_JSON_PATH] = report_abs.replace("\\", "/")
    return dict(sorted(written.items()))


__all__ = [
    "PRODUCT_BOOT_MATRIX_DOC_PATH",
    "PRODUCT_BOOT_MATRIX_JSON_PATH",
    "PRODUCT_BOOT_MATRIX_REPORT_ID",
    "PRODUCT_BOOT_MATRIX_REPORT_PATH",
    "PRODUCT_BOOT_MATRIX_TOOL_PATH",
    "PROD_GATE_FINAL_PATH",
    "build_product_boot_matrix_report",
    "load_or_run_product_boot_matrix_report",
    "product_boot_matrix_violations",
    "write_product_boot_matrix_outputs",
]
