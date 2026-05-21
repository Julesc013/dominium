"""Deterministic document patch transaction helper.

This module applies a narrow Process-like patch contract to the `content` member
of a Dominium document. It does not commit storage, migrate schemas, or grant
authority; it only validates and applies an already declared transaction.
"""

from __future__ import annotations

import copy
import math
import re
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence, Tuple

from runtime.serialization.canonical_json import canonical_json_text, canonical_sha256


PATCH_TRANSACTION_SCHEMA_ID = "dominium.document.patch_transaction.v1"
PATCH_TRANSACTION_SCHEMA_VERSION = "1.0.0"
PATCH_TRANSACTION_STABILITY = "provisional"

_VALID_OPS = {"test", "add", "replace", "remove"}
_TRANSACTION_ID_RE = re.compile(r"^dominium\.document\.patch_txn\.[a-z0-9][a-z0-9_.-]*$")
_TRANSACTION_KEYS = {
    "schema_id",
    "schema_version",
    "stability",
    "transaction_id",
    "document_id",
    "document_schema_id",
    "expected_content_hash",
    "authority",
    "operations",
    "evidence",
}
_AUTHORITY_KEYS = {"authority_origin", "law_profile_id", "actor_id"}
_VALUE_OPS = {"test", "add", "replace"}
_HEX = set("0123456789abcdef")


@dataclass(frozen=True)
class PatchFinding:
    """A deterministic validation or apply finding."""

    code: str
    message: str
    operation_index: Optional[int] = None
    path: Tuple[object, ...] = ()

    def as_dict(self) -> dict:
        item = {
            "code": self.code,
            "message": self.message,
            "path": list(self.path),
        }
        if self.operation_index is not None:
            item["operation_index"] = self.operation_index
        return item


@dataclass(frozen=True)
class PatchTransactionResult:
    """Result of validating or applying a document patch transaction."""

    status: str
    transaction_id: str
    document_id: str
    before_hash: Optional[str]
    after_hash: Optional[str]
    document: Optional[dict]
    findings: Tuple[PatchFinding, ...]
    applied_operations: int

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "transaction_id": self.transaction_id,
            "document_id": self.document_id,
            "before_hash": self.before_hash,
            "after_hash": self.after_hash,
            "applied_operations": self.applied_operations,
            "findings": [finding.as_dict() for finding in self.findings],
            "document": copy.deepcopy(self.document),
        }


def canonical_content_hash(content: object) -> str:
    """Return the canonical SHA-256 hash for JSON-like document content."""

    findings = _json_like_findings(content, ())
    if findings:
        raise ValueError("; ".join(finding.message for finding in findings))
    return canonical_sha256(content)


def document_content_hash(document: Mapping[str, object]) -> str:
    """Return the canonical SHA-256 hash of a Dominium document's content."""

    if not isinstance(document, Mapping) or "content" not in document:
        raise ValueError("document must be an object with a content member")
    return canonical_content_hash(document["content"])


def validate_patch_transaction(
    document: Mapping[str, object],
    transaction: Mapping[str, object],
) -> Tuple[PatchFinding, ...]:
    """Validate a patch transaction against a document without returning output."""

    return apply_patch_transaction(document, transaction).findings


def apply_patch_transaction(
    document: Mapping[str, object],
    transaction: Mapping[str, object],
) -> PatchTransactionResult:
    """Apply a valid patch transaction to a copy of `document`.

    Refusal is atomic: if any precondition or operation fails, no patched
    document is returned.
    """

    transaction_id = _string_field(transaction, "transaction_id")
    document_id = _string_field(document, "document_id")
    findings = list(_validate_transaction_shape(document, transaction))
    before_hash: Optional[str] = None
    if isinstance(document, Mapping) and "content" in document:
        content_findings = _json_like_findings(document["content"], ("content",))
        if not content_findings:
            before_hash = canonical_sha256(document["content"])
    if findings:
        return _refused(transaction_id, document_id, before_hash, findings, 0)

    expected_hash = str(transaction["expected_content_hash"])
    if before_hash != expected_hash:
        return _refused(
            transaction_id,
            document_id,
            before_hash,
            [
                PatchFinding(
                    "content_hash_mismatch",
                    "transaction expected_content_hash does not match document content",
                )
            ],
            0,
        )

    working_content = copy.deepcopy(document["content"])
    operations = transaction["operations"]
    applied = 0
    for index, operation in enumerate(operations if isinstance(operations, list) else []):
        finding = _apply_operation(working_content, operation, index)
        if finding is not None:
            return _refused(transaction_id, document_id, before_hash, [finding], applied)
        applied += 1

    patched_document = copy.deepcopy(dict(document))
    patched_document["content"] = working_content
    after_hash = canonical_sha256(working_content)
    return PatchTransactionResult(
        status="ok",
        transaction_id=transaction_id,
        document_id=document_id,
        before_hash=before_hash,
        after_hash=after_hash,
        document=patched_document,
        findings=(),
        applied_operations=applied,
    )


