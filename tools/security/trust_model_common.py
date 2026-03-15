"""Deterministic TRUST-MODEL-0 helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping, Sequence

from src.security.trust import (
    ARTIFACT_KIND_PACK,
    ARTIFACT_KIND_RELEASE_INDEX,
    ARTIFACT_KIND_RELEASE_MANIFEST,
    DEFAULT_TRUST_POLICY_ID,
    REFUSAL_TRUST_HASH_MISSING,
    REFUSAL_TRUST_SIGNATURE_INVALID,
    REFUSAL_TRUST_SIGNATURE_MISSING,
    TRUST_POLICY_ANARCHY,
    TRUST_POLICY_STRICT,
    canonicalize_signature_record,
    deterministic_fingerprint,
    load_trust_policy_registry,
    load_trust_root_registry,
    select_trust_policy,
    verify_artifact_trust,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "TRUST_MODEL0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "security", "TRUST_AND_SIGNING_MODEL.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "TRUST_MODEL_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "trust_model_report.json")
TRUST_POLICY_REGISTRY_REL = os.path.join("data", "registries", "trust_policy_registry.json")
TRUST_ROOT_REGISTRY_REL = os.path.join("data", "registries", "trust_root_registry.json")
SERVER_CONFIG_REGISTRY_REL = os.path.join("data", "registries", "server_config_registry.json")
RULE_HASHES = "INV-HASHES-MANDATORY-FOR-ARTIFACTS"
RULE_POLICY = "INV-TRUST-POLICY-DECLARED"
RULE_STRICT = "INV-STRICT-REQUIRES-SIGNATURES"
LAST_REVIEWED = "2026-03-14"
_DEFAULT_SCHEME_ID = "signature.mock_detached_hash.v1"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _file_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(_norm(repo_root), rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _mock_signature_bytes(*, signature_id: str, signer_id: str, signed_hash: str) -> str:
    return canonical_sha256(
        {
            "scheme_id": _DEFAULT_SCHEME_ID,
            "signature_id": _token(signature_id),
            "signer_id": _token(signer_id),
            "signed_hash": _token(signed_hash).lower(),
        }
    )


def _signature_row(*, signer_id: str, signed_hash: str, valid: bool) -> dict:
    signature_id = "signature.{}.{}".format(_token(signer_id).replace(" ", "_") or "anonymous", _token(signed_hash).lower()[:16] or "unsigned")
    row = canonicalize_signature_record(
        {
            "signature_id": signature_id,
            "signer_id": _token(signer_id),
            "signed_hash": _token(signed_hash).lower(),
            "signature_bytes": _mock_signature_bytes(signature_id=signature_id, signer_id=signer_id, signed_hash=signed_hash) if valid else "invalid-signature-bytes",
            "extensions": {"scheme_id": _DEFAULT_SCHEME_ID},
        }
    )
    return row


def _trusted_root_row(signer_id: str, trust_level_id: str = "official") -> dict:
    payload = {
        "signer_id": _token(signer_id),
        "public_key_bytes": "mock-public-key:{}".format(_token(signer_id)),
        "trust_level_id": "official" if _token(trust_level_id) == "official" else "thirdparty",
        "deterministic_fingerprint": "",
        "extensions": {"official.source": "TRUST-MODEL0-6"},
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def _violation(rule_id: str, code: str, message: str, *, file_path: str) -> dict:
    return {
        "rule_id": _token(rule_id),
        "code": _token(code),
        "message": _token(message),
        "file_path": _norm_rel(file_path),
    }


def _integration_checks(repo_root: str) -> list[dict]:
    checks = []
    for rel_path, token, rule_id, code, message in (
        ("tools/setup/setup_cli.py", "handle_trust(", RULE_POLICY, "setup_trust_cli_missing", "setup CLI must expose trust commands"),
        ("tools/setup/setup_cli.py", "trust_policy_id", RULE_POLICY, "setup_trust_policy_missing", "setup verification and update flows must accept trust_policy_id"),
        ("src/release/update_resolver.py", "verify_artifact_trust(", RULE_STRICT, "update_resolver_trust_missing", "update resolver must verify release index trust"),
        ("src/appshell/pack_verifier_adapter.py", "verify_artifact_trust(", RULE_HASHES, "pack_pipeline_trust_missing", "pack verification pipeline must route through trust verification"),
        ("tools/dist/dist_verify_common.py", "verify_release_manifest(", RULE_HASHES, "dist_verify_trust_missing", "dist verification must route through release manifest verification"),
    ):
        if token in _file_text(repo_root, rel_path):
            continue
        checks.append(_violation(rule_id, code, message, file_path=rel_path))
    return checks


def build_trust_model_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    policy_registry = load_trust_policy_registry(repo_root=root)
    root_registry = load_trust_root_registry(repo_root=root)
    server_registry = _read_json(os.path.join(root, SERVER_CONFIG_REGISTRY_REL))

    policy_rows = list(_as_map(policy_registry.get("record")).get("trust_policies") or [])
    policy_ids = sorted(_token(_as_map(row).get("trust_policy_id")) for row in policy_rows if _token(_as_map(row).get("trust_policy_id")))
    strict_policy = select_trust_policy(policy_registry, trust_policy_id=TRUST_POLICY_STRICT)
    default_policy = select_trust_policy(policy_registry, trust_policy_id=DEFAULT_TRUST_POLICY_ID)
    anarchy_policy = select_trust_policy(policy_registry, trust_policy_id=TRUST_POLICY_ANARCHY)

    fixture_hash = canonical_sha256({"artifact": "trust-model-fixture"})
    signer_id = "signer.fixture.official"
    trusted_roots = [_trusted_root_row(signer_id)]

    cases = {
        "hash_missing": verify_artifact_trust(
            artifact_kind=ARTIFACT_KIND_RELEASE_MANIFEST,
            content_hash="",
            trust_policy=default_policy,
            trust_policy_id=DEFAULT_TRUST_POLICY_ID,
        ),
        "strict_unsigned": verify_artifact_trust(
            artifact_kind=ARTIFACT_KIND_RELEASE_INDEX,
            content_hash=fixture_hash,
            trust_policy=strict_policy,
            trust_policy_id=TRUST_POLICY_STRICT,
            trust_roots=trusted_roots,
        ),
        "default_unsigned": verify_artifact_trust(
            artifact_kind=ARTIFACT_KIND_PACK,
            content_hash=fixture_hash,
            trust_policy=default_policy,
            trust_policy_id=DEFAULT_TRUST_POLICY_ID,
            trust_roots=trusted_roots,
        ),
        "invalid_signature": verify_artifact_trust(
            artifact_kind=ARTIFACT_KIND_RELEASE_MANIFEST,
            content_hash=fixture_hash,
            signatures=[_signature_row(signer_id=signer_id, signed_hash=fixture_hash, valid=False)],
            trust_policy=strict_policy,
            trust_policy_id=TRUST_POLICY_STRICT,
            trust_roots=trusted_roots,
        ),
        "strict_signed": verify_artifact_trust(
            artifact_kind=ARTIFACT_KIND_RELEASE_MANIFEST,
            content_hash=fixture_hash,
            signatures=[_signature_row(signer_id=signer_id, signed_hash=fixture_hash, valid=True)],
            trust_policy=strict_policy,
            trust_policy_id=TRUST_POLICY_STRICT,
            trust_roots=trusted_roots,
        ),
        "anarchy_unsigned": verify_artifact_trust(
            artifact_kind=ARTIFACT_KIND_PACK,
            content_hash=fixture_hash,
            trust_policy=anarchy_policy,
            trust_policy_id=TRUST_POLICY_ANARCHY,
        ),
    }

    violations: list[dict] = []
    required_policy_ids = [TRUST_POLICY_ANARCHY, DEFAULT_TRUST_POLICY_ID, TRUST_POLICY_STRICT]
    for policy_id in required_policy_ids:
        if policy_id in policy_ids:
            continue
        violations.append(
            _violation(RULE_POLICY, "required_policy_missing", "trust policy '{}' must be declared".format(policy_id), file_path=TRUST_POLICY_REGISTRY_REL)
        )
    registry_text = _file_text(root, TRUST_POLICY_REGISTRY_REL)
    if "PLACEHOLDER" in registry_text:
        violations.append(
            _violation(RULE_POLICY, "placeholder_fingerprint", "trust policy registry must not contain placeholder fingerprints", file_path=TRUST_POLICY_REGISTRY_REL)
        )

    if _token(cases["hash_missing"].get("refusal_code")) != REFUSAL_TRUST_HASH_MISSING:
        violations.append(
            _violation(RULE_HASHES, "hash_missing_not_refused", "artifacts must never be accepted without a canonical content hash", file_path="src/security/trust/trust_verifier.py")
        )
    if _token(cases["strict_unsigned"].get("refusal_code")) != REFUSAL_TRUST_SIGNATURE_MISSING:
        violations.append(
            _violation(RULE_STRICT, "strict_unsigned_not_refused", "strict trust policy must refuse unsigned governed artifacts", file_path="src/security/trust/trust_verifier.py")
        )
    default_warnings = { _token(_as_map(row).get("code")) for row in _as_list(cases["default_unsigned"].get("warnings")) }
    if _token(cases["default_unsigned"].get("result")) not in {"complete", "warn"} or "warn.trust.signature_missing" not in default_warnings:
        violations.append(
            _violation(RULE_POLICY, "default_unsigned_not_warning", "default mock trust policy must warn but not refuse unsigned artifacts", file_path="src/security/trust/trust_verifier.py")
        )
    if _token(cases["invalid_signature"].get("refusal_code")) != REFUSAL_TRUST_SIGNATURE_INVALID:
        violations.append(
            _violation(RULE_STRICT, "invalid_signature_not_refused", "invalid signatures must be refused deterministically", file_path="src/security/trust/trust_verifier.py")
        )
    if _token(cases["strict_signed"].get("result")) != "complete":
        violations.append(
            _violation(RULE_STRICT, "strict_signed_not_accepted", "strict trust policy must accept valid signatures from trusted roots", file_path="src/security/trust/trust_verifier.py")
        )

    server_rows = list(_as_map(server_registry.get("record")).get("server_configs") or [])
    server_default_policy_id = ""
    if server_rows:
        server_default_policy_id = _token(_as_map(_as_map(server_rows[0]).get("extensions")).get("official.trust_policy_id"))
    if not server_default_policy_id:
        violations.append(
            _violation(RULE_POLICY, "server_trust_policy_missing", "server config must declare a trust policy id", file_path=SERVER_CONFIG_REGISTRY_REL)
        )

    violations.extend(_integration_checks(root))

    report = {
        "report_id": "security.trust_model.v1",
        "result": "complete" if not violations else "refused",
        "policy_ids": policy_ids,
        "root_count": int(len(_as_list(_as_map(root_registry.get("record")).get("trust_roots")))),
        "server_default_trust_policy_id": server_default_policy_id,
        "cases": {
            key: {
                "result": _token(_as_map(value).get("result")),
                "refusal_code": _token(_as_map(value).get("refusal_code")),
                "reason": _token(_as_map(value).get("reason")),
                "warnings": [
                    {
                        "code": _token(_as_map(row).get("code")),
                        "message": _token(_as_map(row).get("message")),
                    }
                    for row in _as_list(_as_map(value).get("warnings"))
                ],
            }
            for key, value in sorted(cases.items())
        },
        "violations": violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_trust_model_baseline(report: Mapping[str, object]) -> str:
    rows = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: TRUST/UPDATE-MODEL",
        "Replacement Target: release-index governed trust-root bundles and signed acquisition policy",
        "",
        "# Trust Model Baseline",
        "",
        "## Policies",
        "",
        "- Declared policies: {}".format(", ".join(_as_list(rows.get("policy_ids"))) or "(none)"),
        "- Server default trust policy: `{}`".format(_token(rows.get("server_default_trust_policy_id")) or "(missing)"),
        "- Mock-channel default behavior: hashes mandatory, signatures optional with warnings.",
        "- Strict ranked behavior: signatures required for governed release and pack artifacts.",
        "- Anarchy behavior: unsigned artifacts allowed, but hashes remain mandatory.",
        "",
        "## Default Behavior For Mock Channel",
        "",
        "- Missing hash: refused with `{}`.".format(REFUSAL_TRUST_HASH_MISSING),
        "- Unsigned governed artifact under default policy: complete with `warn.trust.signature_missing`.",
        "- Unsigned governed artifact under strict policy: refused with `{}`.".format(REFUSAL_TRUST_SIGNATURE_MISSING),
        "- Invalid signature: refused with `{}`.".format(REFUSAL_TRUST_SIGNATURE_INVALID),
        "",
        "## Integration Points",
        "",
        "- `setup verify` and pack verification route through `src/security/trust/trust_verifier.py`.",
        "- `setup update` passes the resolved trust policy into `src/release/update_resolver.py`.",
        "- `tool_verify_release_manifest` and DIST-2 verification use trust-aware manifest verification.",
        "- Server policy binding is declared in `data/registries/server_config_registry.json`.",
        "",
        "## Canonical Verification Cases",
        "",
    ]
    for case_id, row in sorted(_as_map(rows.get("cases")).items()):
        item = _as_map(row)
        lines.append(
            "- `{}`: result=`{}` refusal=`{}`".format(
                case_id,
                _token(item.get("result")) or "unknown",
                _token(item.get("refusal_code")) or "-",
            )
        )
    if _as_list(rows.get("violations")):
        lines.extend(["", "## Open Violations", ""])
        for row in _as_list(rows.get("violations")):
            item = _as_map(row)
            lines.append("- `{}`: {}".format(_token(item.get("code")), _token(item.get("message"))))
    return "\n".join(lines) + "\n"


def write_trust_model_outputs(repo_root: str, report: Mapping[str, object] | None = None) -> dict:
    root = _norm(repo_root)
    payload = dict(report or build_trust_model_report(root))
    baseline_doc_path = _write_text(os.path.join(root, BASELINE_DOC_REL), render_trust_model_baseline(payload))
    report_json_path = _write_json(os.path.join(root, REPORT_JSON_REL), payload)
    return {
        "report": payload,
        "baseline_doc_path": _norm_rel(os.path.relpath(baseline_doc_path, root)),
        "report_json_path": _norm_rel(os.path.relpath(report_json_path, root)),
    }


def trust_model_violations(repo_root: str) -> list[dict]:
    return list(build_trust_model_report(repo_root).get("violations") or [])


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "LAST_REVIEWED",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_HASHES",
    "RULE_POLICY",
    "RULE_STRICT",
    "build_trust_model_report",
    "render_trust_model_baseline",
    "trust_model_violations",
    "write_trust_model_outputs",
]
