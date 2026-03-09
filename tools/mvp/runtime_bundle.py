"""Deterministic MVP runtime bundle helpers for Dominium v0.0.0."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256
from tools.xstack.sessionx.common import deterministic_seed_hex


MVP_RUNTIME_VERSION = "0.0.0"
MVP_PROFILE_BUNDLE_ID = "profile.bundle.mvp_default"
MVP_PACK_LOCK_ID = "pack_lock.mvp_default"
MVP_SESSION_TEMPLATE_ID = "session.mvp_default"
MVP_PROFILE_BUNDLE_REL = os.path.join("profiles", "bundles", "bundle.mvp_default.json")
MVP_PACK_LOCK_REL = os.path.join("locks", "pack_lock.mvp_default.json")
MVP_SESSION_TEMPLATE_REL = os.path.join("data", "session_templates", "session.mvp_default.json")
MVP_DIST_ROOT_REL = "dist"

MVP_SOURCE_PACKS = (
    {
        "pack_id": "pack.base.procedural",
        "version": MVP_RUNTIME_VERSION,
        "distribution_channel": "base",
        "distribution_rel": os.path.join("packs", "base", "pack.base.procedural"),
        "source_packs": (
            {
                "pack_id": "pack.core.runtime",
                "manifest_rel": os.path.join("packs", "core", "pack.core.runtime", "pack.json"),
            },
            {
                "pack_id": "astronomy.milky_way",
                "manifest_rel": os.path.join("packs", "domain", "astronomy.milky_way", "pack.json"),
            },
        ),
    },
    {
        "pack_id": "pack.sol.pin_minimal",
        "version": MVP_RUNTIME_VERSION,
        "distribution_channel": "official",
        "distribution_rel": os.path.join("packs", "official", "pack.sol.pin_minimal"),
        "source_packs": (
            {
                "pack_id": "astronomy.sol",
                "manifest_rel": os.path.join("packs", "domain", "astronomy.sol", "pack.json"),
            },
        ),
    },
    {
        "pack_id": "pack.earth.procedural",
        "version": MVP_RUNTIME_VERSION,
        "distribution_channel": "official",
        "distribution_rel": os.path.join("packs", "official", "pack.earth.procedural"),
        "source_packs": (
            {
                "pack_id": "planet.earth",
                "manifest_rel": os.path.join("packs", "domain", "planet.earth", "pack.json"),
            },
        ),
    },
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def load_json_object(path: str) -> dict:
    payload = json.loads(_read_text(path))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be object: {}".format(_norm(path)))
    return payload


def _write_canonical_json(path: str, payload: Dict[str, object]) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def _write_text(path: str, text: str) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace("\r\n", "\n"))


def _payload_hash(payload: Dict[str, object], field_name: str = "deterministic_fingerprint") -> str:
    body = dict(payload)
    body[field_name] = ""
    return canonical_sha256(body)


def _profile_bundle_hash(payload: Dict[str, object]) -> str:
    body = dict(payload)
    body["deterministic_fingerprint"] = ""
    body["profile_bundle_hash"] = ""
    return canonical_sha256(body)


def _source_pack_row(repo_root: str, rel_path: str) -> Dict[str, object]:
    manifest = load_json_object(os.path.join(repo_root, rel_path.replace("/", os.sep)))
    return {
        "pack_id": str(manifest.get("pack_id", "")).strip(),
        "version": str(manifest.get("version", "")).strip(),
        "canonical_hash": str(manifest.get("canonical_hash", "")).strip(),
        "signature_status": str(manifest.get("signature_status", "")).strip(),
        "manifest_path": _norm(rel_path),
    }


def _alias_pack_hash(pack_id: str, version: str, source_rows: List[Dict[str, object]]) -> str:
    return canonical_sha256(
        {
            "pack_id": str(pack_id),
            "version": str(version),
            "source_packs": [
                {
                    "pack_id": str(row.get("pack_id", "")),
                    "version": str(row.get("version", "")),
                    "canonical_hash": str(row.get("canonical_hash", "")),
                    "signature_status": str(row.get("signature_status", "")),
                }
                for row in source_rows
            ],
        }
    )


def _ordered_alias_pack_rows(repo_root: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for item in MVP_SOURCE_PACKS:
        source_rows = [
            _source_pack_row(repo_root=repo_root, rel_path=_norm(source["manifest_rel"]))
            for source in item["source_packs"]
        ]
        rows.append(
            {
                "pack_id": str(item["pack_id"]),
                "version": str(item["version"]),
                "distribution_channel": str(item["distribution_channel"]),
                "distribution_rel": _norm(item["distribution_rel"]),
                "canonical_hash": _alias_pack_hash(
                    pack_id=str(item["pack_id"]),
                    version=str(item["version"]),
                    source_rows=source_rows,
                ),
                "source_packs": source_rows,
            }
        )
    return rows


def build_profile_bundle_payload() -> Dict[str, object]:
    payload = {
        "schema_version": "1.0.0",
        "profile_bundle_id": MVP_PROFILE_BUNDLE_ID,
        "runtime_version": MVP_RUNTIME_VERSION,
        "generator_version_lock": "gen.v0_stub",
        "profiles": {
            "geo": {
                "topology": {"profile_id": "geo.topology.r3_infinite", "version": "1.0.0"},
                "metric": {"profile_id": "geo.metric.euclidean", "version": "1.0.0"},
                "partition": {"profile_id": "geo.partition.grid_zd", "version": "1.0.0"},
                "projections": [
                    {"profile_id": "geo.projection.perspective_3d", "version": "1.0.0"},
                    {"profile_id": "geo.projection.ortho_2d", "version": "1.0.0"},
                ],
            },
            "realism": {"profile_id": "realism.realistic_default_milkyway_stub", "version": "1.0.0"},
            "physics": {"profile_id": "physics.default_realistic", "version": "1.0.0"},
            "law": {
                "dev": {"profile_id": "law.lab_freecam", "version": "1.0.0"},
                "release": {"profile_id": "law.softcore_observer", "version": "1.0.0"},
            },
            "epistemic": {
                "dev": {"profile_id": "epistemic.admin_full", "version": "1.0.0"},
                "release": {"profile_id": "epistemic.diegetic_default", "version": "1.0.0"},
            },
            "compute": {"profile_id": "compute.default", "version": "1.0.0"},
            "coupling": {"profile_id": "coupling.default", "version": "1.0.0"},
            "overlay": {"profile_id": "overlay.default", "version": "1.0.0"},
            "logic": {"profile_id": "logic.default", "version": "1.0.0"},
        },
        "runtime_defaults": {
            "authority_default": "dev",
            "release_seed_policy": "explicit_required",
            "dev_seed_default": "0",
            "cli_default": {
                "profile_bundle": MVP_PROFILE_BUNDLE_ID,
                "pack_lock": MVP_PACK_LOCK_ID,
                "teleport": "",
                "ui": "cli",
            },
            "gui_default": {
                "profile_bundle": MVP_PROFILE_BUNDLE_ID,
                "pack_lock": MVP_PACK_LOCK_ID,
                "teleport": "",
                "ui": "gui",
                "camera_mode": "freecam",
            },
            "server_default": {
                "profile_bundle": MVP_PROFILE_BUNDLE_ID,
                "pack_lock": MVP_PACK_LOCK_ID,
                "teleport": "",
                "ui": "headless",
            },
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _profile_bundle_hash(payload)
    payload["profile_bundle_hash"] = payload["deterministic_fingerprint"]
    return payload


def validate_profile_bundle_payload(payload: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    if str(payload.get("profile_bundle_id", "")).strip() != MVP_PROFILE_BUNDLE_ID:
        errors.append("profile_bundle_id mismatch")
    expected = _profile_bundle_hash(payload)
    if str(payload.get("deterministic_fingerprint", "")).strip() != expected:
        errors.append("deterministic_fingerprint mismatch")
    if str(payload.get("profile_bundle_hash", "")).strip() != expected:
        errors.append("profile_bundle_hash mismatch")
    return errors


def _ordered_pack_hashes(pack_rows: List[Dict[str, object]]) -> List[str]:
    return [str(row.get("canonical_hash", "")).strip() for row in pack_rows]


def build_pack_lock_payload(repo_root: str, profile_bundle_payload: Dict[str, object] | None = None) -> Dict[str, object]:
    profile_bundle_payload = dict(profile_bundle_payload or build_profile_bundle_payload())
    pack_rows = _ordered_alias_pack_rows(repo_root=repo_root)
    profile_bundle_hash = str(profile_bundle_payload.get("profile_bundle_hash", "")).strip()
    payload = {
        "schema_version": "1.0.0",
        "pack_lock_id": MVP_PACK_LOCK_ID,
        "runtime_version": MVP_RUNTIME_VERSION,
        "profile_bundle_id": str(profile_bundle_payload.get("profile_bundle_id", "")),
        "profile_bundle_hash": profile_bundle_hash,
        "ordered_packs": pack_rows,
        "pack_lock_hash": canonical_sha256(
            {
                "ordered_pack_hashes": _ordered_pack_hashes(pack_rows),
                "profile_bundle_hash": profile_bundle_hash,
            }
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _payload_hash(payload)
    return payload


def validate_pack_lock_payload(repo_root: str, payload: Dict[str, object]) -> List[str]:
    expected = build_pack_lock_payload(repo_root=repo_root, profile_bundle_payload=build_profile_bundle_payload())
    errors: List[str] = []
    if str(payload.get("pack_lock_id", "")).strip() != MVP_PACK_LOCK_ID:
        errors.append("pack_lock_id mismatch")
    if list(payload.get("ordered_packs") or []) != list(expected.get("ordered_packs") or []):
        errors.append("ordered_packs mismatch")
    if str(payload.get("profile_bundle_hash", "")).strip() != str(expected.get("profile_bundle_hash", "")).strip():
        errors.append("profile_bundle_hash mismatch")
    if str(payload.get("pack_lock_hash", "")).strip() != str(expected.get("pack_lock_hash", "")).strip():
        errors.append("pack_lock_hash mismatch")
    if str(payload.get("deterministic_fingerprint", "")).strip() != _payload_hash(payload):
        errors.append("deterministic_fingerprint mismatch")
    return errors


def build_session_template_payload(repo_root: str, pack_lock_payload: Dict[str, object] | None = None) -> Dict[str, object]:
    pack_lock_payload = dict(pack_lock_payload or build_pack_lock_payload(repo_root=repo_root))
    payload = {
        "schema_version": "1.0.0",
        "template_id": MVP_SESSION_TEMPLATE_ID,
        "runtime_version": MVP_RUNTIME_VERSION,
        "universe_id": {
            "mode": "derived",
            "algorithm": "sha256(universe_seed|generator_version_id|profile_bundle_id|pack_lock_hash)",
            "format": "universe.<16hex>",
        },
        "universe_seed": {
            "dev_default": "0",
            "release_policy": "explicit_required",
        },
        "generator_version_id": "gen.v0_stub",
        "realism_profile_id": "realism.realistic_default_milkyway_stub",
        "profile_bundle_id": MVP_PROFILE_BUNDLE_ID,
        "profile_bundle_hash": str(pack_lock_payload.get("profile_bundle_hash", "")),
        "pack_lock_hash": str(pack_lock_payload.get("pack_lock_hash", "")),
        "authority_context": {
            "default": "dev",
            "modes": {
                "dev": {
                    "authority_origin": "tool",
                    "law_profile_id": "law.lab_freecam",
                    "epistemic_profile_id": "epistemic.admin_full",
                    "privilege_level": "operator",
                },
                "release": {
                    "authority_origin": "client",
                    "law_profile_id": "law.softcore_observer",
                    "epistemic_profile_id": "epistemic.diegetic_default",
                    "privilege_level": "observer",
                },
            },
        },
        "budget_policy_id": "policy.budget.default_lab",
        "fidelity_policy_id": "policy.fidelity.default_lab",
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _payload_hash(payload)
    return payload


def validate_session_template_payload(repo_root: str, payload: Dict[str, object]) -> List[str]:
    expected = build_session_template_payload(repo_root=repo_root)
    errors: List[str] = []
    if str(payload.get("template_id", "")).strip() != MVP_SESSION_TEMPLATE_ID:
        errors.append("template_id mismatch")
    for key in (
        "generator_version_id",
        "realism_profile_id",
        "profile_bundle_id",
        "profile_bundle_hash",
        "pack_lock_hash",
        "budget_policy_id",
        "fidelity_policy_id",
    ):
        if payload.get(key) != expected.get(key):
            errors.append("{} mismatch".format(key))
    if str(payload.get("deterministic_fingerprint", "")).strip() != _payload_hash(payload):
        errors.append("deterministic_fingerprint mismatch")
    return errors


def _dist_alias_payload(alias_row: Dict[str, object]) -> Dict[str, object]:
    payload = {
        "schema_version": "1.0.0",
        "pack_alias_id": str(alias_row.get("pack_id", "")),
        "runtime_version": MVP_RUNTIME_VERSION,
        "distribution_channel": str(alias_row.get("distribution_channel", "")),
        "canonical_hash": str(alias_row.get("canonical_hash", "")),
        "source_packs": list(alias_row.get("source_packs") or []),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = _payload_hash(payload)
    return payload


def _dist_python_stub(entrypoint: str, ui_mode: str) -> str:
    return """#!/usr/bin/env python3
