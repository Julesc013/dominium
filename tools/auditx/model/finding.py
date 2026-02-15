"""AuditX finding model and deterministic validation helpers."""

from dataclasses import dataclass, field
from typing import Dict, List


VALID_CATEGORIES = (
    "reachability",
    "ownership_boundary",
    "canon_drift",
    "schema_usage",
    "capability_misuse",
    "ui_parity",
    "legacy_contamination",
    "derived_freshness",
    "general",
)

VALID_SEVERITIES = ("INFO", "WARN", "RISK", "VIOLATION")
VALID_STATUSES = ("OPEN", "ACK", "RESOLVED", "DEFERRED")
VALID_CLASSIFICATIONS = (
    "CANONICAL",
    "SUPERSEDED",
    "PROTOTYPE",
    "LEGACY",
    "INVALID",
    "TODO-BLOCKED",
)
VALID_RECOMMENDED_ACTIONS = (
    "KEEP",
    "RETIRE",
    "REWRITE",
    "QUARANTINE",
    "ADD_TEST",
    "ADD_RULE",
    "DOC_FIX",
)


@dataclass
class FindingLocation:
    file_path: str
    line_start: int = 0
    line_end: int = 0

    @property
    def file(self) -> str:  # compatibility alias
        return str(self.file_path)

    @property
    def line(self) -> int:  # compatibility alias
        return int(self.line_start)

    @property
    def end_line(self) -> int:  # compatibility alias
        return int(self.line_end)


@dataclass
class Finding:
    finding_id: str
    analyzer_id: str
    category: str
    severity: str
    confidence: float
    status: str
    location: FindingLocation
    evidence: List[str] = field(default_factory=list)
    suggested_classification: str = "TODO-BLOCKED"
    recommended_action: str = "DOC_FIX"
    related_invariants: List[str] = field(default_factory=list)
    related_paths: List[str] = field(default_factory=list)
    fingerprint: str = ""
    created_utc: str = "1970-01-01T00:00:00Z"


def validate_finding_record(record: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    required = (
        "finding_id",
        "analyzer_id",
        "category",
        "severity",
        "confidence",
        "status",
        "location",
        "evidence",
        "suggested_classification",
        "recommended_action",
        "related_invariants",
        "related_paths",
        "fingerprint",
        "created_utc",
    )
    for key in required:
        if key not in record:
            errors.append("missing required field '{}'".format(key))
    if errors:
        return errors

    category = str(record.get("category", ""))
    if category not in VALID_CATEGORIES:
        errors.append("invalid category '{}'".format(category))

    severity = str(record.get("severity", ""))
    if severity not in VALID_SEVERITIES:
        errors.append("invalid severity '{}'".format(severity))

    status = str(record.get("status", ""))
    if status not in VALID_STATUSES:
        errors.append("invalid status '{}'".format(status))

    classification = str(record.get("suggested_classification", ""))
    if classification not in VALID_CLASSIFICATIONS:
        errors.append("invalid suggested_classification '{}'".format(classification))

    action = str(record.get("recommended_action", ""))
    if action not in VALID_RECOMMENDED_ACTIONS:
        errors.append("invalid recommended_action '{}'".format(action))

    try:
        confidence = float(record.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = -1.0
    if confidence < 0.0 or confidence > 1.0:
        errors.append("confidence must be in [0.0, 1.0]")

    location = record.get("location")
    if not isinstance(location, dict):
        errors.append("location must be an object")
    else:
        if not str(location.get("file_path", "")).strip():
            errors.append("location.file_path is required")
        start = int(location.get("line_start", 0) or 0)
        end = int(location.get("line_end", 0) or 0)
        if start < 0 or end < 0:
            errors.append("location line range must be non-negative")
        if start and end and end < start:
            errors.append("location.line_end must be >= line_start")

    for list_key in ("evidence", "related_invariants", "related_paths"):
        value = record.get(list_key)
        if not isinstance(value, list):
            errors.append("'{}' must be a list".format(list_key))

    if not str(record.get("fingerprint", "")).strip():
        errors.append("fingerprint is required")
    if not str(record.get("created_utc", "")).strip():
        errors.append("created_utc is required")

    return errors