def _refused(
    transaction_id: str,
    document_id: str,
    before_hash: Optional[str],
    findings: Sequence[PatchFinding],
    applied: int,
) -> PatchTransactionResult:
    return PatchTransactionResult(
        status="refused",
        transaction_id=transaction_id,
        document_id=document_id,
        before_hash=before_hash,
        after_hash=None,
        document=None,
        findings=tuple(findings),
        applied_operations=applied,
    )


def _string_field(value: object, key: str) -> str:
    if isinstance(value, Mapping) and isinstance(value.get(key), str):
        return str(value.get(key))
    return ""


def _validate_transaction_shape(
    document: Mapping[str, object],
    transaction: Mapping[str, object],
) -> Tuple[PatchFinding, ...]:
    findings = []
    if not isinstance(document, Mapping):
        return (PatchFinding("document_not_object", "document must be an object"),)
    if not isinstance(transaction, Mapping):
        return (PatchFinding("transaction_not_object", "transaction must be an object"),)

    for key in ("document_id", "schema_id", "content"):
        if key not in document:
            findings.append(PatchFinding("document_missing_field", "document is missing required field " + key))
    for key in (
        "schema_id",
        "schema_version",
        "stability",
        "transaction_id",
        "document_id",
        "document_schema_id",
        "expected_content_hash",
        "authority",
        "operations",
    ):
        if key not in transaction:
            findings.append(PatchFinding("transaction_missing_field", "transaction is missing required field " + key))

    extra_keys = sorted(str(key) for key in transaction.keys() if str(key) not in _TRANSACTION_KEYS)
    if extra_keys:
        findings.append(
            PatchFinding(
                "transaction_unknown_field",
                "transaction contains unsupported fields: " + ", ".join(extra_keys),
            )
        )

    if findings:
        return tuple(findings)

    if transaction["schema_id"] != PATCH_TRANSACTION_SCHEMA_ID:
        findings.append(PatchFinding("schema_id_mismatch", "transaction schema_id is not supported"))
    if transaction["schema_version"] != PATCH_TRANSACTION_SCHEMA_VERSION:
        findings.append(PatchFinding("schema_version_mismatch", "transaction schema_version is not supported"))
    if transaction["stability"] != PATCH_TRANSACTION_STABILITY:
        findings.append(PatchFinding("stability_mismatch", "transaction stability is not supported"))
    if not isinstance(transaction.get("transaction_id"), str) or not _TRANSACTION_ID_RE.match(str(transaction.get("transaction_id"))):
        findings.append(PatchFinding("transaction_id_invalid", "transaction_id must match dominium.document.patch_txn.*"))
    if not _nonempty_string(transaction.get("document_id")):
        findings.append(PatchFinding("transaction_document_id_invalid", "document_id must be a non-empty string"))
    if not _nonempty_string(transaction.get("document_schema_id")):
        findings.append(PatchFinding("transaction_document_schema_id_invalid", "document_schema_id must be a non-empty string"))
    if not _sha256_string(transaction.get("expected_content_hash")):
        findings.append(PatchFinding("expected_content_hash_invalid", "expected_content_hash must be lowercase SHA-256 hex"))

    if _string_field(document, "document_id") != str(transaction["document_id"]):
        findings.append(PatchFinding("document_id_mismatch", "transaction document_id does not match document"))
    if _string_field(document, "schema_id") != str(transaction["document_schema_id"]):
        findings.append(PatchFinding("document_schema_mismatch", "transaction document_schema_id does not match document schema_id"))

    findings.extend(_validate_authority(transaction.get("authority")))
    findings.extend(_validate_evidence(transaction.get("evidence")))
    findings.extend(_json_like_findings(document.get("content"), ("content",)))
    findings.extend(_validate_operations(transaction.get("operations")))
    return tuple(findings)


def _validate_authority(value: object) -> Tuple[PatchFinding, ...]:
    if not isinstance(value, Mapping):
        return (PatchFinding("authority_not_object", "authority must be an object"),)
    findings = []
    extra = sorted(str(key) for key in value.keys() if str(key) not in _AUTHORITY_KEYS)
    if extra:
        findings.append(PatchFinding("authority_unknown_field", "authority contains unsupported fields: " + ", ".join(extra)))
    for key in sorted(_AUTHORITY_KEYS):
        if not _nonempty_string(value.get(key)):
            findings.append(PatchFinding("authority_missing_field", "authority is missing required field " + key))
    return tuple(findings)