import os
import subprocess
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
SCRIPT = os.path.join(REPO_ROOT, "tools", "mvp", "runtime_entry.py")

if not os.path.isfile(SCRIPT):
    print("dominium runtime bootstrap missing: {{}}".format(SCRIPT))
    raise SystemExit(2)

cmd = [sys.executable, SCRIPT, "{entrypoint}", "--ui", "{ui_mode}"] + sys.argv[1:]
raise SystemExit(subprocess.call(cmd))
""".format(entrypoint=entrypoint, ui_mode=ui_mode)


def _dist_cmd_stub(entrypoint: str, ui_mode: str) -> str:
    return (
        "@echo off\r\n"
        "python \"%~dp0\\..\\..\\tools\\mvp\\runtime_entry.py\" {entrypoint} --ui {ui_mode} %*\r\n"
    ).format(entrypoint=entrypoint, ui_mode=ui_mode)


def build_dist_layout(repo_root: str) -> Dict[str, object]:
    profile_bundle = build_profile_bundle_payload()
    pack_lock = build_pack_lock_payload(repo_root=repo_root, profile_bundle_payload=profile_bundle)
    out_root = os.path.join(repo_root, MVP_DIST_ROOT_REL)

    required_dirs = (
        "bin",
        os.path.join("packs", "base", "pack.base.procedural"),
        os.path.join("packs", "official", "pack.sol.pin_minimal"),
        os.path.join("packs", "official", "pack.earth.procedural"),
        "profiles",
        "locks",
        "saves",
        "logs",
    )
    for rel_dir in required_dirs:
        _ensure_dir(os.path.join(out_root, rel_dir.replace("/", os.sep)))

    alias_rows = list(pack_lock.get("ordered_packs") or [])
    alias_payloads = []
    for alias_row in alias_rows:
        rel_dir = str(alias_row.get("distribution_rel", "")).strip()
        alias_path = os.path.join(out_root, rel_dir.replace("/", os.sep), "pack.alias.json")
        _write_canonical_json(alias_path, _dist_alias_payload(alias_row))
        alias_payloads.append({"pack_id": str(alias_row.get("pack_id", "")), "path": _norm(os.path.relpath(alias_path, out_root))})

    _write_canonical_json(os.path.join(out_root, "profiles", "bundle.mvp_default.json"), profile_bundle)
    _write_canonical_json(os.path.join(out_root, "locks", "pack_lock.mvp_default.json"), pack_lock)
    _write_text(os.path.join(out_root, "saves", ".gitkeep"), "")
    _write_text(os.path.join(out_root, "logs", ".gitkeep"), "")
    _write_text(os.path.join(out_root, "bin", "dominium_client"), _dist_python_stub(entrypoint="client", ui_mode="gui"))
    _write_text(os.path.join(out_root, "bin", "dominium_client.cmd"), _dist_cmd_stub(entrypoint="client", ui_mode="gui"))
    _write_text(os.path.join(out_root, "bin", "dominium_server"), _dist_python_stub(entrypoint="server", ui_mode="headless"))
    _write_text(os.path.join(out_root, "bin", "dominium_server.cmd"), _dist_cmd_stub(entrypoint="server", ui_mode="headless"))

    return {
        "result": "complete",
        "dist_root": MVP_DIST_ROOT_REL,
        "profile_bundle_rel": _norm(os.path.join(MVP_DIST_ROOT_REL, "profiles", "bundle.mvp_default.json")),
        "pack_lock_rel": _norm(os.path.join(MVP_DIST_ROOT_REL, "locks", "pack_lock.mvp_default.json")),
        "alias_manifests": alias_payloads,
    }


def validate_dist_layout(repo_root: str) -> List[str]:
    out_root = os.path.join(repo_root, MVP_DIST_ROOT_REL)
    errors: List[str] = []
    for rel_dir in (
        "bin",
        os.path.join("packs", "base", "pack.base.procedural"),
        os.path.join("packs", "official", "pack.sol.pin_minimal"),
        os.path.join("packs", "official", "pack.earth.procedural"),
        "profiles",
        "locks",
        "saves",
        "logs",
    ):
        if not os.path.isdir(os.path.join(out_root, rel_dir.replace("/", os.sep))):
            errors.append("missing dist directory {}".format(_norm(os.path.join(MVP_DIST_ROOT_REL, rel_dir))))
    for rel_file in (
        os.path.join("bin", "dominium_client"),
        os.path.join("bin", "dominium_server"),
        os.path.join("profiles", "bundle.mvp_default.json"),
        os.path.join("locks", "pack_lock.mvp_default.json"),
    ):
        if not os.path.isfile(os.path.join(out_root, rel_file.replace("/", os.sep))):
            errors.append("missing dist file {}".format(_norm(os.path.join(MVP_DIST_ROOT_REL, rel_file))))
    for alias_row in _ordered_alias_pack_rows(repo_root=repo_root):
        alias_path = os.path.join(out_root, str(alias_row.get("distribution_rel", "")).replace("/", os.sep), "pack.alias.json")
        if not os.path.isfile(alias_path):
            errors.append("missing dist alias {}".format(_norm(os.path.relpath(alias_path, repo_root))))
    return errors


def derive_universe_id(universe_seed: str, generator_version_id: str, profile_bundle_id: str, pack_lock_hash: str) -> str:
    token = canonical_sha256(
        {
            "universe_seed": str(universe_seed),
            "generator_version_id": str(generator_version_id),
            "profile_bundle_id": str(profile_bundle_id),
            "pack_lock_hash": str(pack_lock_hash),
        }
    )
    return "universe.{}".format(token[:16])


def _named_rng_streams(universe_seed: str, generator_version_id: str) -> List[Dict[str, str]]:
    root = "{}|{}".format(str(universe_seed), str(generator_version_id))
    return [
        {"stream_name": name, "root_seed": deterministic_seed_hex(root, name)}
        for name in (
            "rng.universe.core",
            "rng.worldgen.milky_way",
            "rng.worldgen.sol",
            "rng.worldgen.earth",
            "rng.overlay.merge",
        )
    ]


def _resolve_seed(seed: str, authority_mode: str) -> Tuple[str, List[str]]:
    mode = str(authority_mode).strip().lower() or "dev"
    token = str(seed).strip()
    if token:
        return token, []
    if mode == "release":
        raise ValueError("release authority requires explicit --seed")
    return "0", ["seed omitted; defaulted to deterministic seed=0 for dev authority"]


def build_runtime_bootstrap(
    repo_root: str,
    entrypoint: str,
    ui: str,
    seed: str,
    profile_bundle_path: str,
    pack_lock_path: str,
    teleport: str,
    authority_mode: str,
) -> Dict[str, object]:
    bundle_payload = load_json_object(os.path.join(repo_root, profile_bundle_path.replace("/", os.sep)))
    lock_payload = load_json_object(os.path.join(repo_root, pack_lock_path.replace("/", os.sep)))
    bundle_errors = validate_profile_bundle_payload(bundle_payload)
    lock_errors = validate_pack_lock_payload(repo_root=repo_root, payload=lock_payload)
    if bundle_errors or lock_errors:
        raise ValueError("invalid MVP runtime artifacts: {} {}".format(bundle_errors, lock_errors))

    authority = str(authority_mode).strip().lower() or "dev"
    if authority not in ("dev", "release"):
        raise ValueError("authority must be dev or release")

    template_payload = build_session_template_payload(repo_root=repo_root, pack_lock_payload=lock_payload)
    template_errors = validate_session_template_payload(repo_root=repo_root, payload=template_payload)
    if template_errors:
        raise ValueError("invalid session template: {}".format(", ".join(template_errors)))

    universe_seed, warnings = _resolve_seed(seed=seed, authority_mode=authority)
    authority_payload = dict((((template_payload.get("authority_context") or {}).get("modes") or {}).get(authority) or {}))
    generator_version_id = str(template_payload.get("generator_version_id", "gen.v0_stub"))
    pack_lock_hash = str(template_payload.get("pack_lock_hash", "")).strip()
    profile_bundle_id = str(template_payload.get("profile_bundle_id", "")).strip()
    universe_id = derive_universe_id(
        universe_seed=universe_seed,
        generator_version_id=generator_version_id,
        profile_bundle_id=profile_bundle_id,
        pack_lock_hash=pack_lock_hash,
    )
    return {
        "result": "complete",
        "entrypoint": str(entrypoint),
        "ui_mode": str(ui),
        "camera_mode": "freecam" if str(ui) != "headless" else "none",
        "freecam_enabled": str(ui) != "headless",
        "teleport_target": str(teleport).strip(),
        "warnings": warnings,
        "profile_bundle": {
            "profile_bundle_id": profile_bundle_id,
            "profile_bundle_hash": str(bundle_payload.get("profile_bundle_hash", "")),
            "path": _norm(profile_bundle_path),
        },
        "pack_lock": {
            "pack_lock_id": str(lock_payload.get("pack_lock_id", "")),
            "pack_lock_hash": pack_lock_hash,
            "path": _norm(pack_lock_path),
        },
        "session_spec": {
            "template_id": MVP_SESSION_TEMPLATE_ID,
            "universe_id": universe_id,
            "universe_seed": universe_seed,
            "generator_version_id": generator_version_id,
            "realism_profile_id": str(template_payload.get("realism_profile_id", "")),
            "profile_bundle_id": profile_bundle_id,
            "pack_lock_hash": pack_lock_hash,
            "authority_context": authority_payload,
            "budget_policy_id": str(template_payload.get("budget_policy_id", "")),
            "fidelity_policy_id": str(template_payload.get("fidelity_policy_id", "")),
        },
        "rng_streams": _named_rng_streams(universe_seed=universe_seed, generator_version_id=generator_version_id),
    }


def write_runtime_artifacts(repo_root: str) -> Dict[str, object]:
    profile_bundle = build_profile_bundle_payload()
    pack_lock = build_pack_lock_payload(repo_root=repo_root, profile_bundle_payload=profile_bundle)
    session_template = build_session_template_payload(repo_root=repo_root, pack_lock_payload=pack_lock)

    _write_canonical_json(os.path.join(repo_root, MVP_PROFILE_BUNDLE_REL.replace("/", os.sep)), profile_bundle)
    _write_canonical_json(os.path.join(repo_root, MVP_PACK_LOCK_REL.replace("/", os.sep)), pack_lock)
    _write_canonical_json(os.path.join(repo_root, MVP_SESSION_TEMPLATE_REL.replace("/", os.sep)), session_template)
    dist_result = build_dist_layout(repo_root=repo_root)
    return {
        "result": "complete",
        "profile_bundle_rel": _norm(MVP_PROFILE_BUNDLE_REL),
        "pack_lock_rel": _norm(MVP_PACK_LOCK_REL),
        "session_template_rel": _norm(MVP_SESSION_TEMPLATE_REL),
        "dist": dist_result,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write deterministic MVP runtime bundle artifacts.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--write", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    repo_root = os.path.abspath(str(args.repo_root))
    payload = write_runtime_artifacts(repo_root=repo_root) if args.write else {
        "result": "complete",
        "profile_bundle": build_profile_bundle_payload(),
        "pack_lock": build_pack_lock_payload(repo_root=repo_root),
        "session_template": build_session_template_payload(repo_root=repo_root),
    }
    print(canonical_json_text(payload))
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
