"""Deterministic reporting and enforcement helpers for DIST-0."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Iterable, Mapping


from release import build_release_manifest, verify_release_manifest, write_release_manifest
from tools.xstack.compatx.canonical_json import canonical_sha256


DISTRIBUTION_MODEL_PATH = "docs/release/DISTRIBUTION_MODEL.md"
DISTRIBUTION_ARCHITECTURE_FREEZE_PATH = "docs/audit/DISTRIBUTION_ARCHITECTURE_FREEZE.md"
DISTRIBUTION_ARCHITECTURE_REPORT_PATH = "data/audit/distribution_architecture_report.json"
RELEASE_MANIFEST_REL = "dist/manifests/release_manifest.json"

RULE_NO_DEV_ARTIFACTS = "INV-DIST-NO-DEV-ARTIFACTS"
RULE_INCLUDES_RELEASE_MANIFEST = "INV-DIST-INCLUDES-RELEASE-MANIFEST"
RULE_PASSES_VERIFY = "INV-DIST-PASSES-VERIFY"

DEFAULT_RELEASE_TAG = "v0.0.0-mock"
DEFAULT_DIST_ROOT = "dist"
DEFAULT_CHANNEL_ID = "mock"
DEFAULT_PLATFORM_TAG = "platform.portable"

CANONICAL_ROOT_FILES = (
    "install.manifest.json",
    "manifests/release_manifest.json",
    "bin/engine",
    "bin/game",
    "bin/client",
    "bin/server",
    "bin/setup",
    "bin/launcher",
    "store/packs",
    "store/profiles",
    "store/locks",
    "instances/default/instance.manifest.json",
    "saves",
    "docs",
    "LICENSE",
    "README",
)

EXCLUDED_DEV_NAMES = frozenset(
    {
        ".git",
        ".gitkeep",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
)
EXCLUDED_DEV_SUFFIXES: tuple[str, ...] = ()


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload or {}), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/").lstrip("./")


def _dist_root(repo_root: str, dist_root: str = DEFAULT_DIST_ROOT) -> str:
    if os.path.isabs(dist_root):
        return os.path.normpath(os.path.abspath(dist_root))
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, dist_root)))


def _canonical_bundle_roots(dist_abs: str) -> list[str]:
    rows: list[str] = []
    direct_install = os.path.join(dist_abs, "install.manifest.json")
    if os.path.isfile(direct_install):
        rows.append(dist_abs)
    tag_root = os.path.join(dist_abs, DEFAULT_RELEASE_TAG)
    if os.path.isdir(tag_root):
        for name in sorted(os.listdir(tag_root)):
            candidate = os.path.join(tag_root, name)
            if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "install.manifest.json")):
                rows.append(candidate)
    return sorted({_norm_rel(os.path.relpath(row, dist_abs)) if row != dist_abs else "." for row in rows})


def _required_path_rows(root_abs: str) -> list[dict]:
    rows = []
    for rel_path in CANONICAL_ROOT_FILES:
        rows.append(
            {
                "path": rel_path,
                "present": os.path.exists(os.path.join(root_abs, rel_path.replace("/", os.sep))),
            }
        )
    return rows


def _scan_dev_artifacts(root_abs: str) -> list[str]:
    hits: list[str] = []
    if not os.path.isdir(root_abs):
        return hits
    for current_root, dirnames, filenames in os.walk(root_abs):
        dirnames[:] = sorted(dirnames)
        rel_root = os.path.relpath(current_root, root_abs)
        rel_root_norm = "" if rel_root in (".", "") else _norm_rel(rel_root)
        for dirname in dirnames:
            if dirname in EXCLUDED_DEV_NAMES:
                hits.append(dirname if not rel_root_norm else "{}/{}".format(rel_root_norm, dirname))
        for filename in sorted(filenames):
            if filename in EXCLUDED_DEV_NAMES or filename.endswith(EXCLUDED_DEV_SUFFIXES):
                hits.append(filename if not rel_root_norm else "{}/{}".format(rel_root_norm, filename))
    return sorted(set(hits))


def _manifest_files_under(root_abs: str) -> list[str]:
    rows: list[str] = []
    if not os.path.isdir(root_abs):
        return rows
    manifest_suffixes = {
        "install.manifest.json",
        "instance.manifest.json",
        "save.manifest.json",
        "release_manifest.json",
        "manifest.json",
    }
    for current_root, _, filenames in os.walk(root_abs):
        rel_root = os.path.relpath(current_root, root_abs)
        rel_root_norm = "" if rel_root in (".", "") else _norm_rel(rel_root)
        for filename in sorted(filenames):
            if filename in manifest_suffixes:
                rows.append(filename if not rel_root_norm else "{}/{}".format(rel_root_norm, filename))
    return sorted(set(rows))


def _walk_strings(value: object, *, prefix: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key in sorted(value):
            next_prefix = key if not prefix else "{}.{}".format(prefix, key)
            yield from _walk_strings(value[key], prefix=next_prefix)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            next_prefix = "{}[{}]".format(prefix, index) if prefix else "[{}]".format(index)
            yield from _walk_strings(item, prefix=next_prefix)
        return
    if isinstance(value, str):
        yield (prefix or "<root>", value)


def _looks_like_absolute_path(token: str) -> bool:
    value = _token(token)
    if not value:
        return False
    if len(value) >= 3 and value[1] == ":" and value[2] in ("\\", "/"):
        return True
    if value.startswith("//") or value.startswith("\\\\"):
        return True
    if value.startswith("/") and not value.startswith("//"):
        return True
    return False


def _collect_absolute_path_hits(root_abs: str) -> list[dict]:
    hits: list[dict] = []
    for rel_path in _manifest_files_under(root_abs):
        payload, error = _read_json(os.path.join(root_abs, rel_path.replace("/", os.sep)))
        if error:
            continue
        for dotted_path, value in _walk_strings(payload):
            if _looks_like_absolute_path(value):
                hits.append({"path": rel_path, "field": dotted_path, "value": _token(value)})
    return sorted(hits, key=lambda row: (_token(row.get("path")), _token(row.get("field")), _token(row.get("value"))))


def _load_release_manifest_hash(path: str) -> tuple[str, str]:
    payload, error = _read_json(path)
    if error:
        return "", error
    return _token(payload.get("manifest_hash")).lower(), ""


def _freeze_doc_text(report: Mapping[str, object]) -> str:
    lines: list[str] = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DIST",
        "Replacement Target: DIST-1 packaged bundle baseline and DIST-2 installer constitution",
        "",
        "# Distribution Architecture Freeze",
        "",
        "## Distribution Types",
        "",
        "- Portable Full Bundle",
        "- Installed Bundle",
        "- Headless Server Bundle",
        "- Tools-Only Bundle",
        "- Development Bundle (optional, experimental)",
        "",
        "## Layout Diagram",
        "",
        "```text",
        "<root>/",
        "  install.manifest.json",
        "  manifests/",
        "    release_manifest.json",
        "  bin/",
        "    engine",
        "    game",
        "    client",
        "    server",
        "    setup",
        "    launcher",
        "  store/",
        "    packs/",
        "    profiles/",
        "    locks/",
        "  instances/",
        "    default/",
        "      instance.manifest.json",
        "  saves/",
        "  docs/",
        "  LICENSE",
        "  README",
        "```",
        "",
        "## Required Artifacts Checklist",
        "",
        "- `install.manifest.json`",
        "- `manifests/release_manifest.json`",
        "- pinned semantic contract registry surface",
        "- default linked instance",
        "- default base-universe `pack_lock`",
        "",
        "## Portability Checklist",
        "",
        "- install root discovered by adjacency",
        "- virtual paths only",
        "- direct product launch from `bin/`",
        "- no mandatory install registry dependency",
        "- offline verification via release manifest tooling",
        "",
        "## Current Staging Observations",
        "",
        "- Canonical bundle roots detected: {}".format(", ".join(_as_list(report.get("bundle_roots")) or ["none"])),
        "- Staging release manifest present: {}".format("yes" if report.get("staging_release_manifest_present") else "no"),
        "- Fresh temporary manifest verifies current staged dist: {}".format(_token(_as_map(report.get("generated_manifest_verification")).get("result")) or "unknown"),
        "- Shipped staging release manifest verification result: {}".format(_token(_as_map(report.get("staging_manifest_verification")).get("result")) or "not_run"),
        "- Shipped staging manifest matches fresh generated manifest: {}".format("yes" if report.get("staging_manifest_matches_generated") else "no"),
        "",
        "### Current DIST-1 Gaps",
        "",
    ]
    for row in _as_list(report.get("staging_gap_paths")):
        lines.append("- missing canonical bundle path: `{}`".format(_token(row)))
    if not _as_list(report.get("staging_gap_paths")):
        lines.append("- no canonical bundle path gaps were observed")
    if _as_list(report.get("staging_dev_artifacts")):
        lines.extend(["", "### Staging-Only Exclusions Still Present", ""])
        for row in _as_list(report.get("staging_dev_artifacts")):
            lines.append("- staging exclusion to remove during DIST-1 packaging: `{}`".format(_token(row)))
    lines.extend(["", "## Portability and Verification Readiness", ""])
    lines.append("- Absolute-path hits in staged manifests: {}".format(int(len(_as_list(report.get("absolute_path_hits"))))))
    lines.append("- Ready for DIST-1 packaging pass: {}".format("yes" if not _as_list(report.get("staging_gap_paths")) else "not yet"))
    return "\n".join(lines).rstrip() + "\n"


def build_distribution_model_report(repo_root: str, *, dist_root: str = DEFAULT_DIST_ROOT) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    dist_abs = _dist_root(root, dist_root=dist_root)
    violations: list[dict] = []
    warnings: list[dict] = []

    for rel_path, message, rule_id in (
        (DISTRIBUTION_MODEL_PATH, "distribution model doctrine is required", RULE_INCLUDES_RELEASE_MANIFEST),
        ("tools/release/distribution_model_common.py", "distribution model helper is required", RULE_INCLUDES_RELEASE_MANIFEST),
        ("tools/release/tool_run_distribution_model.py", "distribution model report tool is required", RULE_INCLUDES_RELEASE_MANIFEST),
    ):
        if not os.path.isfile(os.path.join(root, rel_path.replace("/", os.sep))):
            violations.append({"code": "distribution_required_file_missing", "file_path": rel_path, "message": message, "rule_id": rule_id})

    staging_release_manifest_abs = os.path.join(dist_abs, "manifests", "release_manifest.json")
    bundle_roots = _canonical_bundle_roots(dist_abs)
    staging_release_manifest_present = os.path.isfile(staging_release_manifest_abs)
    if not staging_release_manifest_present:
        violations.append(
            {
                "code": "distribution_release_manifest_missing",
                "file_path": RELEASE_MANIFEST_REL,
                "message": "staged distribution surface must include manifests/release_manifest.json",
                "rule_id": RULE_INCLUDES_RELEASE_MANIFEST,
            }
        )

    generated_manifest = {}
    generated_manifest_verification = {"result": "refused", "errors": [{"code": "refusal.dist_root.missing", "message": "distribution root is missing", "path": _norm_rel(dist_abs)}], "warnings": []}
    staging_manifest_verification = {"result": "not_run", "errors": [], "warnings": []}
    staging_manifest_matches_generated = False
    staging_manifest_hash = ""

    if os.path.isdir(dist_abs):
        generated_manifest = build_release_manifest(dist_abs, platform_tag=DEFAULT_PLATFORM_TAG, channel_id=DEFAULT_CHANNEL_ID, repo_root=root)
        with tempfile.TemporaryDirectory(prefix="dominium_dist_model_") as tmp_dir:
            manifest_path = os.path.join(tmp_dir, "release_manifest.json")
            write_release_manifest(dist_abs, generated_manifest, manifest_path=manifest_path)
            generated_manifest_verification = verify_release_manifest(dist_abs, manifest_path, repo_root=root)
        if _token(generated_manifest_verification.get("result")) != "complete":
            violations.append(
                {
                    "code": "distribution_generated_manifest_verify_failed",
                    "file_path": "tools/release/tool_verify_release_manifest.py",
                    "message": "freshly generated release manifest must verify offline against dist",
                    "rule_id": RULE_PASSES_VERIFY,
                }
            )
        if staging_release_manifest_present:
            staging_manifest_verification = verify_release_manifest(dist_abs, staging_release_manifest_abs, repo_root=root)
            staging_manifest_hash, staging_manifest_error = _load_release_manifest_hash(staging_release_manifest_abs)
            if staging_manifest_error:
                warnings.append({"code": "distribution_staging_manifest_unreadable", "file_path": RELEASE_MANIFEST_REL, "message": "staged release manifest could not be read ({})".format(staging_manifest_error)})
            generated_manifest_hash = _token(generated_manifest.get("manifest_hash")).lower()
            staging_manifest_matches_generated = bool(staging_manifest_hash and staging_manifest_hash == generated_manifest_hash)
            if not staging_manifest_matches_generated:
                warnings.append({"code": "distribution_staging_manifest_drift", "file_path": RELEASE_MANIFEST_REL, "message": "staged release manifest differs from the current deterministic dist surface"})
            if _token(staging_manifest_verification.get("result")) != "complete":
                warnings.append({"code": "distribution_staging_manifest_verify_failed", "file_path": RELEASE_MANIFEST_REL, "message": "staged release manifest does not currently verify against the staged dist surface"})

    absolute_path_hits = _collect_absolute_path_hits(dist_abs) if os.path.isdir(dist_abs) else []
    for row in absolute_path_hits:
        violations.append(
            {
                "code": "distribution_manifest_absolute_path",
                "file_path": _token(row.get("path")),
                "message": "manifest field '{}' contains an absolute path".format(_token(row.get("field"))),
                "rule_id": RULE_INCLUDES_RELEASE_MANIFEST,
            }
        )

    staging_gap_paths = [_token(row.get("path")) for row in _required_path_rows(dist_abs) if not bool(row.get("present"))] if os.path.isdir(dist_abs) else []
    staging_dev_artifacts = _scan_dev_artifacts(dist_abs) if os.path.isdir(dist_abs) else []
    if staging_gap_paths:
        warnings.append({"code": "distribution_staging_bundle_incomplete", "file_path": DEFAULT_DIST_ROOT, "message": "staging dist is not yet laid out as the canonical portable bundle"})
    if staging_dev_artifacts:
        warnings.append({"code": "distribution_staging_dev_artifacts_present", "file_path": DEFAULT_DIST_ROOT, "message": "staging dist still contains pre-packaging development artifacts"})

    for rel_root in bundle_roots:
        bundle_abs = dist_abs if rel_root == "." else os.path.join(dist_abs, rel_root.replace("/", os.sep))
        for missing_path in [_token(row.get("path")) for row in _required_path_rows(bundle_abs) if not bool(row.get("present"))]:
            violations.append(
                {
                    "code": "distribution_bundle_required_path_missing",
                    "file_path": "{}/{}".format(rel_root, missing_path) if rel_root != "." else missing_path,
                    "message": "canonical bundle is missing required path '{}'".format(missing_path),
                    "rule_id": RULE_INCLUDES_RELEASE_MANIFEST,
                }
            )
        for rel_path in _scan_dev_artifacts(bundle_abs):
            violations.append(
                {
                    "code": "distribution_bundle_dev_artifact_present",
                    "file_path": "{}/{}".format(rel_root, rel_path) if rel_root != "." else rel_path,
                    "message": "canonical distribution bundle must not include development artifact '{}'".format(rel_path),
                    "rule_id": RULE_NO_DEV_ARTIFACTS,
                }
            )

    report = {
        "report_id": "distribution.architecture.v1",
        "result": "complete" if not violations else "violation",
        "distribution_model_path": DISTRIBUTION_MODEL_PATH,
        "freeze_doc_path": DISTRIBUTION_ARCHITECTURE_FREEZE_PATH,
        "dist_root": dist_abs.replace("\\", "/"),
        "release_tag": DEFAULT_RELEASE_TAG,
        "channel_id": DEFAULT_CHANNEL_ID,
        "bundle_roots": bundle_roots,
        "staging_release_manifest_present": staging_release_manifest_present,
        "staging_manifest_hash": staging_manifest_hash,
        "generated_manifest_hash": _token(generated_manifest.get("manifest_hash")).lower(),
        "generated_manifest_verification": dict(generated_manifest_verification or {}),
        "staging_manifest_verification": dict(staging_manifest_verification or {}),
        "staging_manifest_matches_generated": staging_manifest_matches_generated,
        "staging_gap_paths": sorted(staging_gap_paths),
        "staging_dev_artifacts": staging_dev_artifacts,
        "absolute_path_hits": absolute_path_hits,
        "warnings": sorted([dict(row or {}) for row in warnings], key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message")))),
        "violations": sorted([dict(row or {}) for row in violations], key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message")))),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def distribution_model_violations(repo_root: str) -> list[dict]:
    return list(build_distribution_model_report(repo_root).get("violations") or [])


def write_distribution_model_outputs(
    repo_root: str,
    *,
    dist_root: str = DEFAULT_DIST_ROOT,
    report_path: str = DISTRIBUTION_ARCHITECTURE_REPORT_PATH,
    doc_path: str = DISTRIBUTION_ARCHITECTURE_FREEZE_PATH,
) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    report = build_distribution_model_report(root, dist_root=dist_root)
    report_abs = os.path.join(root, report_path.replace("/", os.sep)) if not os.path.isabs(report_path) else report_path
    doc_abs = os.path.join(root, doc_path.replace("/", os.sep)) if not os.path.isabs(doc_path) else doc_path
    _write_json(report_abs, report)
    os.makedirs(os.path.dirname(doc_abs), exist_ok=True)
    with open(doc_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(_freeze_doc_text(report))
    return report


__all__ = [
    "DEFAULT_CHANNEL_ID",
    "DEFAULT_DIST_ROOT",
    "DEFAULT_PLATFORM_TAG",
    "DEFAULT_RELEASE_TAG",
    "DISTRIBUTION_ARCHITECTURE_FREEZE_PATH",
    "DISTRIBUTION_ARCHITECTURE_REPORT_PATH",
    "DISTRIBUTION_MODEL_PATH",
    "RULE_INCLUDES_RELEASE_MANIFEST",
    "RULE_NO_DEV_ARTIFACTS",
    "RULE_PASSES_VERIFY",
    "build_distribution_model_report",
    "distribution_model_violations",
    "write_distribution_model_outputs",
]
