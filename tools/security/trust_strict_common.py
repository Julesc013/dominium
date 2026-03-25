"""Deterministic TRUST-STRICT-VERIFY-0 helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.meta.stability import build_stability_marker  # noqa: E402
from src.release import canonicalize_release_index, load_release_index, release_index_signed_hash  # noqa: E402
from src.release.release_manifest_engine import build_mock_signature_block  # noqa: E402
from src.security.trust import (  # noqa: E402
    ARTIFACT_KIND_LICENSE_CAPABILITY,
    ARTIFACT_KIND_PACK,
    ARTIFACT_KIND_RELEASE_INDEX,
    ARTIFACT_KIND_RELEASE_MANIFEST,
    DEFAULT_TRUST_POLICY_ID,
    LICENSE_CAPABILITY_EXTENSION_REQUESTED_KEY,
    LICENSE_CAPABILITY_SCHEMA_ID,
    REFUSAL_TRUST_ROOT_NOT_TRUSTED,
    REFUSAL_TRUST_SIGNATURE_MISSING,
    TRUST_POLICY_ANARCHY,
    TRUST_POLICY_STRICT,
    build_license_capability_artifact,
    canonicalize_signature_record,
    deterministic_fingerprint,
    effective_trust_policy_id,
    license_capability_signed_hash,
    verify_artifact_trust,
    verify_license_capability_artifact,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


TRUST_STRICT_RUN_SCHEMA_ID = "dominium.schema.audit.trust_strict_run"
TRUST_STRICT_BASELINE_SCHEMA_ID = "dominium.schema.governance.trust_strict_baseline"
TRUST_STRICT_VERSION = 0
TRUST_STRICT_STABILITY_CLASS = "stable"
TRUST_STRICT_REQUIRED_TAG = "TRUST-REGRESSION-UPDATE"

TRUST_STRICT_RETRO_AUDIT_REL = os.path.join("docs", "audit", "TRUST_STRICT0_RETRO_AUDIT.md")
TRUST_STRICT_MODEL_DOC_REL = os.path.join("docs", "security", "TRUST_STRICT_MODEL_v0_0_0.md")
TRUST_STRICT_RUN_DOC_REL = os.path.join("docs", "audit", "TRUST_STRICT_SUITE_RUN.md")
TRUST_STRICT_RUN_JSON_REL = os.path.join("data", "audit", "trust_strict_run.json")
TRUST_STRICT_BASELINE_REL = os.path.join("data", "regression", "trust_strict_baseline.json")
TRUST_STRICT_BASELINE_DOC_REL = os.path.join("docs", "audit", "TRUST_STRICT_BASELINE.md")
TRUST_FIXTURE_DIR_REL = os.path.join("data", "baselines", "trust")
UNSIGNED_RELEASE_INDEX_REL = os.path.join(TRUST_FIXTURE_DIR_REL, "unsigned_release_index.json")
SIGNED_RELEASE_INDEX_REL = os.path.join(TRUST_FIXTURE_DIR_REL, "signed_release_index.json")
UNSIGNED_OFFICIAL_PACK_REL = os.path.join(TRUST_FIXTURE_DIR_REL, "unsigned_official_pack.compat.json")
SIGNED_LICENSE_CAPABILITY_REL = os.path.join(TRUST_FIXTURE_DIR_REL, "signed_license_capability.json")
TRUST_STRICT_TOOL_REL = os.path.join("tools", "security", "tool_run_trust_strict_suite")
TRUST_STRICT_TOOL_PY_REL = os.path.join("tools", "security", "tool_run_trust_strict_suite.py")
LICENSE_CAPABILITY_SCHEMA_REL = os.path.join("schema", "security", "license_capability_artifact.schema")
LICENSE_CAPABILITY_SCHEMA_JSON_REL = os.path.join("schemas", "license_capability_artifact.schema.json")
UPDATE_SIM_BASELINE_INDEX_REL = os.path.join("data", "baselines", "update_sim", "release_index_baseline.json")

OFFICIAL_SIGNER_ID = "signer.fixture.official"
UNTRUSTED_SIGNER_ID = "signer.fixture.untrusted"
PREMIUM_NAMESPACE_CAPABILITY = "cap.premium.*"
REQUESTED_CAPABILITY_IDS = [
    "cap.premium.feature.preview",
    "cap.premium.render.4k",
    "cap.ui.tui",
]
EXPECTED_PREMIUM_AVAILABLE = [
    "cap.premium.feature.preview",
    "cap.premium.render.4k",
]
EXPECTED_PREMIUM_DEGRADED = ["cap.ui.tui"]

_FIXTURE_PATHS = {
    "unsigned_release_index": UNSIGNED_RELEASE_INDEX_REL,
    "signed_release_index": SIGNED_RELEASE_INDEX_REL,
    "unsigned_official_pack": UNSIGNED_OFFICIAL_PACK_REL,
    "signed_license_capability": SIGNED_LICENSE_CAPABILITY_REL,
}


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: object) -> list[str]:
    return sorted({str(item).strip() for item in _as_list(values) if str(item).strip()})


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
            if str(key).strip()
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _repo_abs(repo_root: str, rel_path: str) -> str:
    token = _token(rel_path)
    if not token:
        return os.path.normpath(os.path.abspath(repo_root))
    if os.path.isabs(token):
        return os.path.normpath(os.path.abspath(token))
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, token.replace("/", os.sep))))


def _relative_to(repo_root: str, path: str) -> str:
    token = _token(path)
    if not token:
        return ""
    abs_path = os.path.normpath(os.path.abspath(token))
    try:
        rel = os.path.relpath(abs_path, repo_root)
    except ValueError:
        return _norm(abs_path)
    return _norm(rel)


def _ensure_dir(path: str) -> None:
    token = _token(path)
    if token and not os.path.isdir(token):
        os.makedirs(token, exist_ok=True)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return path


def _write_text(path: str, text: str) -> str:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return path


def _load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, TypeError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def trust_strict_run_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def trust_strict_baseline_hash(payload: Mapping[str, object]) -> str:
    return canonical_sha256(dict(dict(payload or {}), deterministic_fingerprint=""))


def _trusted_root(*, signer_id: str, trust_level_id: str) -> dict:
    payload = {
        "signer_id": _token(signer_id),
        "public_key_bytes": "mock-public-key:{}".format(_token(signer_id)),
        "trust_level_id": _token(trust_level_id),
        "deterministic_fingerprint": "",
        "extensions": {"official.source": "OMEGA-7"},
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def _official_root() -> dict:
    return _trusted_root(signer_id=OFFICIAL_SIGNER_ID, trust_level_id="trust.official_signed")


def _untrusted_root() -> dict:
    return _trusted_root(signer_id=UNTRUSTED_SIGNER_ID, trust_level_id="trust.thirdparty_signed")


def _signature_row(*, signer_id: str, signed_hash: str) -> dict:
    return canonicalize_signature_record(
        build_mock_signature_block(
            signer_id=_token(signer_id),
            signed_hash=_token(signed_hash).lower(),
        )
    )


def _fixture_release_index(repo_root: str) -> dict:
    base = load_release_index(_repo_abs(repo_root, UPDATE_SIM_BASELINE_INDEX_REL))
    payload = dict(base)
    payload["signatures"] = []
    extensions = dict(_as_map(payload.get("extensions")))
    extensions["official.source"] = "OMEGA-7"
    extensions["official.fixture_id"] = "omega7.trust.release_index"
    payload["extensions"] = extensions
    return canonicalize_release_index(payload)


def _signed_release_index(unsigned_payload: Mapping[str, object]) -> dict:
    payload = dict(unsigned_payload or {})
    signed_hash = release_index_signed_hash(payload)
    payload["signatures"] = [_signature_row(signer_id=OFFICIAL_SIGNER_ID, signed_hash=signed_hash)]
    return canonicalize_release_index(payload)


def _unsigned_official_pack_fixture() -> dict:
    payload = {
        "schema_id": "dominium.fixture.trust.official_pack_compat",
        "schema_version": "1.0.0",
        "artifact_kind_id": ARTIFACT_KIND_PACK,
        "pack_id": "pack.official.fixture",
        "distribution_channel": "official",
        "component_kind": "pack_compat",
        "extensions": {
            "official.source": "OMEGA-7",
            "official.is_official_pack_fixture": True,
            "official.signature_state": "unsigned",
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def _license_fixture(*, signer_id: str) -> dict:
    extensions = {
        "official.source": "OMEGA-7",
        LICENSE_CAPABILITY_EXTENSION_REQUESTED_KEY: list(REQUESTED_CAPABILITY_IDS),
    }
    unsigned_payload = build_license_capability_artifact(
        artifact_id="identity.license_capability.official.fixture",
        enabled_capabilities=[PREMIUM_NAMESPACE_CAPABILITY],
        valid_from_release="release.v0.0.0-mock",
        extensions=extensions,
        signature_records=[],
        stability_class_id="provisional",
    )
    signed_hash = license_capability_signed_hash(unsigned_payload)
    return build_license_capability_artifact(
        artifact_id="identity.license_capability.official.fixture",
        enabled_capabilities=[PREMIUM_NAMESPACE_CAPABILITY],
        valid_from_release="release.v0.0.0-mock",
        extensions=extensions,
        signature_records=[_signature_row(signer_id=_token(signer_id), signed_hash=signed_hash)],
        stability_class_id="provisional",
    )


def build_trust_fixture_payloads(repo_root: str) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    unsigned_release_index = _fixture_release_index(root)
    signed_release_index = _signed_release_index(unsigned_release_index)
    unsigned_pack = _unsigned_official_pack_fixture()
    signed_license_capability = _license_fixture(signer_id=OFFICIAL_SIGNER_ID)
    return {
        "unsigned_release_index": unsigned_release_index,
        "signed_release_index": signed_release_index,
        "unsigned_official_pack": unsigned_pack,
        "signed_license_capability": signed_license_capability,
    }


def write_trust_fixture_outputs(repo_root: str) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    payloads = build_trust_fixture_payloads(root)
    written = {}
    for fixture_id, rel_path in sorted(_FIXTURE_PATHS.items()):
        written[fixture_id] = _write_canonical_json(_repo_abs(root, rel_path), _as_map(payloads.get(fixture_id)))
    return {"fixtures": payloads, "written": written}


def _warning_codes(report: Mapping[str, object] | None) -> list[str]:
    return _sorted_tokens([_token(_as_map(row).get("code")) for row in _as_list(_as_map(report).get("warnings"))])


def _case_row(
    *,
    case_id: str,
    description: str,
    result: str,
    refusal_code: str = "",
    remediation_hint: str = "",
    details: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "case_id": _token(case_id),
        "description": _token(description),
        "result": _token(result) or "refused",
        "refusal_code": _token(refusal_code),
        "remediation_hint": _token(remediation_hint),
        "details": _normalize_tree(details or {}),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def _artifact_summary(repo_root: str, fixture_id: str, payload: Mapping[str, object]) -> dict:
    rel_path = _FIXTURE_PATHS[fixture_id]
    return {
        "fixture_id": fixture_id,
        "path": rel_path,
        "content_hash": canonical_sha256(dict(payload or {})),
        "signed_hash": release_index_signed_hash(payload) if fixture_id.endswith("release_index") else "",
        "exists": os.path.isfile(_repo_abs(repo_root, rel_path)),
    }


def _signed_release_manifest_result(repo_root: str, trust_roots: Sequence[Mapping[str, object]]) -> dict:
    signed_hash = canonical_sha256({"fixture_id": "omega7.signed_release_manifest"})
    return verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_RELEASE_MANIFEST,
        content_hash=signed_hash,
        signatures=[_signature_row(signer_id=OFFICIAL_SIGNER_ID, signed_hash=signed_hash)],
        trust_policy_id=TRUST_POLICY_STRICT,
        repo_root=repo_root,
        trust_roots=trust_roots,
    )


def _policy_matrix(repo_root: str, unsigned_release_index: Mapping[str, object], trust_roots: Sequence[Mapping[str, object]]) -> dict:
    signed_hash = release_index_signed_hash(unsigned_release_index)
    matrix = {}
    for policy_id in (DEFAULT_TRUST_POLICY_ID, TRUST_POLICY_STRICT, TRUST_POLICY_ANARCHY):
        report = verify_artifact_trust(
            artifact_kind=ARTIFACT_KIND_RELEASE_INDEX,
            content_hash=signed_hash,
            signatures=[],
            trust_policy_id=policy_id,
            repo_root=repo_root,
            trust_roots=trust_roots,
        )
        matrix[policy_id] = {
            "result": _token(report.get("result")),
            "refusal_code": _token(report.get("refusal_code")),
            "warning_codes": _warning_codes(report),
            "signature_status": _token(report.get("signature_status")),
            "deterministic_fingerprint": _token(report.get("deterministic_fingerprint")),
        }
    return dict(sorted(matrix.items()))


def _mod_policy_bindings() -> dict:
    return {
        "mod_policy.anarchy": effective_trust_policy_id(mod_policy_id="mod_policy.anarchy"),
        "mod_policy.lab": effective_trust_policy_id(mod_policy_id="mod_policy.lab"),
        "mod_policy.strict": effective_trust_policy_id(mod_policy_id="mod_policy.strict"),
    }


def _commercialization_hook() -> dict:
    payload = {
        "artifact_kind_id": ARTIFACT_KIND_LICENSE_CAPABILITY,
        "schema_id": LICENSE_CAPABILITY_SCHEMA_ID,
        "capability_namespace": PREMIUM_NAMESPACE_CAPABILITY,
        "verification_mode": "offline_trust_only",
        "runtime_effect_scope": "capability_availability_only",
        "network_access_required": False,
        "payment_logic_present": False,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def run_trust_strict_suite(repo_root: str, *, write_outputs: bool = False) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    fixture_payloads = build_trust_fixture_payloads(root)
    official_roots = [_official_root()]

    unsigned_release_index = _as_map(fixture_payloads.get("unsigned_release_index"))
    signed_release_index = _as_map(fixture_payloads.get("signed_release_index"))
    unsigned_pack = _as_map(fixture_payloads.get("unsigned_official_pack"))
    signed_license = _as_map(fixture_payloads.get("signed_license_capability"))

    unsigned_release_hash = release_index_signed_hash(unsigned_release_index)
    signed_release_hash = release_index_signed_hash(signed_release_index)
    unsigned_pack_hash = canonical_sha256(unsigned_pack)

    default_unsigned = verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_RELEASE_INDEX,
        content_hash=unsigned_release_hash,
        signatures=[],
        trust_policy_id=DEFAULT_TRUST_POLICY_ID,
        repo_root=root,
        trust_roots=official_roots,
    )
    strict_unsigned_release = verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_RELEASE_INDEX,
        content_hash=unsigned_release_hash,
        signatures=[],
        trust_policy_id=TRUST_POLICY_STRICT,
        repo_root=root,
        trust_roots=official_roots,
    )
    strict_unsigned_pack = verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_PACK,
        content_hash=unsigned_pack_hash,
        signatures=[],
        trust_policy_id=TRUST_POLICY_STRICT,
        repo_root=root,
        trust_roots=official_roots,
    )
    strict_signed_release_index = verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_RELEASE_INDEX,
        content_hash=signed_release_hash,
        signatures=_as_list(signed_release_index.get("signatures")),
        trust_policy_id=TRUST_POLICY_STRICT,
        repo_root=root,
        trust_roots=official_roots,
    )
    strict_signed_release_manifest = _signed_release_manifest_result(root, official_roots)

    unsigned_license = build_license_capability_artifact(
        artifact_id="identity.license_capability.official.fixture",
        enabled_capabilities=[PREMIUM_NAMESPACE_CAPABILITY],
        valid_from_release="release.v0.0.0-mock",
        extensions={
            "official.source": "OMEGA-7",
            LICENSE_CAPABILITY_EXTENSION_REQUESTED_KEY: list(REQUESTED_CAPABILITY_IDS),
        },
        signature_records=[],
        stability_class_id="provisional",
    )
    untrusted_license = _license_fixture(signer_id=UNTRUSTED_SIGNER_ID)
    signed_license_result = verify_license_capability_artifact(
        signed_license,
        repo_root=root,
        trust_roots=official_roots,
        requested_capability_ids=REQUESTED_CAPABILITY_IDS,
    )
    unsigned_license_result = verify_license_capability_artifact(
        unsigned_license,
        repo_root=root,
        trust_roots=official_roots,
        requested_capability_ids=REQUESTED_CAPABILITY_IDS,
    )
    untrusted_license_result = verify_license_capability_artifact(
        untrusted_license,
        repo_root=root,
        trust_roots=official_roots,
        requested_capability_ids=REQUESTED_CAPABILITY_IDS,
    )

    cases = [
        _case_row(
            case_id="default_mock_accepts_unsigned_release_index",
            description="default_mock accepts unsigned release_index and emits a deterministic warning",
            result="complete"
            if _token(default_unsigned.get("result")) in {"complete", "warn"}
            and "warn.trust.signature_missing" in _warning_codes(default_unsigned)
            else "refused",
            refusal_code=_token(default_unsigned.get("refusal_code")),
            remediation_hint=_token(default_unsigned.get("remediation_hint")),
            details={
                "trust_policy_id": DEFAULT_TRUST_POLICY_ID,
                "artifact_kind": ARTIFACT_KIND_RELEASE_INDEX,
                "warning_codes": _warning_codes(default_unsigned),
                "signature_status": _token(default_unsigned.get("signature_status")),
                "deterministic_fingerprint": _token(default_unsigned.get("deterministic_fingerprint")),
            },
        ),
        _case_row(
            case_id="strict_ranked_refuses_unsigned_release_index",
            description="strict_ranked refuses an unsigned release_index fixture",
            result="complete"
            if _token(strict_unsigned_release.get("result")) == "refused"
            and _token(strict_unsigned_release.get("refusal_code")) == REFUSAL_TRUST_SIGNATURE_MISSING
            else "refused",
            refusal_code=_token(strict_unsigned_release.get("refusal_code")),
            remediation_hint=_token(strict_unsigned_release.get("remediation_hint")),
            details={
                "trust_policy_id": TRUST_POLICY_STRICT,
                "artifact_kind": ARTIFACT_KIND_RELEASE_INDEX,
                "signature_status": _token(strict_unsigned_release.get("signature_status")),
                "deterministic_fingerprint": _token(strict_unsigned_release.get("deterministic_fingerprint")),
            },
        ),
        _case_row(
            case_id="strict_ranked_refuses_unsigned_official_pack",
            description="strict_ranked refuses an unsigned official pack artifact fixture",
            result="complete"
            if _token(strict_unsigned_pack.get("result")) == "refused"
            and _token(strict_unsigned_pack.get("refusal_code")) == REFUSAL_TRUST_SIGNATURE_MISSING
            else "refused",
            refusal_code=_token(strict_unsigned_pack.get("refusal_code")),
            remediation_hint=_token(strict_unsigned_pack.get("remediation_hint")),
            details={
                "trust_policy_id": TRUST_POLICY_STRICT,
                "artifact_kind": ARTIFACT_KIND_PACK,
                "fixture_path": UNSIGNED_OFFICIAL_PACK_REL,
                "signature_status": _token(strict_unsigned_pack.get("signature_status")),
                "deterministic_fingerprint": _token(strict_unsigned_pack.get("deterministic_fingerprint")),
            },
        ),
        _case_row(
            case_id="strict_ranked_accepts_signed_artifacts",
            description="strict_ranked accepts signed release-index and release-manifest fixtures from a trusted root",
            result="complete"
            if _token(strict_signed_release_index.get("result")) == "complete"
            and _token(strict_signed_release_manifest.get("result")) == "complete"
            else "refused",
            details={
                "release_index_result": _token(strict_signed_release_index.get("result")),
                "release_index_refusal_code": _token(strict_signed_release_index.get("refusal_code")),
                "release_index_verified_signer_ids": _sorted_tokens(strict_signed_release_index.get("trusted_signer_ids")),
                "release_manifest_result": _token(strict_signed_release_manifest.get("result")),
                "release_manifest_refusal_code": _token(strict_signed_release_manifest.get("refusal_code")),
                "release_manifest_verified_signer_ids": _sorted_tokens(strict_signed_release_manifest.get("trusted_signer_ids")),
            },
        ),
        _case_row(
            case_id="license_capability_requires_trusted_signature",
            description="license capability artifacts are accepted only when signed by a trusted official root",
            result="complete"
            if _token(signed_license_result.get("result")) == "complete"
            and _token(unsigned_license_result.get("refusal_code")) == REFUSAL_TRUST_SIGNATURE_MISSING
            and _token(untrusted_license_result.get("refusal_code")) == REFUSAL_TRUST_ROOT_NOT_TRUSTED
            else "refused",
            refusal_code=_token(unsigned_license_result.get("refusal_code")),
            remediation_hint=_token(unsigned_license_result.get("remediation_hint")),
            details={
                "signed_result": _token(signed_license_result.get("result")),
                "signed_refusal_code": _token(signed_license_result.get("refusal_code")),
                "unsigned_result": _token(unsigned_license_result.get("result")),
                "unsigned_refusal_code": _token(unsigned_license_result.get("refusal_code")),
                "untrusted_result": _token(untrusted_license_result.get("result")),
                "untrusted_refusal_code": _token(untrusted_license_result.get("refusal_code")),
                "trusted_signer_ids": _sorted_tokens(_as_map(signed_license_result.get("trust_result")).get("trusted_signer_ids")),
            },
        ),
        _case_row(
            case_id="license_capability_availability_display",
            description="accepted license capability fixtures only affect capability availability and degrade-display surfaces",
            result="complete"
            if _sorted_tokens(_as_map(signed_license_result.get("display")).get("available_capability_ids")) == EXPECTED_PREMIUM_AVAILABLE
            and _sorted_tokens(_as_map(signed_license_result.get("display")).get("degraded_capability_ids")) == EXPECTED_PREMIUM_DEGRADED
            else "refused",
            details={
                "requested_capability_ids": _sorted_tokens(REQUESTED_CAPABILITY_IDS),
                "available_capability_ids": _sorted_tokens(_as_map(signed_license_result.get("display")).get("available_capability_ids")),
                "degraded_capability_ids": _sorted_tokens(_as_map(signed_license_result.get("display")).get("degraded_capability_ids")),
                "enabled_capabilities": _sorted_tokens(signed_license_result.get("enabled_capabilities")),
                "display_fingerprint": _token(_as_map(signed_license_result.get("display")).get("deterministic_fingerprint")),
            },
        ),
    ]

    report = {
        "schema_id": TRUST_STRICT_RUN_SCHEMA_ID,
        "schema_version": "1.0.0",
        "trust_strict_version": TRUST_STRICT_VERSION,
        "stability_class": TRUST_STRICT_STABILITY_CLASS,
        "result": "complete" if all(_token(row.get("result")) == "complete" for row in cases) else "refused",
        "scenario_order": [_token(row.get("case_id")) for row in cases],
        "fixture_inputs": {
            fixture_id: _artifact_summary(root, fixture_id, _as_map(payload))
            for fixture_id, payload in sorted(fixture_payloads.items())
        },
        "trusted_fixture_roots": [_official_root()],
        "mod_policy_bindings": _mod_policy_bindings(),
        "policy_matrix": _policy_matrix(root, unsigned_release_index, official_roots),
        "cases": cases,
        "commercialization_hook": _commercialization_hook(),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = trust_strict_run_hash(report)
    if write_outputs:
        report["written"] = write_trust_strict_outputs(root, report)
    return report


def build_trust_strict_baseline(report: Mapping[str, object]) -> dict:
    payload = _as_map(report)
    baseline = {
        "schema_id": TRUST_STRICT_BASELINE_SCHEMA_ID,
        "schema_version": "1.0.0",
        "baseline_id": "trust_strict.baseline.v0_0_0",
        "required_update_tag": TRUST_STRICT_REQUIRED_TAG,
        "trust_strict_version": TRUST_STRICT_VERSION,
        "stability_class": TRUST_STRICT_STABILITY_CLASS,
        "result": _token(payload.get("result")),
        "scenario_order": list(_as_list(payload.get("scenario_order"))),
        "expected_mod_policy_bindings": dict(sorted(_as_map(payload.get("mod_policy_bindings")).items())),
        "policy_matrix": _normalize_tree(_as_map(payload.get("policy_matrix"))),
        "expected_cases": [
            {
                "case_id": _token(_as_map(row).get("case_id")),
                "result": _token(_as_map(row).get("result")),
                "refusal_code": _token(_as_map(row).get("refusal_code")),
                "details": _normalize_tree(_as_map(row).get("details")),
            }
            for row in _as_list(payload.get("cases"))
        ],
        "commercialization_hook": _normalize_tree(_as_map(payload.get("commercialization_hook"))),
        "source_run_fingerprint": _token(payload.get("deterministic_fingerprint")),
        "deterministic_fingerprint": "",
    }
    baseline["deterministic_fingerprint"] = trust_strict_baseline_hash(baseline)
    return baseline


def load_trust_strict_run(repo_root: str, path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return _load_json(_repo_abs(root, path or TRUST_STRICT_RUN_JSON_REL))


def load_trust_strict_baseline(repo_root: str, path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return _load_json(_repo_abs(root, path or TRUST_STRICT_BASELINE_REL))


def render_trust_strict_run(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Stability: stable",
        "Future Series: OMEGA",
        "Replacement Target: Frozen strict trust baseline and offline commercialization hook for v0.0.0-mock distribution gating.",
        "",
        "# Trust Strict Suite Run",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Scenario Results",
        "",
    ]
    for row in _as_list(payload.get("cases")):
        item = _as_map(row)
        lines.append(
            "- `{}`: result=`{}` refusal=`{}`".format(
                _token(item.get("case_id")),
                _token(item.get("result")),
                _token(item.get("refusal_code")) or "-",
            )
        )
    lines.extend(
        [
            "",
            "## Commercialization Hook",
            "",
            "- artifact kind: `{}`".format(_token(_as_map(payload.get("commercialization_hook")).get("artifact_kind_id"))),
            "- capability namespace: `{}`".format(_token(_as_map(payload.get("commercialization_hook")).get("capability_namespace"))),
            "- verification mode: `{}`".format(_token(_as_map(payload.get("commercialization_hook")).get("verification_mode"))),
            "- runtime effect scope: `{}`".format(_token(_as_map(payload.get("commercialization_hook")).get("runtime_effect_scope"))),
            "",
        ]
    )
    return "\n".join(lines)


def render_trust_strict_baseline(baseline: Mapping[str, object]) -> str:
    payload = _as_map(baseline)
    lines = [
        "Status: DERIVED",
        "Stability: stable",
        "Future Series: OMEGA",
        "Replacement Target: Frozen strict trust baseline and offline commercialization hook for v0.0.0-mock distribution gating.",
        "",
        "# Trust Strict Baseline",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Policy Summary",
        "",
        "- mod_policy.lab -> `{}`".format(_token(_as_map(payload.get("expected_mod_policy_bindings")).get("mod_policy.lab"))),
        "- mod_policy.strict -> `{}`".format(_token(_as_map(payload.get("expected_mod_policy_bindings")).get("mod_policy.strict"))),
        "- mod_policy.anarchy -> `{}`".format(_token(_as_map(payload.get("expected_mod_policy_bindings")).get("mod_policy.anarchy"))),
        "",
        "## Fixture Outcomes",
        "",
    ]
    for row in _as_list(payload.get("expected_cases")):
        item = _as_map(row)
        lines.append(
            "- `{}` -> result=`{}` refusal=`{}`".format(
                _token(item.get("case_id")),
                _token(item.get("result")),
                _token(item.get("refusal_code")) or "-",
            )
        )
    hook = _as_map(payload.get("commercialization_hook"))
    lines.extend(
        [
            "",
            "## Commercialization Hook",
            "",
            "- artifact kind: `{}`".format(_token(hook.get("artifact_kind_id"))),
            "- schema id: `{}`".format(_token(hook.get("schema_id"))),
            "- capability namespace: `{}`".format(_token(hook.get("capability_namespace"))),
            "- runtime effect scope: `{}`".format(_token(hook.get("runtime_effect_scope"))),
            "",
            "## Readiness",
            "",
            "- Ready for Ω-8 archive offline verification once RepoX, AuditX, TestX, and strict build remain green.",
            "",
        ]
    )
    return "\n".join(lines)


def write_trust_strict_outputs(repo_root: str, report: Mapping[str, object], *, json_path: str = "", doc_path: str = "") -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return {
        "json_path": _write_canonical_json(_repo_abs(root, json_path or TRUST_STRICT_RUN_JSON_REL), report),
        "doc_path": _write_text(_repo_abs(root, doc_path or TRUST_STRICT_RUN_DOC_REL), render_trust_strict_run(report)),
    }


def write_trust_strict_baseline_outputs(
    repo_root: str,
    baseline: Mapping[str, object],
    *,
    json_path: str = "",
    doc_path: str = "",
) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    return {
        "json_path": _write_canonical_json(_repo_abs(root, json_path or TRUST_STRICT_BASELINE_REL), baseline),
        "doc_path": _write_text(_repo_abs(root, doc_path or TRUST_STRICT_BASELINE_DOC_REL), render_trust_strict_baseline(baseline)),
    }


__all__ = [
    "LICENSE_CAPABILITY_SCHEMA_JSON_REL",
    "LICENSE_CAPABILITY_SCHEMA_REL",
    "OFFICIAL_SIGNER_ID",
    "PREMIUM_NAMESPACE_CAPABILITY",
    "SIGNED_LICENSE_CAPABILITY_REL",
    "SIGNED_RELEASE_INDEX_REL",
    "TRUST_FIXTURE_DIR_REL",
    "TRUST_STRICT_BASELINE_DOC_REL",
    "TRUST_STRICT_BASELINE_REL",
    "TRUST_STRICT_BASELINE_SCHEMA_ID",
    "TRUST_STRICT_MODEL_DOC_REL",
    "TRUST_STRICT_REQUIRED_TAG",
    "TRUST_STRICT_RETRO_AUDIT_REL",
    "TRUST_STRICT_RUN_DOC_REL",
    "TRUST_STRICT_RUN_JSON_REL",
    "TRUST_STRICT_RUN_SCHEMA_ID",
    "TRUST_STRICT_STABILITY_CLASS",
    "TRUST_STRICT_TOOL_PY_REL",
    "TRUST_STRICT_TOOL_REL",
    "TRUST_STRICT_VERSION",
    "UNSIGNED_OFFICIAL_PACK_REL",
    "UNSIGNED_RELEASE_INDEX_REL",
    "build_trust_fixture_payloads",
    "build_trust_strict_baseline",
    "load_trust_strict_baseline",
    "load_trust_strict_run",
    "render_trust_strict_baseline",
    "render_trust_strict_run",
    "run_trust_strict_suite",
    "trust_strict_baseline_hash",
    "trust_strict_run_hash",
    "write_trust_fixture_outputs",
    "write_trust_strict_baseline_outputs",
    "write_trust_strict_outputs",
]
