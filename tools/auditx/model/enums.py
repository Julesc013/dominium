"""AuditX model enums."""

CATEGORIES = (
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

SEVERITIES = ("INFO", "WARN", "RISK", "VIOLATION")
STATUSES = ("OPEN", "ACK", "RESOLVED", "DEFERRED")

CLASSIFICATIONS = (
    "CANONICAL",
    "SUPERSEDED",
    "PROTOTYPE",
    "LEGACY",
    "INVALID",
    "TODO-BLOCKED",
)

RECOMMENDED_ACTIONS = (
    "KEEP",
    "RETIRE",
    "REWRITE",
    "QUARANTINE",
    "ADD_TEST",
    "ADD_RULE",
    "DOC_FIX",
)

