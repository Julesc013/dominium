"""AuditX finding serialization helpers."""

import hashlib
import json
from typing import Dict, List


def _severity_rank(value: str) -> int:
    token = str(value or "").strip().upper()
    if token == "VIOLATION":
        return 0
    if token == "RISK":
        return 1
    if token == "WARN":
        return 2
    if token == "INFO":
        return 3
    return 9


def _stable_fingerprint_payload(finding_dict: Dict[str, object]) -> Dict[str, object]:
    payload = dict(finding_dict)
    payload.pop("finding_id", None)
    payload.pop("fingerprint", None)
    payload.pop("created_utc", None)  # informational only; excluded by contract
    return payload


def compute_fingerprint(finding_dict: Dict[str, object]) -> str:
    payload = _stable_fingerprint_payload(finding_dict)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def finding_to_dict(finding) -> Dict[str, object]:
    location = {
        "file_path": str(finding.location.file_path),
    }
    if int(finding.location.line_start):
        location["line_start"] = int(finding.location.line_start)
    if int(finding.location.line_end):
        location["line_end"] = int(finding.location.line_end)
    return {
        "finding_id": str(finding.finding_id),
        "analyzer_id": str(finding.analyzer_id),
        "category": str(finding.category),
        "severity": str(finding.severity),
        "confidence": float(finding.confidence),
        "status": str(finding.status),
        "location": location,
        "evidence": [str(item) for item in list(finding.evidence)],
        "suggested_classification": str(finding.suggested_classification),
        "recommended_action": str(finding.recommended_action),
        "related_invariants": sorted(set(str(item) for item in list(finding.related_invariants))),
        "related_paths": sorted(set(str(item) for item in list(finding.related_paths))),
        "fingerprint": str(finding.fingerprint),
        "created_utc": str(finding.created_utc),
    }


def sort_findings(finding_dicts: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return sorted(
        finding_dicts,
        key=lambda item: (
            _severity_rank(str(item.get("severity", ""))),
            str(item.get("analyzer_id", "")),
            str((item.get("location") or {}).get("file_path", "")),
            int(((item.get("location") or {}).get("line_start", 0) or 0)),
            str(item.get("category", "")),
            str(item.get("finding_id", "")),
        ),
    )
