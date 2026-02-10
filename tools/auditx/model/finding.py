"""AuditX finding model."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class FindingLocation:
    file: str
    line: int = 0
    end_line: int = 0


@dataclass
class Finding:
    analyzer_id: str
    finding_id: str
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
    created_utc: str = "1970-01-01T00:00:00Z"
    fingerprint: str = ""