def _validate_evidence(value: object) -> Tuple[PatchFinding, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        return (PatchFinding("evidence_not_array", "evidence must be an array when present"),)
    findings = []
    seen = set()
    for index, item in enumerate(value):
        if not _nonempty_string(item):
            findings.append(PatchFinding("evidence_item_invalid", "evidence entries must be non-empty strings", None, ("evidence", index)))
            continue
        if item in seen:
            findings.append(PatchFinding("evidence_duplicate", "evidence entries must be unique", None, ("evidence", index)))
        seen.add(item)
    return tuple(findings)


def _validate_operations(value: object) -> Tuple[PatchFinding, ...]:
    if not isinstance(value, list):
        return (PatchFinding("operations_not_array", "operations must be an array"),)
    findings = []
    if not value:
        findings.append(PatchFinding("operations_empty", "operations must contain at least one operation"))
    if len(value) > 100:
        findings.append(PatchFinding("operations_too_many", "operations may contain at most 100 entries"))
    for index, operation in enumerate(value):
        findings.extend(_validate_operation(operation, index))
    return tuple(findings)


def _validate_operation(operation: object, index: int) -> Tuple[PatchFinding, ...]:
    if not isinstance(operation, Mapping):
        return (PatchFinding("operation_not_object", "operation must be an object", index),)
    findings = []
    op = operation.get("op")
    if op not in _VALID_OPS:
        findings.append(PatchFinding("operation_unknown_op", "operation op is not supported", index))
    expected_keys = {"op", "path"}
    if op in _VALUE_OPS:
        expected_keys.add("value")
    extra = sorted(str(key) for key in operation.keys() if str(key) not in expected_keys)
    if extra:
        findings.append(PatchFinding("operation_unknown_field", "operation contains unsupported fields: " + ", ".join(extra), index))
    if op in _VALUE_OPS and "value" not in operation:
        findings.append(PatchFinding("operation_missing_value", "operation requires value", index))
    if op == "remove" and "value" in operation:
        findings.append(PatchFinding("remove_has_value", "remove operation must not carry value", index))

    path = operation.get("path")
    if not isinstance(path, list):
        findings.append(PatchFinding("operation_path_not_array", "operation path must be an array", index))
    else:
        if op in {"add", "replace", "remove"} and not path:
            findings.append(PatchFinding("operation_empty_mutation_path", "mutation operation path must not be empty", index))
        if len(path) > 64:
            findings.append(PatchFinding("operation_path_too_deep", "operation path may contain at most 64 segments", index))
        for segment_index, segment in enumerate(path):
            if not _valid_path_segment(segment):
                findings.append(
                    PatchFinding(
                        "operation_path_segment_invalid",
                        "path segment must be a non-empty string or non-negative integer",
                        index,
                        tuple(path[: segment_index + 1]),
                    )
                )
    if "value" in operation:
        value_path = tuple(path) if isinstance(path, list) else ()
        findings.extend(_json_like_findings(operation.get("value"), value_path, index))
    return tuple(findings)


def _apply_operation(root: object, operation: object, index: int) -> Optional[PatchFinding]:
    if not isinstance(operation, Mapping):
        return PatchFinding("operation_not_object", "operation must be an object", index)
    op = operation.get("op")
    path = operation.get("path")
    if not isinstance(path, list):
        return PatchFinding("operation_path_not_array", "operation path must be an array", index)

    if op == "test":
        found, current = _get_value(root, path)
        if not found:
            return PatchFinding("test_path_missing", "test path does not exist", index, tuple(path))
        if canonical_json_text(current) != canonical_json_text(operation.get("value")):
            return PatchFinding("test_mismatch", "test value does not match current document content", index, tuple(path))
        return None

    parent_found, parent, token = _resolve_parent(root, path)
    if not parent_found:
        return PatchFinding("parent_path_missing", "operation parent path does not exist", index, tuple(path))

    if op == "add":
        return _apply_add(parent, token, operation.get("value"), index, tuple(path))
    if op == "replace":
        return _apply_replace(parent, token, operation.get("value"), index, tuple(path))
    if op == "remove":
        return _apply_remove(parent, token, index, tuple(path))
    return PatchFinding("operation_unknown_op", "operation op is not supported", index, tuple(path))


def _apply_add(parent: object, token: object, value: object, index: int, path: Tuple[object, ...]) -> Optional[PatchFinding]:
    if isinstance(parent, dict):
        if not isinstance(token, str):
            return PatchFinding("object_key_type_invalid", "object targets require a string key", index, path)
        if token in parent:
            return PatchFinding("add_target_exists", "add target already exists", index, path)
        parent[token] = copy.deepcopy(value)
        return None
    if isinstance(parent, list):
        if not _strict_int(token):
            return PatchFinding("array_index_type_invalid", "array targets require an integer index", index, path)
        position = int(token)
        if position < 0 or position > len(parent):
            return PatchFinding("array_index_out_of_range", "add index must be between zero and array length", index, path)
        parent.insert(position, copy.deepcopy(value))
        return None
    return PatchFinding("parent_not_container", "operation parent is not an object or array", index, path)


def _apply_replace(parent: object, token: object, value: object, index: int, path: Tuple[object, ...]) -> Optional[PatchFinding]:
    if isinstance(parent, dict):
        if not isinstance(token, str):
            return PatchFinding("object_key_type_invalid", "object targets require a string key", index, path)
        if token not in parent:
            return PatchFinding("replace_target_missing", "replace target does not exist", index, path)
        parent[token] = copy.deepcopy(value)
        return None
    if isinstance(parent, list):
        if not _strict_int(token):
            return PatchFinding("array_index_type_invalid", "array targets require an integer index", index, path)
        position = int(token)
        if position < 0 or position >= len(parent):
            return PatchFinding("array_index_out_of_range", "replace index must address an existing array item", index, path)
        parent[position] = copy.deepcopy(value)
        return None
    return PatchFinding("parent_not_container", "operation parent is not an object or array", index, path)


def _apply_remove(parent: object, token: object, index: int, path: Tuple[object, ...]) -> Optional[PatchFinding]:
    if isinstance(parent, dict):
        if not isinstance(token, str):
            return PatchFinding("object_key_type_invalid", "object targets require a string key", index, path)
        if token not in parent:
            return PatchFinding("remove_target_missing", "remove target does not exist", index, path)
        del parent[token]
        return None
    if isinstance(parent, list):
        if not _strict_int(token):
            return PatchFinding("array_index_type_invalid", "array targets require an integer index", index, path)
        position = int(token)
        if position < 0 or position >= len(parent):
            return PatchFinding("array_index_out_of_range", "remove index must address an existing array item", index, path)
        del parent[position]
        return None
    return PatchFinding("parent_not_container", "operation parent is not an object or array", index, path)


def _resolve_parent(root: object, path: Sequence[object]) -> Tuple[bool, object, object]:
    if not path:
        return False, None, None
    found, parent = _get_value(root, path[:-1])
    if not found:
        return False, None, path[-1]
    return True, parent, path[-1]


def _get_value(root: object, path: Sequence[object]) -> Tuple[bool, object]:
    current = root
    for segment in path:
        if isinstance(current, Mapping):
            if not isinstance(segment, str) or segment not in current:
                return False, None
            current = current[segment]
            continue
        if isinstance(current, list):
            if not _strict_int(segment):
                return False, None
            position = int(segment)
            if position < 0 or position >= len(current):
                return False, None
            current = current[position]
            continue
        return False, None
    return True, current


def _json_like_findings(value: object, path: Tuple[object, ...], operation_index: Optional[int] = None) -> Tuple[PatchFinding, ...]:
    findings = []
    if value is None or isinstance(value, (str, bool)):
        return ()
    if _strict_int(value):
        return ()
    if isinstance(value, float):
        if math.isfinite(value):
            return ()
        return (PatchFinding("json_number_not_finite", "JSON number must be finite", operation_index, path),)
    if isinstance(value, Mapping):
        for key, item in sorted(value.items(), key=lambda row: str(row[0])):
            if not isinstance(key, str) or not key:
                findings.append(PatchFinding("json_object_key_invalid", "JSON object keys must be non-empty strings", operation_index, path))
                continue
            findings.extend(_json_like_findings(item, path + (key,), operation_index))
        return tuple(findings)
    if isinstance(value, list):
        for item_index, item in enumerate(value):
            findings.extend(_json_like_findings(item, path + (item_index,), operation_index))
        return tuple(findings)
    return (PatchFinding("json_value_invalid", "value must be JSON-like", operation_index, path),)


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def _sha256_string(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in _HEX for ch in value)


def _strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_path_segment(value: object) -> bool:
    return (isinstance(value, str) and bool(value)) or (_strict_int(value) and value >= 0)


__all__ = [
    "PATCH_TRANSACTION_SCHEMA_ID",
    "PATCH_TRANSACTION_SCHEMA_VERSION",
    "PatchFinding",
    "PatchTransactionResult",
    "apply_patch_transaction",
    "canonical_content_hash",
    "document_content_hash",
    "validate_patch_transaction",
]
