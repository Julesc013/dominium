#!/usr/bin/env python3
"""Validate Dominium document, patch, transaction, and evidence law."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None

DOC_TYPE_SCHEMA = Path("contracts/document/document_type.schema.json")
DOC_REF_SCHEMA = Path("contracts/document/document_ref.schema.json")
DOC_TYPE_REGISTRY = Path("contracts/document/document_type.registry.json")
DOC_DESCRIPTOR_SCHEMA = Path("contracts/document/document_descriptor.schema.json")
PATCH_SCHEMA = Path("contracts/patch/patch.schema.json")
PATCH_KIND_REGISTRY = Path("contracts/patch/patch_kind.registry.json")
PATCH_OPERATION_REGISTRY = Path("contracts/patch/patch_operation.registry.json")
PATCH_POLICY = Path("contracts/patch/patch_policy.contract.toml")
TX_SCHEMA = Path("contracts/transaction/transaction.schema.json")
TX_STATUS_REGISTRY = Path("contracts/transaction/transaction_status.registry.json")
TX_COMMIT_POLICY_REGISTRY = Path("contracts/transaction/transaction_commit_policy.registry.json")
TX_DIAGNOSTIC_REGISTRY = Path("contracts/transaction/transaction_diagnostic.registry.json")
TX_REFUSAL_REGISTRY = Path("contracts/transaction/transaction_refusal.registry.json")
TX_POLICY = Path("contracts/transaction/transaction_policy.contract.toml")
EVIDENCE_BINDING_SCHEMA = Path("contracts/transaction/evidence_binding.schema.json")
ROLLBACK_HANDLE_SCHEMA = Path("contracts/transaction/rollback_handle.schema.json")
FIXTURE_MANIFEST = Path("tests/contract/document_patch/document_patch_fixture_manifest.json")
COMMAND_CONTRACT = Path("contracts/command/command_surface.contract.toml")
ARTIFACT_KIND_REGISTRY = Path("contracts/artifact/artifact_kind.registry.json")

JSON_SURFACES = [DOC_TYPE_SCHEMA, DOC_REF_SCHEMA, DOC_TYPE_REGISTRY, DOC_DESCRIPTOR_SCHEMA, PATCH_SCHEMA,
    PATCH_KIND_REGISTRY, PATCH_OPERATION_REGISTRY, TX_SCHEMA, TX_STATUS_REGISTRY, TX_COMMIT_POLICY_REGISTRY,
    TX_DIAGNOSTIC_REGISTRY, TX_REFUSAL_REGISTRY, EVIDENCE_BINDING_SCHEMA, ROLLBACK_HANDLE_SCHEMA]
TOML_SURFACES = [PATCH_POLICY, TX_POLICY]
REQ_OPS = {"set", "insert", "remove", "move", "replace", "merge", "annotate", "import_asset", "generate", "no_op"}
REQ_STATUSES = {"proposed", "validated", "refused", "dry_run_passed", "dry_run_failed", "committed", "rolled_back", "superseded", "retired"}
REQ_POLICIES = {"dry_run_only", "manual_review_required", "auto_commit_allowed", "package_export_only", "evidence_only"}
REQ_DIAGS = {
    "dominium.diagnostic.document_patch.unknown_document_type",
    "dominium.diagnostic.document_patch.unsupported_patch_operation",
    "dominium.diagnostic.document_patch.precondition_failed",
    "dominium.diagnostic.document_patch.capability_missing",
    "dominium.diagnostic.document_patch.validation_failed",
    "dominium.diagnostic.document_patch.dry_run_failed",
    "dominium.diagnostic.document_patch.rollback_unavailable",
    "dominium.diagnostic.document_patch.target_outside_allowed_root",
    "dominium.diagnostic.document_patch.schema_mismatch",
    "dominium.diagnostic.document_patch.evidence_missing",
}
REQ_REFUSALS = {
    "dominium.refusal.document_patch.unknown_document_type",
    "dominium.refusal.document_patch.unsupported_patch_operation",
    "dominium.refusal.document_patch.precondition_failed",
    "dominium.refusal.document_patch.capability_missing",
    "dominium.refusal.document_patch.validation_failed",
    "dominium.refusal.document_patch.dry_run_failed",
    "dominium.refusal.document_patch.rollback_unavailable",
    "dominium.refusal.document_patch.target_outside_allowed_root",
    "dominium.refusal.document_patch.schema_mismatch",
    "dominium.refusal.document_patch.evidence_required_missing",
}
DOC_TYPE_RE = re.compile(r"^dominium\.document_type\.[a-z0-9][a-z0-9_.-]+$")
DOC_REF_RE = re.compile(r"^dominium\.document_ref\.[a-z0-9][a-z0-9_.-]+$")
PATCH_RE = re.compile(r"^dominium\.patch\.[a-z0-9][a-z0-9_.-]+$")
TX_RE = re.compile(r"^dominium\.transaction\.[a-z0-9][a-z0-9_.-]+$")
ROLLBACK_RE = re.compile(r"^dominium\.rollback\.[a-z0-9][a-z0-9_.-]+$")
ALLOWED_ROOTS = ("contracts/", "docs/", "tests/", ".aide/reports/")
FORBIDDEN_ROOTS = ("engine/", "game/", "runtime/", "apps/", "content/", "build/", "out/", "dist/", ".dominium.local/", ".aide.local/", "external/")


def finding(code: str, message: str, path: str, level: str = "error") -> dict[str, Any]:
    return {"level": level, "code": code, "path": path, "message": message}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else ([] if value is None else [value])


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _strip_comment(line: str) -> str:
    out: list[str] = []
    quoted = False
    escaped = False
    for ch in line:
        if escaped:
            out.append(ch); escaped = False; continue
        if ch == "\\" and quoted:
            out.append(ch); escaped = True; continue
        if ch == '"':
            quoted = not quoted; out.append(ch); continue
        if ch == "#" and not quoted:
            break
        out.append(ch)
    return "".join(out).strip()


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"')
    if raw in {"true", "false"}:
        return raw == "true"
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        items: list[str] = []
        cur: list[str] = []
        quoted = False
        for ch in inner:
            if ch == '"': quoted = not quoted
            if ch == "," and not quoted:
                items.append("".join(cur).strip()); cur = []; continue
            cur.append(ch)
        if cur: items.append("".join(cur).strip())
        return [_parse_value(item) for item in items if item]
    return raw


def load_toml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    if tomllib is not None:
        return tomllib.loads(text)
    root: dict[str, Any] = {}
    cur = root
    for line_no, original in enumerate(text.splitlines(), 1):
        line = _strip_comment(original)
        if not line: continue
        if line.startswith("[[") and line.endswith("]]"):
            cur = {}; root.setdefault(line[2:-2].strip(), []).append(cur); continue
        if line.startswith("[") and line.endswith("]"):
            cur = root
            for part in line[1:-1].strip().split("."):
                cur = cur.setdefault(part, {})
            continue
        if "=" not in line:
            raise ValueError(f"invalid TOML line {line_no}: {original}")
        k, v = line.split("=", 1); cur[k.strip()] = _parse_value(v)
    return root


def ids(data: dict[str, Any], key: str, id_key: str = "id") -> set[str]:
    return {str(item.get(id_key)) for item in as_list(data.get(key)) if isinstance(item, dict) and item.get(id_key)}


def command_ids(root: Path) -> set[str]:
    path = root / COMMAND_CONTRACT
    if not path.exists(): return set()
    data = load_toml(path)
    return ids(data, "command")


def artifact_kinds(root: Path) -> set[str]:
    path = root / ARTIFACT_KIND_REGISTRY
    if not path.exists(): return set()
    return ids(load_json(path), "kinds")


def valid_target_path(value: str) -> bool:
    v = value.replace("\\", "/").strip()
    if not v or v.startswith("/") or ":" in v or ".." in Path(v).parts:
        return False
    if v.startswith(FORBIDDEN_ROOTS):
        return False
    return v.startswith(ALLOWED_ROOTS)


def validate_surfaces(root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rel in JSON_SURFACES:
        path = root / rel
        if not path.exists():
            out.append(finding("SURFACE-MISSING", "required JSON surface is missing", rel.as_posix())); continue
        try:
            data = load_json(path)
        except Exception as exc:
            out.append(finding("SURFACE-INVALID-JSON", str(exc), rel.as_posix())); continue
        if not isinstance(data, dict):
            out.append(finding("SURFACE-NOT-OBJECT", "JSON surface root must be an object", rel.as_posix()))
        if rel.name.endswith(".schema.json") and data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            out.append(finding("SCHEMA-DRAFT-MISMATCH", "schema must declare draft 2020-12", rel.as_posix()))
    for rel in TOML_SURFACES:
        path = root / rel
        if not path.exists():
            out.append(finding("SURFACE-MISSING", "required TOML surface is missing", rel.as_posix())); continue
        try: load_toml(path)
        except Exception as exc: out.append(finding("SURFACE-INVALID-TOML", str(exc), rel.as_posix()))
    if out: return out
    op_ids = ids(load_json(root / PATCH_OPERATION_REGISTRY), "operations")
    st_ids = ids(load_json(root / TX_STATUS_REGISTRY), "statuses")
    pol_ids = ids(load_json(root / TX_COMMIT_POLICY_REGISTRY), "commit_policies")
    diag_ids = ids(load_json(root / TX_DIAGNOSTIC_REGISTRY), "diagnostics")
    refusal_data = load_json(root / TX_REFUSAL_REGISTRY)
    ref_ids = ids(refusal_data, "refusals")
    for req, got, code, path in [(REQ_OPS, op_ids, "OPERATION-REGISTRY-MISSING", PATCH_OPERATION_REGISTRY), (REQ_STATUSES, st_ids, "STATUS-REGISTRY-MISSING", TX_STATUS_REGISTRY), (REQ_POLICIES, pol_ids, "COMMIT-POLICY-REGISTRY-MISSING", TX_COMMIT_POLICY_REGISTRY), (REQ_DIAGS, diag_ids, "DIAGNOSTIC-REGISTRY-MISSING", TX_DIAGNOSTIC_REGISTRY), (REQ_REFUSALS, ref_ids, "REFUSAL-REGISTRY-MISSING", TX_REFUSAL_REGISTRY)]:
        miss = sorted(req - got)
        if miss: out.append(finding(code, "missing required ids: " + ", ".join(miss), path.as_posix()))
    for item in as_list(refusal_data.get("refusals")):
        if isinstance(item, dict) and item.get("diagnostic_ref") not in diag_ids:
            out.append(finding("REFUSAL-DIAGNOSTIC-UNKNOWN", f"{item.get('id')} references unknown diagnostic", TX_REFUSAL_REGISTRY.as_posix()))
    out.extend(validate_document_type_registry(root, op_ids, command_ids(root), artifact_kinds(root)))
    return out


def validate_document_type_registry(root: Path, op_ids: set[str], cmd_ids: set[str], art_ids: set[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    data = load_json(root / DOC_TYPE_REGISTRY)
    seen: set[str] = set()
    for item in as_list(data.get("document_types")):
        if not isinstance(item, dict):
            out.append(finding("DOCUMENT-TYPE-NOT-OBJECT", "document type entry must be an object", DOC_TYPE_REGISTRY.as_posix())); continue
        out.extend(validate_document_type(item, DOC_TYPE_REGISTRY.as_posix(), op_ids, cmd_ids, art_ids))
        dt = str(item.get("document_type_id"))
        if dt in seen: out.append(finding("DOCUMENT-TYPE-DUPLICATE", f"duplicate document type {dt}", DOC_TYPE_REGISTRY.as_posix()))
        seen.add(dt)
    return out


def validate_document_type(data: dict[str, Any], path: str, op_ids: set[str], cmd_ids: set[str], art_ids: set[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    required = ["document_type_id", "version", "stability", "owner", "schema_ref", "artifact_kind_refs", "command_refs", "patch_operation_refs", "validation_policy_ref", "canonical_serialization_policy_ref", "compatibility_policy_ref", "evidence_policy_ref"]
    for key in required:
        if key not in data or data.get(key) in ("", None, []): out.append(finding("DOCUMENT-TYPE-MISSING-FIELD", f"missing {key}", path))
    if not DOC_TYPE_RE.match(str(data.get("document_type_id", ""))): out.append(finding("DOCUMENT-TYPE-ID", "document_type_id must use dominium.document_type.*", path))
    if data.get("stability") != "stable" and data.get("support_claim") == "stable": out.append(finding("DOCUMENT-STABILITY-CLAIM-FALSE", "planned/provisional document type cannot claim stable support", path))
    for op in as_list(data.get("patch_operation_refs")):
        if str(op) not in op_ids: out.append(finding("DOCUMENT-TYPE-UNKNOWN-OPERATION", f"unknown patch operation {op}", path))
    for cmd in as_list(data.get("command_refs")):
        if cmd_ids and str(cmd) not in cmd_ids: out.append(finding("DOCUMENT-TYPE-UNKNOWN-COMMAND", f"unknown command ref {cmd}", path))
    for art in as_list(data.get("artifact_kind_refs")):
        if art_ids and str(art) not in art_ids: out.append(finding("DOCUMENT-TYPE-UNKNOWN-ARTIFACT", f"unknown artifact kind {art}", path))
    return out


def validate_document_ref(data: dict[str, Any], path: str, doc_types: set[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key in ["document_ref_id", "document_type_id", "schema_version", "source_kind"]:
        if key not in data or data.get(key) in ("", None): out.append(finding("DOCUMENT-REF-MISSING-FIELD", f"missing {key}", path))
    if not DOC_REF_RE.match(str(data.get("document_ref_id", ""))): out.append(finding("DOCUMENT-REF-ID", "document_ref_id must use dominium.document_ref.*", path))
    dt = str(data.get("document_type_id", ""))
    if dt not in doc_types: out.append(finding("DOCUMENT-UNKNOWN-TYPE", f"unknown document type {dt}", path))
    if data.get("path_authoritative") is True: out.append(finding("DOCUMENT-PATH-AUTHORITY", "path must not be document authority", path))
    if data.get("path") and not valid_target_path(str(data.get("path"))): out.append(finding("DOCUMENT-PATH-OUTSIDE-ROOT", "document locator path is outside allowed roots", path))
    return out


def validate_refs(values: list[Any], known: set[str], code: str, path: str) -> list[dict[str, Any]]:
    return [finding(code, f"unknown reference {value}", path) for value in values if str(value) not in known]


def validate_patch(data: dict[str, Any], path: str, doc_types: set[str], op_ids: set[str], diag_ids: set[str], ref_ids: set[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key in ["patch_id", "patch_kind", "document_ref", "operation", "path_or_selector", "preconditions", "capability_refs", "deterministic_order_key"]:
        if key not in data or data.get(key) in ("", None): out.append(finding("PATCH-MISSING-FIELD", f"missing {key}", path))
    if "document_ref" not in data: out.append(finding("PATCH-MISSING-DOCUMENT-REF", "patch requires document_ref", path))
    if not PATCH_RE.match(str(data.get("patch_id", ""))): out.append(finding("PATCH-ID", "patch_id must use dominium.patch.*", path))
    op = str(data.get("operation", ""))
    if op not in op_ids: out.append(finding("PATCH-UNKNOWN-OPERATION", f"unknown patch operation {op}", path))
    if isinstance(data.get("document_ref"), dict): out.extend(validate_document_ref(data["document_ref"], path, doc_types))
    if data.get("target_path") and not valid_target_path(str(data.get("target_path"))): out.append(finding("PATCH-TARGET-OUTSIDE-ROOT", "patch target path is outside allowed roots", path))
    out.extend(validate_refs(as_list(data.get("diagnostics_expected")), diag_ids, "DIAGNOSTIC-REF-UNKNOWN", path))
    out.extend(validate_refs(as_list(data.get("refusal_refs")), ref_ids, "REFUSAL-REF-UNKNOWN", path))
    return out


def validate_transaction(data: dict[str, Any], path: str, doc_types: set[str], op_ids: set[str], diag_ids: set[str], ref_ids: set[str], cmd_ids: set[str], art_ids: set[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    required = ["transaction_id", "transaction_kind", "command_ref", "patches", "affected_documents", "affected_artifacts", "capability_decision_refs", "validation_results", "diagnostics", "dry_run_result", "commit_policy", "rollback_policy", "status"]
    for key in required:
        if key not in data or data.get(key) in ("", None): out.append(finding("TX-MISSING-FIELD", f"missing {key}", path))
    if not TX_RE.match(str(data.get("transaction_id", ""))): out.append(finding("TX-ID", "transaction_id must use dominium.transaction.*", path))
    if cmd_ids and data.get("command_ref") not in cmd_ids: out.append(finding("TX-UNKNOWN-COMMAND", f"unknown command_ref {data.get('command_ref')}", path))
    if data.get("status") == "committed" and not data.get("evidence_packet_ref"): out.append(finding("TX-COMMITTED-MISSING-EVIDENCE", "committed transaction requires evidence_packet_ref", path))
    if data.get("status") == "committed" and data.get("commit_policy") == "dry_run_only": out.append(finding("TX-DRY-RUN-ONLY-COMMITTED", "dry_run_only transaction cannot claim committed", path))
    if data.get("status") == "committed" and data.get("dry_run_result", {}).get("status") != "passed": out.append(finding("TX-COMMITTED-WITHOUT-DRY-RUN", "committed transaction requires passed dry-run", path))
    if data.get("status") in {"refused", "dry_run_failed"} and not (data.get("diagnostics") or data.get("refusal_refs")): out.append(finding("TX-REFUSAL-MISSING-DIAGNOSTIC", "refused/failed transaction requires diagnostics or refusals", path))
    out.extend(validate_refs(as_list(data.get("diagnostics")), diag_ids, "DIAGNOSTIC-REF-UNKNOWN", path))
    out.extend(validate_refs(as_list(data.get("refusal_refs")), ref_ids, "REFUSAL-REF-UNKNOWN", path))
    for patch in as_list(data.get("patches")):
        if isinstance(patch, dict): out.extend(validate_patch(patch, path, doc_types, op_ids, diag_ids, ref_ids))
        else: out.append(finding("TX-PATCH-NOT-OBJECT", "patches entries must be patch objects for fixtures", path))
    for doc in as_list(data.get("affected_documents")):
        if isinstance(doc, dict): out.extend(validate_document_ref(doc, path, doc_types))
    for art in as_list(data.get("affected_artifacts")):
        if isinstance(art, dict) and art_ids and art.get("artifact_kind") not in art_ids:
            out.append(finding("TX-UNKNOWN-ARTIFACT", f"unknown artifact kind {art.get('artifact_kind')}", path))
    return out


def validate_rollback(data: dict[str, Any], path: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not ROLLBACK_RE.match(str(data.get("rollback_id", ""))): out.append(finding("ROLLBACK-ID", "rollback_id must use dominium.rollback.*", path))
    if not TX_RE.match(str(data.get("transaction_id", ""))): out.append(finding("ROLLBACK-MISSING-TRANSACTION", "rollback requires transaction_id", path))
    for key in ["rollback_kind", "preimage_hash", "postimage_hash", "evidence_packet_ref"]:
        if key not in data or data.get(key) in ("", None): out.append(finding("ROLLBACK-MISSING-FIELD", f"missing {key}", path))
    return out


def context(root: Path) -> tuple[set[str], set[str], set[str], set[str], set[str], set[str], set[str]]:
    doc_types = ids(load_json(root / DOC_TYPE_REGISTRY), "document_types", "document_type_id")
    op_ids = ids(load_json(root / PATCH_OPERATION_REGISTRY), "operations")
    diag_ids = ids(load_json(root / TX_DIAGNOSTIC_REGISTRY), "diagnostics")
    ref_ids = ids(load_json(root / TX_REFUSAL_REGISTRY), "refusals")
    return doc_types, op_ids, diag_ids, ref_ids, command_ids(root), artifact_kinds(root), ids(load_json(root / TX_STATUS_REGISTRY), "statuses")


def validate_fixture(root: Path, fixture: dict[str, Any]) -> list[dict[str, Any]]:
    rel = str(fixture.get("path", ""))
    path = root / rel
    if not path.exists(): return [finding("FIXTURE-MISSING", "fixture path missing", rel)]
    try: data = load_json(path)
    except Exception as exc: return [finding("FIXTURE-INVALID-JSON", str(exc), rel)]
    doc_types, op_ids, diag_ids, ref_ids, cmd_ids, art_ids, _ = context(root)
    kind = str(fixture.get("fixture_kind", ""))
    if kind == "document_type": got = validate_document_type(data, rel, op_ids, cmd_ids, art_ids)
    elif kind == "document_ref": got = validate_document_ref(data, rel, doc_types)
    elif kind == "patch": got = validate_patch(data, rel, doc_types, op_ids, diag_ids, ref_ids)
    elif kind == "transaction": got = validate_transaction(data, rel, doc_types, op_ids, diag_ids, ref_ids, cmd_ids, art_ids)
    elif kind == "rollback": got = validate_rollback(data, rel)
    else: got = [finding("FIXTURE-UNKNOWN-KIND", f"unknown fixture kind {kind}", rel)]
    codes = {str(item["code"]) for item in got if item.get("level") == "error"}
    expect = fixture.get("expected")
    if expect == "pass" and codes: return [finding("FIXTURE-EXPECTED-PASS-FAILED", "fixture expected pass but failed: " + ", ".join(sorted(codes)), rel)] + got
    if expect == "fail" and not codes: return [finding("FIXTURE-EXPECTED-FAIL-PASSED", "fixture expected fail but passed", rel)]
    missing = set(as_list(fixture.get("expected_codes"))) - codes
    if expect == "fail" and missing: return [finding("FIXTURE-EXPECTED-CODE-MISSING", "missing expected codes: " + ", ".join(sorted(missing)), rel)] + got
    return []


def validate_fixtures(root: Path) -> list[dict[str, Any]]:
    if not (root / FIXTURE_MANIFEST).exists(): return [finding("FIXTURE-MANIFEST-MISSING", "fixture manifest missing", FIXTURE_MANIFEST.as_posix())]
    data = load_json(root / FIXTURE_MANIFEST)
    out: list[dict[str, Any]] = []
    for fixture in as_list(data.get("fixtures")):
        if isinstance(fixture, dict): out.extend(validate_fixture(root, fixture))
        else: out.append(finding("FIXTURE-ENTRY-NOT-OBJECT", "fixture entry must be an object", FIXTURE_MANIFEST.as_posix()))
    return out


def inventory(root: Path) -> dict[str, Any]:
    doc_types, op_ids, diag_ids, ref_ids, cmd_ids, art_ids, status_ids = context(root)
    policies = ids(load_json(root / TX_COMMIT_POLICY_REGISTRY), "commit_policies")
    fixtures = as_list(load_json(root / FIXTURE_MANIFEST).get("fixtures")) if (root / FIXTURE_MANIFEST).exists() else []
    return {"document_types": sorted(doc_types), "patch_operations": sorted(op_ids), "transaction_statuses": sorted(status_ids), "commit_policies": sorted(policies), "diagnostics": sorted(diag_ids), "refusals": sorted(ref_ids), "commands_seen": sorted(cmd_ids), "artifact_kinds_seen": sorted(art_ids), "fixture_count": len(fixtures)}


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    findings: list[dict[str, Any]] = []
    if args.inventory:
        return {"status": "inventory", "findings": [], "inventory": inventory(root)}
    findings.extend(validate_surfaces(root))
    if args.fixtures or args.strict or args.json:
        if not findings: findings.extend(validate_fixtures(root))
    status = "pass" if not any(f.get("level") == "error" for f in findings) else "fail"
    return {"status": status, "findings": findings, "inventory": inventory(root) if not findings else None}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fixtures", action="store_true")
    parser.add_argument("--inventory", action="store_true")
    args = parser.parse_args(argv)
    result = run(args)
    if args.json or args.inventory:
        print(json.dumps(result, indent=2))
    else:
        print(f"document_patch_transaction: {result['status']}")
        for item in result["findings"]:
            print(f"{item['level']} {item['code']} {item['path']}: {item['message']}")
    return 0 if result["status"] in {"pass", "inventory"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
