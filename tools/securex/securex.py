#!/usr/bin/env python3
"""SecureX trust and integrity enforcement CLI."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(THIS_DIR, "core")
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

DEV_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "scripts", "dev"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from boundary_validator import validate_boundaries
from env_tools_lib import canonical_workspace_id, canonicalize_env_for_workspace, detect_repo_root
from integrity_manifest import generate_manifest, write_manifest
from pack_signature import sign_pack, verify_pack_signature, verify_signature_payload, write_signature
from privilege_enforcer import scan_for_hardcoded_modes, validate_security_roles
from reproducible_build_check import canonical_hash_map, compare_hash_maps
from trust_model import load_and_validate as load_trust_policy


TRUST_POLICY_REL = os.path.join("data", "registries", "trust_policy.json")
SECURITY_ROLES_REL = os.path.join("data", "registries", "security_roles.json")
OUTPUT_DIR_REL = os.path.join("docs", "audit", "security")
FINDINGS_REL = "FINDINGS.json"
RUN_META_REL = "RUN_META.json"
INTEGRITY_REL = "INTEGRITY_MANIFEST.json"


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return detect_repo_root(os.getcwd(), __file__)


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _read_json(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key in sorted(value.keys()):
            out[str(key)] = _canonicalize(value[key])
        return out
    if isinstance(value, list):
        normalized = [_canonicalize(item) for item in value]
        if all(isinstance(item, dict) for item in normalized):
            return sorted(
                normalized,
                key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":")),
            )
        if all(isinstance(item, str) for item in normalized):
            return sorted(set(normalized))
        return normalized
    return value


def _iter_source_files(repo_root: str) -> Iterable[str]:
    roots = [os.path.join(repo_root, part) for part in ("engine", "game", "client", "server", "launcher", "setup", "tools")]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in {".git", ".vs", "__pycache__", "out", "dist"}]
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() not in {".c", ".cc", ".cpp", ".h", ".hpp", ".py", ".json", ".md"}:
                    continue
                yield os.path.join(dirpath, filename)


def _security_findings(repo_root: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    secret_re = re.compile(r"(AKIA[0-9A-Z]{16}|BEGIN[ ]+PRIVATE[ ]+KEY|password\\s*=\\s*['\\\"])")
    bypass_tokens = (
        "bypass_law_profile",
        "disable_epistemic_guard",
        "override_authority_state",
    )
    direct_io_tokens = ("open(", "fopen(", "std::fstream", "ifstream(")

    for path in sorted(_iter_source_files(repo_root)):
        rel = os.path.relpath(path, repo_root).replace("\\", "/")
        text = ""
        try:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            continue
        lowered = text.lower()

        if secret_re.search(text):
            findings.append(
                {
                    "category": "hardcoded_secret",
                    "severity": "RISK",
                    "confidence": 0.8,
                    "path": rel,
                    "evidence": "secret-like token detected",
                }
            )
        for token in bypass_tokens:
            if token in lowered:
                findings.append(
                    {
                        "category": "privilege_bypass",
                        "severity": "VIOLATION",
                        "confidence": 0.9,
                        "path": rel,
                        "evidence": token,
                    }
                )
        if rel.startswith(("client/", "renderer/")) and any(token in lowered for token in direct_io_tokens):
            findings.append(
                {
                    "category": "boundary_io",
                    "severity": "WARN",
                    "confidence": 0.6,
                    "path": rel,
                    "evidence": "direct file I/O token in client/render path",
                }
            )

    findings.sort(key=lambda row: (row.get("category", ""), row.get("path", ""), row.get("evidence", "")))
    output: List[Dict[str, Any]] = []
    for idx, row in enumerate(findings, start=1):
        item = dict(row)
        item["finding_id"] = "SECUREX:{:04d}".format(idx)
        output.append(item)
    return output


def _manifest_inputs(repo_root: str) -> Tuple[List[tuple[str, str]], List[tuple[str, str]], List[tuple[str, str]], List[tuple[str, str]]]:
    schema_files = [
        ("schema.trust_policy", os.path.join(repo_root, "schema", "governance", "trust_policy.schema")),
        ("schema.pack_signature", os.path.join(repo_root, "schema", "governance", "pack_signature.schema")),
        ("schema.integrity_manifest", os.path.join(repo_root, "schema", "governance", "integrity_manifest.schema")),
        ("schema.privilege_model", os.path.join(repo_root, "schema", "governance", "privilege_model.schema")),
    ]
    pack_files = [
        ("registry.trust_policy", os.path.join(repo_root, TRUST_POLICY_REL)),
        ("registry.security_roles", os.path.join(repo_root, SECURITY_ROLES_REL)),
    ]
    tool_files = [
        ("tool.securex", os.path.join(repo_root, "tools", "securex", "securex.py")),
        ("tool.auditx", os.path.join(repo_root, "tools", "auditx", "auditx.py")),
        ("tool.compatx", os.path.join(repo_root, "tools", "compatx", "compatx.py")),
        ("tool.controlx", os.path.join(repo_root, "tools", "controlx", "controlx.py")),
    ]
    canonical_artifacts = [
        ("artifact.identity_fingerprint", os.path.join(repo_root, "docs", "audit", "identity_fingerprint.json")),
        ("artifact.auditx.findings", os.path.join(repo_root, "docs", "audit", "auditx", "FINDINGS.json")),
        ("artifact.compatx.baseline", os.path.join(repo_root, "docs", "audit", "compat", "COMPAT_BASELINE.json")),
    ]
    return schema_files, pack_files, tool_files, canonical_artifacts


def _run_verify(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    ws_id = canonical_workspace_id(repo_root, env=os.environ)
    _env, ws_dirs = canonicalize_env_for_workspace(dict(os.environ), repo_root, ws_id=ws_id)
    start = time.time()

    trust_entries, trust_errors = load_trust_policy(os.path.join(repo_root, TRUST_POLICY_REL))
    role_entries, role_errors = validate_security_roles(os.path.join(repo_root, SECURITY_ROLES_REL))
    boundary_errors = validate_boundaries(repo_root, trust_entries)
    mode_errors = scan_for_hardcoded_modes(repo_root)

    findings = _security_findings(repo_root)
    output_dir = os.path.join(repo_root, OUTPUT_DIR_REL)
    findings_path = os.path.join(output_dir, FINDINGS_REL)
    run_meta_path = os.path.join(output_dir, RUN_META_REL)
    integrity_path = os.path.join(output_dir, INTEGRITY_REL)

    finding_payload = _canonicalize(
        {
            "artifact_class": "CANONICAL",
            "schema_id": "dominium.schema.governance.securex_findings",  # schema_version: 1.0.0
            "schema_version": "1.0.0",
            "record": {
                "finding_set_id": "securex.findings",
                "findings": findings,
                "summary": {
                    "total": len(findings),
                    "by_category": _canonicalize(
                        {
                            key: len([row for row in findings if row.get("category") == key])
                            for key in sorted({str(row.get("category", "")) for row in findings})
                        }
                    ),
                },
                "extensions": {},
            },
        }
    )
    _write_json(findings_path, finding_payload)

    schema_files, pack_files, tool_files, canonical_artifacts = _manifest_inputs(repo_root)
    integrity_payload = _canonicalize(
        generate_manifest(
            repo_root=repo_root,
            schema_files=schema_files,
            pack_files=pack_files,
            tool_files=tool_files,
            canonical_artifacts=canonical_artifacts,
            identity_path=os.path.join(repo_root, "docs", "audit", "identity_fingerprint.json"),
        )
    )
    write_manifest(integrity_path, integrity_payload)

    run_meta = {
        "artifact_class": "RUN_META",
        "generated_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workspace_id": str(ws_dirs.get("workspace_id", "")),
        "duration_ms": int((time.time() - start) * 1000.0),
        "trust_entry_count": len(trust_entries),
        "role_entry_count": len(role_entries),
        "finding_count": len(findings),
    }
    _write_json(run_meta_path, run_meta)

    refusal_codes = sorted(set(trust_errors + role_errors + boundary_errors + mode_errors))
    if refusal_codes:
        print(
            json.dumps(
                {
                    "result": "refused",
                    "refusal_codes": refusal_codes,
                    "outputs": {
                        "findings": FINDINGS_REL,
                        "integrity_manifest": INTEGRITY_REL,
                        "run_meta": RUN_META_REL,
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    print(
        json.dumps(
            {
                "result": "complete",
                "workspace_id": str(ws_dirs.get("workspace_id", "")),
                "outputs": {
                    "findings": FINDINGS_REL,
                    "integrity_manifest": INTEGRITY_REL,
                    "run_meta": RUN_META_REL,
                },
                "finding_count": len(findings),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _cmd_sign_pack(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    pack_path = os.path.normpath(os.path.abspath(args.pack_path))
    if not os.path.isfile(pack_path):
        print(json.dumps({"result": "refused", "refusal_code": "refuse.pack_missing"}, indent=2, sort_keys=True))
        return 2
    payload = sign_pack(
        pack_path=pack_path,
        signer_id=args.signer_id,
        key_id=args.key_id,
        key_material=args.key_material,
        issued_utc=args.issued_utc,
    )
    output_path = os.path.normpath(os.path.abspath(args.output))
    write_signature(output_path, _canonicalize(payload))
    print(
        json.dumps(
            {
                "result": "complete",
                "output": os.path.relpath(output_path, repo_root).replace("\\", "/"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _cmd_verify_pack(args: argparse.Namespace) -> int:
    pack_path = os.path.normpath(os.path.abspath(args.pack_path))
    signature = _read_json(os.path.normpath(os.path.abspath(args.signature_json)))
    if signature is None:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.signature_missing"}, indent=2, sort_keys=True))
        return 2
    ok, refusal = verify_pack_signature(pack_path, signature, key_material=args.key_material)
    if not ok:
        print(json.dumps({"result": "refused", "refusal_code": refusal}, indent=2, sort_keys=True))
        return 2
    print(json.dumps({"result": "complete"}, indent=2, sort_keys=True))
    return 0


def _collect_paths(path: str) -> List[str]:
    norm = os.path.normpath(os.path.abspath(path))
    if os.path.isfile(norm):
        return [norm]
    out: List[str] = []
    if not os.path.isdir(norm):
        return out
    for dirpath, dirnames, filenames in os.walk(norm):
        dirnames[:] = sorted([name for name in dirnames if name not in {".git", ".vs", "__pycache__"}])
        for filename in sorted(filenames):
            out.append(os.path.join(dirpath, filename))
    return out


def _cmd_repro_build_check(args: argparse.Namespace) -> int:
    left_abs = os.path.normpath(os.path.abspath(args.left))
    right_abs = os.path.normpath(os.path.abspath(args.right))
    left_paths = _collect_paths(args.left)
    right_paths = _collect_paths(args.right)
    if not left_paths or not right_paths:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.repro_build.inputs_missing"}, indent=2, sort_keys=True))
        return 2

    if os.path.isfile(left_abs) and os.path.isfile(right_abs):
        left_hash = canonical_hash_map([left_abs])
        right_hash = canonical_hash_map([right_abs])
        left_value = next(iter(left_hash.values()), "")
        right_value = next(iter(right_hash.values()), "")
        if left_value != right_value:
            print(json.dumps({"result": "refused", "refusal_code": "refuse.repro_build.hash_mismatch"}, indent=2, sort_keys=True))
            return 2
        print(json.dumps({"result": "complete", "artifacts": 1}, indent=2, sort_keys=True))
        return 0

    if os.path.isdir(left_abs):
        left_root = left_abs
        right_root = right_abs
        left_rel = [os.path.relpath(path, left_root).replace("\\", "/") for path in left_paths]
        right_map = {
            os.path.relpath(path, right_root).replace("\\", "/"): path
            for path in right_paths
        }
        mapped_left = []
        mapped_right = []
        for rel in sorted(left_rel):
            if rel not in right_map:
                print(json.dumps({"result": "refused", "refusal_code": "refuse.repro_build.path_set_mismatch"}, indent=2, sort_keys=True))
                return 2
            mapped_left.append(os.path.join(left_root, rel))
            mapped_right.append(right_map[rel])
        left_paths = mapped_left
        right_paths = mapped_right

    left_hash = canonical_hash_map(left_paths)
    right_hash = canonical_hash_map(right_paths)
    ok, issues = compare_hash_maps(left_hash, right_hash)
    if not ok:
        print(json.dumps({"result": "refused", "refusal_codes": issues}, indent=2, sort_keys=True))
        return 2
    print(json.dumps({"result": "complete", "artifacts": len(left_hash)}, indent=2, sort_keys=True))
    return 0


def _cmd_boundary_check(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    trust_entries, errors = load_trust_policy(os.path.join(repo_root, TRUST_POLICY_REL))
    errors.extend(validate_boundaries(repo_root, trust_entries))
    codes = sorted(set(errors))
    if codes:
        print(json.dumps({"result": "refused", "refusal_codes": codes}, indent=2, sort_keys=True))
        return 2
    print(json.dumps({"result": "complete"}, indent=2, sort_keys=True))
    return 0


def _cmd_privilege_check(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    _, errors = validate_security_roles(os.path.join(repo_root, SECURITY_ROLES_REL))
    errors.extend(scan_for_hardcoded_modes(repo_root))
    codes = sorted(set(errors))
    if codes:
        print(json.dumps({"result": "refused", "refusal_codes": codes}, indent=2, sort_keys=True))
        return 2
    print(json.dumps({"result": "complete"}, indent=2, sort_keys=True))
    return 0


def _cmd_integrity_manifest(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    schema_files, pack_files, tool_files, canonical_artifacts = _manifest_inputs(repo_root)
    payload = _canonicalize(
        generate_manifest(
            repo_root=repo_root,
            schema_files=schema_files,
            pack_files=pack_files,
            tool_files=tool_files,
            canonical_artifacts=canonical_artifacts,
            identity_path=os.path.join(repo_root, "docs", "audit", "identity_fingerprint.json"),
        )
    )
    output_path = os.path.normpath(os.path.abspath(args.output))
    write_manifest(output_path, payload)
    print(json.dumps({"result": "complete", "output": output_path.replace("\\", "/")}, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SecureX trust and integrity enforcement.")
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="Run SecureX trust, boundary, and integrity checks.")
    verify.add_argument("--repo-root", default="")
    verify.set_defaults(func=_run_verify)

    sign_pack_cmd = sub.add_parser("sign-pack", help="Sign a pack artifact with deterministic signature payload.")
    sign_pack_cmd.add_argument("--repo-root", default="")
    sign_pack_cmd.add_argument("--pack-path", required=True)
    sign_pack_cmd.add_argument("--signer-id", required=True)
    sign_pack_cmd.add_argument("--key-id", required=True)
    sign_pack_cmd.add_argument("--key-material", required=True)
    sign_pack_cmd.add_argument("--issued-utc", default="1970-01-01T00:00:00Z")
    sign_pack_cmd.add_argument("--output", required=True)
    sign_pack_cmd.set_defaults(func=_cmd_sign_pack)

    verify_pack_cmd = sub.add_parser("verify-pack", help="Verify a signed pack artifact.")
    verify_pack_cmd.add_argument("--repo-root", default="")
    verify_pack_cmd.add_argument("--pack-path", required=True)
    verify_pack_cmd.add_argument("--signature-json", required=True)
    verify_pack_cmd.add_argument("--key-material", required=True)
    verify_pack_cmd.set_defaults(func=_cmd_verify_pack)

    integrity_cmd = sub.add_parser("integrity-manifest", help="Generate deterministic integrity manifest.")
    integrity_cmd.add_argument("--repo-root", default="")
    integrity_cmd.add_argument("--output", default=os.path.join(OUTPUT_DIR_REL, INTEGRITY_REL))
    integrity_cmd.set_defaults(func=_cmd_integrity_manifest)

    boundary_cmd = sub.add_parser("boundary-check", help="Validate trust boundary invariants.")
    boundary_cmd.add_argument("--repo-root", default="")
    boundary_cmd.set_defaults(func=_cmd_boundary_check)

    privilege_cmd = sub.add_parser("privilege-check", help="Validate role and entitlement enforcement policy.")
    privilege_cmd.add_argument("--repo-root", default="")
    privilege_cmd.set_defaults(func=_cmd_privilege_check)

    repro_cmd = sub.add_parser("repro-build-check", help="Compare canonical artifact hashes between two builds.")
    repro_cmd.add_argument("--repo-root", default="")
    repro_cmd.add_argument("--left", required=True)
    repro_cmd.add_argument("--right", required=True)
    repro_cmd.set_defaults(func=_cmd_repro_build_check)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
