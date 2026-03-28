"""Deterministic DIST-2 bundle verification helpers."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from typing import Iterable, Mapping, Sequence

from release import DEFAULT_RELEASE_MANIFEST_REL, load_release_manifest, verify_release_manifest
from tools.dist.dist_tree_common import (
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_PLATFORM_TAG,
    DEFAULT_RELEASE_CHANNEL,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


DIST_VERIFY_REPORT_ID = "dist.verify.v1"
DIST2_FINAL_REPORT_ID = "dist.verify.final.v1"
DEFAULT_RELEASE_TAG = "v0.0.0-{}".format(DEFAULT_RELEASE_CHANNEL)
DEFAULT_PLATFORM = DEFAULT_PLATFORM_TAG
DEFAULT_BUNDLE_REL = os.path.join(DEFAULT_OUTPUT_ROOT, DEFAULT_RELEASE_TAG, DEFAULT_PLATFORM, "dominium")
DIST_VERIFY_RULES_PATH = "docs/release/DIST_VERIFICATION_RULES.md"
DIST2_FINAL_DOC_PATH = "docs/audit/DIST2_FINAL.md"
RULE_VERIFY = "INV-DIST-VERIFY-MUST-PASS"
RULE_ABSOLUTE_PATHS = "INV-NO-ABSOLUTE-PATHS-IN-DIST"
RULE_NO_XSTACK = "INV-NO-XSTACK-IN-DIST"
LAST_REVIEWED = "2026-03-14"
ARTIFACT_KIND_BINARY = "artifact.binary"

REQUIRED_LAYOUT = (
    "install.manifest.json",
    "manifests/filelist.txt",
    "manifests/release_manifest.json",
    "bin/engine",
    "bin/game",
    "bin/client",
    "bin/server",
    "bin/setup",
    "bin/launcher",
    "store/store.root.json",
    "store/locks/pack_lock.mvp_default.json",
    "store/profiles/bundles/bundle.mvp_default.json",
    "instances/default/instance.manifest.json",
    "docs/COMPATIBILITY.md",
    "docs/RELEASE_NOTES_v0_0_0_mock.md",
    "README",
    "LICENSE",
)

FORBIDDEN_DIR_NAMES = frozenset(
    {
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        "fixtures",
        "testdata",
        "tests",
        "tmp",
    }
)
FORBIDDEN_FILE_NAMES = frozenset({".gitattributes", ".gitignore", ".gitkeep"})
FORBIDDEN_FILE_SUFFIXES = (".bak", ".log", ".pdb", ".py", ".pyi", ".tmp")
FORBIDDEN_PATH_PREFIXES = (
    "tools/auditx",
    "tools/convergence",
    "tools/dist",
    "tools/release",
    "tools/xstack/auditx",
    "tools/xstack/controlx",
    "tools/xstack/core",
    "tools/xstack/extensions",
    "tools/xstack/out",
    "tools/xstack/performx",
    "tools/xstack/repox",
    "tools/xstack/securex",
    "tools/xstack/testx",
)
ALLOWED_XSTACK_RUNTIME_PREFIXES = (
    "tools/xstack/cache_store",
    "tools/xstack/compatx",
    "tools/xstack/pack_contrib",
    "tools/xstack/pack_loader",
    "tools/xstack/packagingx",
    "tools/xstack/registry_compile",
    "tools/xstack/sessionx",
)
ABSOLUTE_PATH_SCAN_SUFFIXES = {".json", ".md", ".txt"}
ABSOLUTE_PATH_SCAN_NAMES = {"README", "LICENSE"}
MODE_SANITY_PRODUCTS = ("engine", "game", "launcher", "setup")
MODE_SANITY_MODES = ("cli", "tui")

WINDOWS_ABSOLUTE_RE = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z]:[\\/][^\s\"'<>|]+)")
UNC_ABSOLUTE_RE = re.compile(r"(\\\\[^\\/\s\"'<>|]+[\\/][^\s\"'<>|]+)")
UNIX_ABSOLUTE_RE = re.compile(r"(?<![A-Za-z0-9_])(/(?:Users|home|tmp|private|var|opt)/[^\s\"'<>|]+)")


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(str(path or "")))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/").lstrip("./")


def _repo_rel_or_abs(repo_root: str, path: str) -> str:
    abs_path = _norm(path)
    root = _norm(repo_root) if _token(repo_root) else ""
    if root:
        try:
            if os.path.commonpath([root, abs_path]) == root:
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


def _report_json_rel(platform_tag: str) -> str:
    return "data/audit/dist_verify_{}.json".format(_platform_slug(platform_tag))


def _report_doc_rel(platform_tag: str) -> str:
    return "docs/audit/DIST_VERIFY_{}.md".format(_platform_slug(platform_tag))


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


def _sha256_file(path: str) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_bundle_files(bundle_root: str) -> list[str]:
    root = _norm(bundle_root)
    rows: list[str] = []
    if not os.path.isdir(root):
        return rows
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(dirnames)
        rel_root = os.path.relpath(current_root, root)
        rel_root_norm = "" if rel_root in (".", "") else _norm_rel(rel_root)
        for name in sorted(filenames):
            rel_path = name if not rel_root_norm else "{}/{}".format(rel_root_norm, name)
            rows.append(_norm_rel(rel_path))
    return sorted(rows)


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


def _run_bundle_command(bundle_root: str, product_id: str, argv: Sequence[str]) -> dict:
    wrapper_path = os.path.join(_norm(bundle_root), "bin", _token(product_id))
    proc = subprocess.run(
        [sys.executable, wrapper_path] + [str(item) for item in list(argv or [])],
        cwd=_norm(bundle_root),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    json_rows = _extract_json_objects(proc.stdout)
    return {
        "returncode": int(proc.returncode or 0),
        "stdout": str(proc.stdout or ""),
        "stderr": str(proc.stderr or ""),
        "json_rows": json_rows,
        "first_json": dict(json_rows[0]) if json_rows else {},
    }


def _load_report(path: str) -> dict:
    target = _norm(path)
    try:
        with open(target, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _required_layout_rows(bundle_root: str) -> list[dict]:
    root = _norm(bundle_root)
    rows = []
    for rel_path in REQUIRED_LAYOUT:
        rows.append(
            {
                "path": rel_path,
                "present": os.path.exists(os.path.join(root, rel_path.replace("/", os.sep))),
            }
        )
    return rows


def scan_forbidden_distribution_files(bundle_root: str) -> list[dict]:
    rows: list[dict] = []
    for rel_path in _iter_bundle_files(bundle_root):
        parts = [part for part in rel_path.split("/") if part]
        filename = parts[-1] if parts else ""
        category = ""
        message = ""
        if filename in FORBIDDEN_FILE_NAMES:
            category = "forbidden_file_name"
            message = "forbidden file name present in distribution"
        elif any(part in FORBIDDEN_DIR_NAMES for part in parts[:-1]):
            category = "forbidden_directory_marker"
            message = "forbidden directory marker present in distribution"
        elif rel_path.endswith(FORBIDDEN_FILE_SUFFIXES):
            category = "forbidden_file_suffix"
            message = "forbidden development/source file suffix present in distribution"
        elif any(rel_path == prefix or rel_path.startswith(prefix + "/") for prefix in FORBIDDEN_PATH_PREFIXES):
            category = "forbidden_path_prefix"
            message = "forbidden development/tool path present in distribution"
        elif rel_path.startswith("tools/xstack/") and not any(
            rel_path == prefix or rel_path.startswith(prefix + "/") for prefix in ALLOWED_XSTACK_RUNTIME_PREFIXES
        ):
            category = "forbidden_xstack_surface"
            message = "non-runtime XStack surface present in distribution"
        if category:
            rows.append({"path": rel_path, "category": category, "message": message})
    return sorted(rows, key=lambda row: (_token(row.get("path")), _token(row.get("category")), _token(row.get("message"))))


def scan_distribution_absolute_path_leaks(bundle_root: str) -> list[dict]:
    root = _norm(bundle_root)
    rows: list[dict] = []
    for rel_path in _iter_bundle_files(root):
        suffix = os.path.splitext(rel_path)[1].lower()
        filename = os.path.basename(rel_path)
        if suffix not in ABSOLUTE_PATH_SCAN_SUFFIXES and filename not in ABSOLUTE_PATH_SCAN_NAMES:
            continue
        abs_path = os.path.join(root, rel_path.replace("/", os.sep))
        if suffix == ".json":
            try:
                with open(abs_path, "r", encoding="utf-8") as handle:
                    payload = json.load(handle)
            except (OSError, ValueError):
                continue
            for field_path, value in _walk_strings(payload):
                for matched in WINDOWS_ABSOLUTE_RE.findall(value):
                    rows.append({"path": rel_path, "location": field_path, "value": _token(matched), "kind": "windows"})
                for matched in UNC_ABSOLUTE_RE.findall(value):
                    rows.append({"path": rel_path, "location": field_path, "value": _token(matched), "kind": "unc"})
                for matched in UNIX_ABSOLUTE_RE.findall(value):
                    rows.append({"path": rel_path, "location": field_path, "value": _token(matched), "kind": "unix"})
            continue
        try:
            with open(abs_path, "r", encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            for matched in WINDOWS_ABSOLUTE_RE.findall(line):
                rows.append({"path": rel_path, "location": "line:{}".format(line_no), "value": _token(matched), "kind": "windows"})
            for matched in UNC_ABSOLUTE_RE.findall(line):
                rows.append({"path": rel_path, "location": "line:{}".format(line_no), "value": _token(matched), "kind": "unc"})
            for matched in UNIX_ABSOLUTE_RE.findall(line):
                rows.append({"path": rel_path, "location": "line:{}".format(line_no), "value": _token(matched), "kind": "unix"})
    return sorted(
        rows,
        key=lambda row: (
            _token(row.get("path")),
            _token(row.get("location")),
            _token(row.get("value")),
            _token(row.get("kind")),
        ),
    )


def _layout_check(bundle_root: str) -> dict:
    rows = _required_layout_rows(bundle_root)
    missing_paths = [_token(row.get("path")) for row in rows if not bool(row.get("present"))]
    return {
        "result": "complete" if not missing_paths else "refused",
        "required_paths": rows,
        "missing_paths": missing_paths,
    }


def _pack_verify_check(bundle_root: str) -> dict:
    run = _run_bundle_command(bundle_root, "setup", ["packs", "verify"])
    payload = dict(run.get("first_json") or {})
    return {
        "result": "complete" if int(run.get("returncode", 0)) == 0 and _token(payload.get("result")) == "complete" else "refused",
        "returncode": int(run.get("returncode", 0)),
        "payload": payload,
        "payload_fingerprint": canonical_sha256(dict(payload or {})),
        "stderr_fingerprint": canonical_sha256({"stderr": _token(run.get("stderr"))}),
    }


def _descriptor_checks(bundle_root: str) -> dict:
    manifest_path = os.path.join(_norm(bundle_root), DEFAULT_RELEASE_MANIFEST_REL.replace("/", os.sep))
    manifest = load_release_manifest(manifest_path)
    rows: list[dict] = []
    for artifact in sorted(_as_list(manifest.get("artifacts")), key=lambda row: (_token(_as_map(row).get("artifact_kind")), _token(_as_map(row).get("artifact_name")))):
        item = _as_map(artifact)
        if _token(item.get("artifact_kind")) != ARTIFACT_KIND_BINARY:
            continue
        artifact_name = _token(item.get("artifact_name"))
        descriptor_hash = _token(item.get("endpoint_descriptor_hash")).lower()
        if not descriptor_hash:
            continue
        product_id = _token(_as_map(item.get("extensions")).get("product_id")) or os.path.basename(artifact_name)
        run = _run_bundle_command(bundle_root, product_id, ["--descriptor"])
        json_rows = _as_list(run.get("json_rows"))
        descriptor_payload = _as_map(json_rows[0]) if json_rows else {}
        if isinstance(descriptor_payload.get("descriptor"), Mapping):
            descriptor = _as_map(descriptor_payload.get("descriptor"))
        else:
            descriptor = descriptor_payload
        actual_hash = canonical_sha256(descriptor) if descriptor else ""
        passed = int(run.get("returncode", 0)) == 0 and bool(descriptor) and actual_hash == descriptor_hash
        rows.append(
            {
                "artifact_name": artifact_name,
                "product_id": product_id,
                "returncode": int(run.get("returncode", 0)),
                "expected_descriptor_hash": descriptor_hash,
                "actual_descriptor_hash": actual_hash,
                "passed": passed,
                "stderr": _token(run.get("stderr")),
            }
        )
    return {
        "result": "complete" if all(bool(row.get("passed")) for row in rows) else "refused",
        "rows": rows,
    }


def _mode_sanity_check(bundle_root: str) -> dict:
    rows: list[dict] = []
    for product_id in MODE_SANITY_PRODUCTS:
        for mode_id in MODE_SANITY_MODES:
            run = _run_bundle_command(bundle_root, product_id, ["compat-status", "--mode", mode_id])
            payload = dict(run.get("first_json") or {})
            mode_selection = _as_map(payload.get("mode_selection"))
            selected_mode = _token(mode_selection.get("selected_mode_id"))
            requested_mode = _token(mode_selection.get("requested_mode_id"))
            passed = int(run.get("returncode", 0)) == 0 and _token(payload.get("result")) == "complete" and requested_mode == mode_id and selected_mode == mode_id
            rows.append(
                {
                    "product_id": product_id,
                    "requested_mode_id": mode_id,
                    "returncode": int(run.get("returncode", 0)),
                    "result": _token(payload.get("result")),
                    "selected_mode_id": selected_mode,
                    "requested_mode_recorded": requested_mode,
                    "degrade_chain": list(mode_selection.get("degrade_chain") or []),
                    "passed": passed,
                    "stderr_fingerprint": canonical_sha256({"stderr": _token(run.get("stderr"))}),
                }
            )
    return {
        "result": "complete" if all(bool(row.get("passed")) for row in rows) else "refused",
        "rows": rows,
    }


def _error(code: str, path: str, message: str, remediation: str, rule_id: str) -> dict:
    return {
        "code": _token(code),
        "path": _token(path),
        "message": _token(message),
        "remediation": _token(remediation),
        "rule_id": _token(rule_id),
    }


def build_distribution_verify_report(
    bundle_root: str,
    *,
    platform_tag: str = DEFAULT_PLATFORM,
    repo_root: str = "",
) -> dict:
    root = _norm(bundle_root)
    repo_token = _token(repo_root)
    layout = _layout_check(root)
    manifest_path = os.path.join(root, DEFAULT_RELEASE_MANIFEST_REL.replace("/", os.sep))
    release_verify = verify_release_manifest(root, manifest_path, repo_root=repo_token) if os.path.isfile(manifest_path) else {
        "result": "refused",
        "errors": [{"code": "refusal.release_manifest.missing_artifact", "path": DEFAULT_RELEASE_MANIFEST_REL, "message": "release manifest is missing"}],
        "warnings": [],
        "verified_artifact_count": 0,
        "manifest_hash": "",
    }
    pack_verify = _pack_verify_check(root) if os.path.isdir(root) else {"result": "refused", "returncode": 1, "payload": {}, "payload_fingerprint": "", "stderr": "bundle root missing"}
    descriptor_checks = _descriptor_checks(root) if os.path.isfile(manifest_path) else {"result": "refused", "rows": []}
    forbidden_files = scan_forbidden_distribution_files(root)
    absolute_path_hits = scan_distribution_absolute_path_leaks(root)
    mode_sanity = _mode_sanity_check(root) if os.path.isdir(root) else {"result": "refused", "rows": []}
    filelist_path = os.path.join(root, "manifests", "filelist.txt")
    filelist_hash = _sha256_file(filelist_path) if os.path.isfile(filelist_path) else ""

    errors: list[dict] = []
    if _token(layout.get("result")) != "complete":
        for rel_path in list(layout.get("missing_paths") or []):
            errors.append(
                _error(
                    "refusal.dist.missing_artifact",
                    rel_path,
                    "required distribution path is missing",
                    "rerun python tools/dist/tool_assemble_dist_tree.py --repo-root . --platform-tag {} --channel {}".format(_token(platform_tag) or DEFAULT_PLATFORM, DEFAULT_RELEASE_CHANNEL),
                    RULE_VERIFY,
                )
            )
    if _token(release_verify.get("result")) != "complete":
        for row in _as_list(release_verify.get("errors")):
            item = _as_map(row)
            lower_code = _token(item.get("code")).lower()
            mapped_code = "refusal.dist.missing_artifact" if "missing_artifact" in lower_code else "refusal.dist.hash_mismatch"
            errors.append(
                _error(
                    mapped_code,
                    _token(item.get("path")) or DEFAULT_RELEASE_MANIFEST_REL,
                    _token(item.get("message")) or "release manifest verification failed",
                    "rerun python tools/release/tool_generate_release_manifest.py --dist-root {} --platform-tag {} --channel {}".format(_repo_rel_or_abs(repo_token, root), _token(platform_tag) or DEFAULT_PLATFORM, DEFAULT_RELEASE_CHANNEL),
                    RULE_VERIFY,
                )
            )
    if _token(pack_verify.get("result")) != "complete":
        errors.append(
            _error(
                "refusal.dist.hash_mismatch",
                "store/packs",
                "offline pack verification failed for the assembled bundle",
                "run python {}/bin/setup packs verify".format(_repo_rel_or_abs(repo_token, root)),
                RULE_VERIFY,
            )
        )
    if _token(descriptor_checks.get("result")) != "complete":
        for row in _as_list(descriptor_checks.get("rows")):
            item = _as_map(row)
            if bool(item.get("passed")):
                continue
            errors.append(
                _error(
                    "refusal.dist.hash_mismatch",
                    _token(item.get("artifact_name")),
                    "endpoint descriptor hash does not match the release manifest",
                    "rerun python tools/release/tool_generate_release_manifest.py --dist-root {} --platform-tag {} --channel {}".format(_repo_rel_or_abs(repo_token, root), _token(platform_tag) or DEFAULT_PLATFORM, DEFAULT_RELEASE_CHANNEL),
                    RULE_VERIFY,
                )
            )
    if forbidden_files:
        for row in forbidden_files:
            item = _as_map(row)
            rule_id = RULE_NO_XSTACK if _token(item.get("category")) == "forbidden_xstack_surface" else RULE_VERIFY
            errors.append(
                _error(
                    "refusal.dist.forbidden_file_present",
                    _token(item.get("path")),
                    _token(item.get("message")) or "forbidden file present in assembled distribution",
                    "remove the forbidden file or rerun deterministic assembly",
                    rule_id,
                )
            )
    if absolute_path_hits:
        for row in absolute_path_hits:
            item = _as_map(row)
            errors.append(
                _error(
                    "refusal.dist.absolute_path_leak",
                    _token(item.get("path")),
                    "absolute path leak detected at {}".format(_token(item.get("location"))),
                    "rewrite the artifact to use relative or logical virtual-path references and regenerate the manifest",
                    RULE_ABSOLUTE_PATHS,
                )
            )
    if _token(mode_sanity.get("result")) != "complete":
        errors.append(
            _error(
                "refusal.dist.hash_mismatch",
                "mode_selection",
                "deterministic mode-selection sanity check failed inside the assembled bundle",
                "rerun the bundle assembly and inspect python tools/release/tool_run_ui_mode_resolution.py --repo-root .",
                RULE_VERIFY,
            )
        )

    report = {
        "report_id": DIST_VERIFY_REPORT_ID,
        "result": "complete" if not errors else "refused",
        "platform_tag": _token(platform_tag) or DEFAULT_PLATFORM,
        "bundle_root": _repo_rel_or_abs(repo_token, root),
        "layout_check": layout,
        "release_manifest_verification": dict(release_verify),
        "pack_verification": pack_verify,
        "descriptor_checks": descriptor_checks,
        "forbidden_file_scan": {
            "result": "complete" if not forbidden_files else "refused",
            "rows": forbidden_files,
            "allowed_xstack_runtime_prefixes": list(ALLOWED_XSTACK_RUNTIME_PREFIXES),
        },
        "absolute_path_scan": {
            "result": "complete" if not absolute_path_hits else "refused",
            "rows": absolute_path_hits,
        },
        "mode_selection_sanity": mode_sanity,
        "key_hashes": {
            "release_manifest_hash": _token(release_verify.get("manifest_hash")).lower(),
            "filelist_hash": filelist_hash,
            "pack_verify_payload_fingerprint": _token(pack_verify.get("payload_fingerprint")),
        },
        "errors": sorted(
            errors,
            key=lambda row: (
                _token(_as_map(row).get("rule_id")),
                _token(_as_map(row).get("code")),
                _token(_as_map(row).get("path")),
                _token(_as_map(row).get("message")),
            ),
        ),
        "warnings": sorted(
            [_as_map(item) for item in _as_list(release_verify.get("warnings")) if _as_map(item)],
            key=lambda row: (
                _token(row.get("code")),
                _token(row.get("path")),
                _token(row.get("message")),
            ),
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_distribution_verify_report(report: Mapping[str, object]) -> str:
    row = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-3 clean-room distribution verification baseline",
        "",
        "# DIST Verify - {}".format(_token(row.get("platform_tag")) or DEFAULT_PLATFORM),
        "",
        "- result: `{}`".format(_token(row.get("result"))),
        "- bundle_root: `{}`".format(_token(row.get("bundle_root"))),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "",
        "## Layout Check",
        "",
        "- result: `{}`".format(_token(_as_map(row.get("layout_check")).get("result"))),
    ]
    missing_paths = list(_as_map(row.get("layout_check")).get("missing_paths") or [])
    lines.append("- missing_paths: `{}`".format(", ".join(_token(item) for item in missing_paths) or "none"))
    lines.extend(
        [
            "",
            "## Release Manifest Verification",
            "",
            "- result: `{}`".format(_token(_as_map(row.get("release_manifest_verification")).get("result"))),
            "- verified_artifact_count: `{}`".format(int(_as_map(row.get("release_manifest_verification")).get("verified_artifact_count") or 0)),
            "- manifest_hash: `{}`".format(_token(_as_map(row.get("release_manifest_verification")).get("manifest_hash"))),
            "",
            "## Pack Verification",
            "",
            "- result: `{}`".format(_token(_as_map(row.get("pack_verification")).get("result"))),
            "- returncode: `{}`".format(int(_as_map(row.get("pack_verification")).get("returncode") or 0)),
            "",
            "## Descriptor Checks",
            "",
        ]
    )
    descriptor_rows = list(_as_map(row.get("descriptor_checks")).get("rows") or [])
    if not descriptor_rows:
        lines.append("- none")
    else:
        for item in descriptor_rows:
            item_map = _as_map(item)
            lines.append(
                "- `{}` passed=`{}` expected=`{}` actual=`{}`".format(
                    _token(item_map.get("artifact_name")),
                    bool(item_map.get("passed")),
                    _token(item_map.get("expected_descriptor_hash")),
                    _token(item_map.get("actual_descriptor_hash")),
                )
            )
    lines.extend(
        [
            "",
            "## Forbidden File Scan",
            "",
            "- result: `{}`".format(_token(_as_map(row.get("forbidden_file_scan")).get("result"))),
        ]
    )
    forbidden_rows = list(_as_map(row.get("forbidden_file_scan")).get("rows") or [])
    if not forbidden_rows:
        lines.append("- none")
    else:
        for item in forbidden_rows:
            item_map = _as_map(item)
            lines.append("- `{}`: {} ({})".format(_token(item_map.get("path")), _token(item_map.get("message")), _token(item_map.get("category"))))
    lines.extend(
        [
            "",
            "## Absolute Path Scan",
            "",
            "- result: `{}`".format(_token(_as_map(row.get("absolute_path_scan")).get("result"))),
        ]
    )
    absolute_rows = list(_as_map(row.get("absolute_path_scan")).get("rows") or [])
    if not absolute_rows:
        lines.append("- none")
    else:
        for item in absolute_rows:
            item_map = _as_map(item)
            lines.append("- `{}` {} -> `{}`".format(_token(item_map.get("path")), _token(item_map.get("location")), _token(item_map.get("value"))))
    lines.extend(["", "## Mode Selection Sanity", ""])
    for item in list(_as_map(row.get("mode_selection_sanity")).get("rows") or []):
        item_map = _as_map(item)
        lines.append(
            "- `{}` requested=`{}` selected=`{}` passed=`{}`".format(
                _token(item_map.get("product_id")),
                _token(item_map.get("requested_mode_id")),
                _token(item_map.get("selected_mode_id")),
                bool(item_map.get("passed")),
            )
        )
    lines.extend(["", "## Errors", ""])
    errors = list(row.get("errors") or [])
    if not errors:
        lines.append("- none")
    else:
        for item in errors:
            item_map = _as_map(item)
            lines.append(
                "- `{}` `{}`: {}. remediation: {}".format(
                    _token(item_map.get("code")),
                    _token(item_map.get("path")),
                    _token(item_map.get("message")),
                    _token(item_map.get("remediation")),
                )
            )
    lines.extend(["", "## Warnings", ""])
    warnings = list(row.get("warnings") or [])
    if not warnings:
        lines.append("- none")
    else:
        for item in warnings:
            item_map = _as_map(item)
            lines.append("- `{}` `{}`: {}".format(_token(item_map.get("code")), _token(item_map.get("path")), _token(item_map.get("message"))))
    return "\n".join(lines) + "\n"


def build_dist2_final_report(reports: Sequence[Mapping[str, object]]) -> dict:
    normalized = sorted(
        [_as_map(item) for item in list(reports or []) if _as_map(item)],
        key=lambda row: (_token(row.get("platform_tag")), _token(row.get("bundle_root"))),
    )
    final = {
        "report_id": DIST2_FINAL_REPORT_ID,
        "result": "complete" if normalized and all(_token(row.get("result")) == "complete" for row in normalized) else "refused",
        "platforms_verified": [_token(row.get("platform_tag")) for row in normalized],
        "report_fingerprints": {_token(row.get("platform_tag")): _token(row.get("deterministic_fingerprint")) for row in normalized},
        "failure_count": int(sum(len(_as_list(row.get("errors"))) for row in normalized)),
        "deterministic_fingerprint": "",
    }
    final["deterministic_fingerprint"] = canonical_sha256(dict(final, deterministic_fingerprint=""))
    return final


def render_dist2_final(report: Mapping[str, object], reports: Sequence[Mapping[str, object]]) -> str:
    row = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-3 clean-room distribution run",
        "",
        "# DIST2 Final",
        "",
        "- result: `{}`".format(_token(row.get("result"))),
        "- platforms_verified: `{}`".format(", ".join(_token(item) for item in _as_list(row.get("platforms_verified"))) or "none"),
        "- failure_count: `{}`".format(int(row.get("failure_count") or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(row.get("deterministic_fingerprint"))),
        "",
        "## Platform Reports",
        "",
    ]
    for item in sorted([_as_map(value) for value in list(reports or []) if _as_map(value)], key=lambda current: _token(current.get("platform_tag"))):
        lines.append(
            "- `{}` result=`{}` fingerprint=`{}` release_manifest_hash=`{}`".format(
                _token(item.get("platform_tag")),
                _token(item.get("result")),
                _token(item.get("deterministic_fingerprint")),
                _token(_as_map(item.get("key_hashes")).get("release_manifest_hash")),
            )
        )
    lines.extend(["", "## Readiness", "", "- DIST-3 clean-room run: {}".format("ready" if _token(row.get("result")) == "complete" else "blocked"), ""])
    return "\n".join(lines)


def write_distribution_verify_outputs(
    repo_root: str,
    report: Mapping[str, object],
    *,
    report_path: str = "",
    doc_path: str = "",
) -> dict:
    root = _norm(repo_root) if _token(repo_root) else os.getcwd()
    platform_tag = _token(_as_map(report).get("platform_tag")) or DEFAULT_PLATFORM
    report_rel = report_path or _report_json_rel(platform_tag)
    doc_rel = doc_path or _report_doc_rel(platform_tag)
    report_abs = report_rel if os.path.isabs(report_rel) else os.path.join(root, report_rel.replace("/", os.sep))
    doc_abs = doc_rel if os.path.isabs(doc_rel) else os.path.join(root, doc_rel.replace("/", os.sep))
    _write_json(report_abs, report)
    _write_text(doc_abs, render_distribution_verify_report(report))
    return {
        "report_path": _repo_rel_or_abs(root, report_abs),
        "doc_path": _repo_rel_or_abs(root, doc_abs),
    }


def write_dist2_final_outputs(
    repo_root: str,
    reports: Sequence[Mapping[str, object]],
    *,
    final_doc_path: str = DIST2_FINAL_DOC_PATH,
) -> dict:
    root = _norm(repo_root) if _token(repo_root) else os.getcwd()
    final = build_dist2_final_report(reports)
    doc_abs = final_doc_path if os.path.isabs(final_doc_path) else os.path.join(root, final_doc_path.replace("/", os.sep))
    _write_text(doc_abs, render_dist2_final(final, reports))
    return {
        "final_doc_path": _repo_rel_or_abs(root, doc_abs),
        "final_report": final,
    }


def load_distribution_verify_report(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM) -> dict:
    path = os.path.join(_norm(repo_root), _report_json_rel(platform_tag).replace("/", os.sep))
    payload = _load_report(path)
    if _token(payload.get("report_id")) == DIST_VERIFY_REPORT_ID:
        return payload
    return {}


def distribution_verify_violations(repo_root: str, *, platform_tag: str = DEFAULT_PLATFORM) -> list[dict]:
    payload = load_distribution_verify_report(repo_root, platform_tag=platform_tag)
    if not payload:
        bundle_root = _default_bundle_root(os.path.join(_norm(repo_root), DEFAULT_OUTPUT_ROOT), platform_tag)
        if not os.path.isdir(bundle_root):
            return [
                {
                    "code": "dist_verify_report_missing",
                    "file_path": _report_json_rel(platform_tag),
                    "message": "distribution verification report is missing",
                    "rule_id": RULE_VERIFY,
                }
            ]
        payload = build_distribution_verify_report(bundle_root, platform_tag=platform_tag, repo_root=repo_root)
    violations: list[dict] = []
    if _token(payload.get("result")) != "complete":
        for item in _as_list(payload.get("errors")):
            row = _as_map(item)
            violations.append(
                {
                    "code": _token(row.get("code")) or "dist_verify_error",
                    "file_path": _token(row.get("path")) or _report_json_rel(platform_tag),
                    "message": _token(row.get("message")) or "distribution verification failed",
                    "rule_id": _token(row.get("rule_id")) or RULE_VERIFY,
                }
            )
    return sorted(
        violations,
        key=lambda row: (
            _token(row.get("rule_id")),
            _token(row.get("code")),
            _token(row.get("file_path")),
            _token(row.get("message")),
        ),
    )


__all__ = [
    "DEFAULT_BUNDLE_REL",
    "DEFAULT_PLATFORM",
    "DIST2_FINAL_DOC_PATH",
    "DIST_VERIFY_REPORT_ID",
    "DIST_VERIFY_RULES_PATH",
    "RULE_ABSOLUTE_PATHS",
    "RULE_NO_XSTACK",
    "RULE_VERIFY",
    "_default_bundle_root",
    "build_distribution_verify_report",
    "distribution_verify_violations",
    "load_distribution_verify_report",
    "render_distribution_verify_report",
    "scan_distribution_absolute_path_leaks",
    "scan_forbidden_distribution_files",
    "write_dist2_final_outputs",
    "write_distribution_verify_outputs",
]
