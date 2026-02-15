#!/usr/bin/env python3
"""Profile-bound deterministic schema checks for FAST/STRICT/FULL XStack runs."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Any, Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.compatx.schema_registry import discover_schema_files, load_schema  # noqa: E402
from tools.xstack.compatx.validator import validate_instance, validate_schema_example  # noqa: E402


DOC_SCHEMA_LINKS = {
    "docs/contracts/session_spec.md": ["session_spec.schema.json"],
    "docs/contracts/authority_context.md": ["authority_context.schema.json"],
    "docs/contracts/law_profile.md": ["law_profile.schema.json"],
    "docs/contracts/lens_contract.md": ["lens.schema.json"],
    "docs/architecture/pack_system.md": ["pack_manifest.schema.json", "bundle_profile.schema.json"],
    "docs/architecture/session_lifecycle.md": ["session_spec.schema.json", "bundle_profile.schema.json"],
    "docs/architecture/srz_contract.md": ["srz_shard.schema.json", "intent_envelope.schema.json"],
    "docs/architecture/hash_anchors.md": ["composite_hash", "tick_hash_anchors"],
    "docs/architecture/deterministic_packaging.md": ["bundle_lockfile.schema.json", "canonical_content_hash", "tools/setup/build"],
    "docs/architecture/setup_and_launcher.md": ["LOCKFILE_MISMATCH", "PACK_INCOMPATIBLE", "tools/launcher/launch"],
    "docs/testing/xstack_profiles.md": ["session_spec.schema.json", "bundle_profile.schema.json", "registry_outputs.schema.json"],
}


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _error(code: str, message: str) -> Dict[str, str]:
    return {"code": str(code), "message": str(message)}


def _load_schema_example(repo_root: str, schema_name: str) -> Dict[str, Any]:
    schema, _path, schema_error = load_schema(repo_root, schema_name)
    if schema_error:
        return {}
    examples = schema.get("examples")
    if not isinstance(examples, list) or not examples:
        return {}
    if not isinstance(examples[0], dict):
        return {}
    return copy.deepcopy(examples[0])


def _fast_checks(repo_root: str) -> Dict[str, Any]:
    checks = []
    errors: List[Dict[str, str]] = []

    schema_files = discover_schema_files(repo_root)
    schema_names = sorted(schema_files.keys())
    if not schema_names:
        errors.append(_error("missing_schemas", "no schemas discovered under schemas/*.schema.json"))
        return {"checks": checks, "errors": errors}

    for schema_name in schema_names:
        result = validate_schema_example(repo_root, schema_name)
        ok = bool(result.get("valid", False))
        checks.append({"check_id": "fast.example.{}".format(schema_name), "ok": ok})
        if not ok:
            for row in result.get("errors", []):
                code = str(row.get("code", "schema_example_invalid"))
                message = "{}: {}".format(schema_name, str(row.get("message", "")))
                errors.append(_error(code, message))

        example = _load_schema_example(repo_root, schema_name)
        if example:
            hash_a = canonical_sha256(example)
            hash_b = canonical_sha256(example)
            hash_ok = hash_a == hash_b
            checks.append({"check_id": "fast.hash_stability.{}".format(schema_name), "ok": hash_ok})
            if not hash_ok:
                errors.append(_error("hash_nondeterministic", "hash mismatch for schema example '{}'".format(schema_name)))

    session_example = _load_schema_example(repo_root, "session_spec")
    if not session_example:
        errors.append(_error("missing_session_example", "session_spec schema example is required for refusal tests"))
        checks.append({"check_id": "fast.refusal.fixture", "ok": False})
        return {"checks": checks, "errors": errors}
    checks.append({"check_id": "fast.refusal.fixture", "ok": True})

    missing_required = copy.deepcopy(session_example)
    if "universe_id" in missing_required:
        del missing_required["universe_id"]
    missing_result = validate_instance(repo_root, "session_spec", missing_required, strict_top_level=True)
    missing_ok = (not bool(missing_result.get("valid", True))) and any(
        str(row.get("code", "")) == "required_missing" for row in (missing_result.get("errors") or [])
    )
    checks.append({"check_id": "fast.refusal.missing_required", "ok": missing_ok})
    if not missing_ok:
        errors.append(_error("missing_required_refusal_failed", "missing required field refusal test failed"))

    unknown_top = copy.deepcopy(session_example)
    unknown_top["unknown_control_field"] = True
    unknown_result = validate_instance(repo_root, "session_spec", unknown_top, strict_top_level=True)
    unknown_ok = (not bool(unknown_result.get("valid", True))) and any(
        str(row.get("code", "")) == "unknown_top_level_field" for row in (unknown_result.get("errors") or [])
    )
    checks.append({"check_id": "fast.refusal.unknown_top_level", "ok": unknown_ok})
    if not unknown_ok:
        errors.append(_error("unknown_top_level_refusal_failed", "unknown top-level field refusal test failed"))

    version_mismatch = copy.deepcopy(session_example)
    version_mismatch["schema_version"] = "9.9.9"
    version_result = validate_instance(repo_root, "session_spec", version_mismatch, strict_top_level=True)
    version_ok = (not bool(version_result.get("valid", True))) and any(
        str(row.get("code", "")).startswith("refuse.compatx.") for row in (version_result.get("errors") or [])
    )
    checks.append({"check_id": "fast.refusal.version_mismatch", "ok": version_ok})
    if not version_ok:
        errors.append(_error("version_mismatch_refusal_failed", "version mismatch refusal test failed"))

    return {"checks": checks, "errors": errors}


def _strict_checks(repo_root: str) -> Dict[str, Any]:
    checks = []
    errors: List[Dict[str, str]] = []

    for rel_path in sorted(DOC_SCHEMA_LINKS.keys()):
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full_path):
            checks.append({"check_id": "strict.docs_link.{}".format(rel_path), "ok": False})
            errors.append(_error("missing_doc", "missing strict hook doc: {}".format(rel_path)))
            continue
        try:
            with open(full_path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            text = ""

        ok = True
        for token in DOC_SCHEMA_LINKS[rel_path]:
            if token not in text:
                ok = False
                errors.append(_error("docs_schema_reference_missing", "{} missing schema reference {}".format(rel_path, token)))
        if "1.0.0" not in text:
            ok = False
            errors.append(_error("docs_version_missing", "{} missing version marker 1.0.0".format(rel_path)))
        checks.append({"check_id": "strict.docs_link.{}".format(rel_path), "ok": ok})

    return {"checks": checks, "errors": errors}


def _deterministic_checks(raw_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        [{"check_id": str(row.get("check_id", "")), "ok": bool(row.get("ok", False))} for row in raw_checks],
        key=lambda row: str(row.get("check_id", "")),
    )


def _deterministic_errors(raw_errors: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return sorted(
        [{"code": str(row.get("code", "")), "message": str(row.get("message", ""))} for row in raw_errors],
        key=lambda row: (str(row.get("code", "")), str(row.get("message", ""))),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic schema checks for an XStack profile.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--profile", default="FAST", choices=("FAST", "STRICT", "FULL"))
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    profile = str(args.profile).strip().upper() or "FAST"

    checks: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []

    fast = _fast_checks(repo_root)
    checks.extend(fast.get("checks", []))
    errors.extend(fast.get("errors", []))

    if profile in {"STRICT", "FULL"}:
        strict = _strict_checks(repo_root)
        checks.extend(strict.get("checks", []))
        errors.extend(strict.get("errors", []))

    payload = {
        "profile": profile,
        "result": "complete" if not errors else "refused",
        "checks": _deterministic_checks(checks),
        "errors": _deterministic_errors(errors),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
