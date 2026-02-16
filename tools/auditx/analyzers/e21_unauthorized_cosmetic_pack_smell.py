"""E21 Unauthorized cosmetic pack smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E21_UNAUTHORIZED_COSMETIC_PACK_SMELL"
COSMETIC_POLICY_REGISTRY = "data/registries/cosmetic_policy_registry.json"
SERVER_PROFILE_REGISTRY = "data/registries/server_profile_registry.json"
REPRESENTATION_PACK_MANIFEST = "packs/representation/pack.representation.base/pack.json"
FORBIDDEN_EXECUTABLE_EXTENSIONS = (
    ".py",
    ".pyw",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".ps1",
    ".bat",
    ".cmd",
    ".sh",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid_json"
    if not isinstance(payload, dict):
        return {}, "invalid_root"
    return payload, ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    policy_payload, policy_err = _read_json(repo_root, COSMETIC_POLICY_REGISTRY)
    if policy_err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="representation.unauthorized_cosmetic_pack_smell",
                severity="RISK",
                confidence=0.9,
                file_path=COSMETIC_POLICY_REGISTRY,
                line=1,
                evidence=["unable to parse cosmetic policy registry"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                related_paths=[COSMETIC_POLICY_REGISTRY],
            )
        )
    else:
        rows = (((policy_payload.get("record") or {}).get("policies")) or [])
        policy_map = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            policy_id = str(row.get("policy_id", "")).strip()
            if policy_id:
                policy_map[policy_id] = row

        ranked = dict(policy_map.get("policy.cosmetics.rank_strict") or {})
        if not ranked:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="representation.unauthorized_cosmetic_pack_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=COSMETIC_POLICY_REGISTRY,
                    line=1,
                    evidence=["missing required ranked cosmetic policy policy.cosmetics.rank_strict"],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                    related_paths=[COSMETIC_POLICY_REGISTRY],
                )
            )
        else:
            require_signed = bool(ranked.get("require_signed_packs", False))
            allow_unsigned = bool(ranked.get("allow_unsigned_packs", True))
            allowed_pack_ids = sorted(
                set(str(item).strip() for item in (ranked.get("allowed_pack_ids") or []) if str(item).strip())
            )
            if not require_signed or allow_unsigned:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="representation.unauthorized_cosmetic_pack_smell",
                        severity="RISK",
                        confidence=0.86,
                        file_path=COSMETIC_POLICY_REGISTRY,
                        line=1,
                        evidence=[
                            "ranked cosmetic policy must require signed packs and disallow unsigned packs",
                            "require_signed_packs={}, allow_unsigned_packs={}".format(require_signed, allow_unsigned),
                        ],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                        related_paths=[COSMETIC_POLICY_REGISTRY],
                    )
                )
            if "pack.representation.base" not in allowed_pack_ids:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="representation.unauthorized_cosmetic_pack_smell",
                        severity="WARN",
                        confidence=0.75,
                        file_path=COSMETIC_POLICY_REGISTRY,
                        line=1,
                        evidence=["ranked cosmetic policy allow-list does not include pack.representation.base"],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="DOC_FIX",
                        related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                        related_paths=[COSMETIC_POLICY_REGISTRY],
                    )
                )

    profile_payload, profile_err = _read_json(repo_root, SERVER_PROFILE_REGISTRY)
    if profile_err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="representation.unauthorized_cosmetic_pack_smell",
                severity="WARN",
                confidence=0.7,
                file_path=SERVER_PROFILE_REGISTRY,
                line=1,
                evidence=["unable to parse server profile registry for cosmetic policy linkage"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                related_paths=[SERVER_PROFILE_REGISTRY],
            )
        )
    else:
        rows = (((profile_payload.get("record") or {}).get("profiles")) or [])
        ranked_profile = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            if str(row.get("server_profile_id", "")).strip() == "server.profile.rank_strict":
                ranked_profile = dict(row)
                break
        if ranked_profile:
            ext = dict(ranked_profile.get("extensions") or {})
            cosmetic_policy_id = str(ext.get("cosmetic_policy_id", "")).strip()
            if cosmetic_policy_id != "policy.cosmetics.rank_strict":
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="representation.unauthorized_cosmetic_pack_smell",
                        severity="RISK",
                        confidence=0.84,
                        file_path=SERVER_PROFILE_REGISTRY,
                        line=1,
                        evidence=[
                            "ranked server profile cosmetic policy mismatch",
                            "extensions.cosmetic_policy_id={}".format(cosmetic_policy_id or "<missing>"),
                        ],
                        suggested_classification="INVALID",
                        recommended_action="ADD_RULE",
                        related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                        related_paths=[SERVER_PROFILE_REGISTRY],
                    )
                )

    manifest_payload, manifest_err = _read_json(repo_root, REPRESENTATION_PACK_MANIFEST)
    if manifest_err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="representation.unauthorized_cosmetic_pack_smell",
                severity="WARN",
                confidence=0.7,
                file_path=REPRESENTATION_PACK_MANIFEST,
                line=1,
                evidence=["representation base pack manifest missing or invalid"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                related_paths=[REPRESENTATION_PACK_MANIFEST],
            )
        )
    else:
        signature_status = str(manifest_payload.get("signature_status", "")).strip().lower()
        if signature_status not in ("signed", "verified", "official"):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="representation.unauthorized_cosmetic_pack_smell",
                    severity="WARN",
                    confidence=0.78,
                    file_path=REPRESENTATION_PACK_MANIFEST,
                    line=1,
                    evidence=[
                        "representation base pack signature_status is not signed/verified/official",
                        "signature_status={}".format(signature_status or "<missing>"),
                    ],
                    suggested_classification="PROTOTYPE",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                    related_paths=[REPRESENTATION_PACK_MANIFEST],
                )
            )

    representation_root = os.path.join(repo_root, "packs", "representation")
    if os.path.isdir(representation_root):
        for walk_root, dirs, files in os.walk(representation_root):
            dirs[:] = sorted(dirs)
            for name in sorted(files):
                lower_name = str(name).lower()
                if not lower_name.endswith(FORBIDDEN_EXECUTABLE_EXTENSIONS):
                    continue
                rel_path = _norm(os.path.relpath(os.path.join(walk_root, name), repo_root))
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="representation.unauthorized_cosmetic_pack_smell",
                        severity="RISK",
                        confidence=0.92,
                        file_path=rel_path,
                        line=1,
                        evidence=["representation pack contains executable/script file '{}'".format(name)],
                        suggested_classification="INVALID",
                        recommended_action="QUARANTINE",
                        related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                        related_paths=[rel_path],
                    )
                )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
