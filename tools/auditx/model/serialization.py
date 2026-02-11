"""AuditX finding serialization helpers."""

import hashlib
import json


def _stable_fingerprint_payload(finding_dict):
    payload = dict(finding_dict)
    payload.pop("finding_id", None)
    payload.pop("fingerprint", None)
    return payload


def compute_fingerprint(finding_dict):
    payload = _stable_fingerprint_payload(finding_dict)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def finding_to_dict(finding):
    location = {
        "file": finding.location.file,
    }
    if finding.location.line:
        location["line"] = finding.location.line
    if finding.location.end_line:
        location["end_line"] = finding.location.end_line
    return {
        "analyzer_id": finding.analyzer_id,
        "finding_id": finding.finding_id,
        "category": finding.category,
        "severity": finding.severity,
        "confidence": float(finding.confidence),
        "status": finding.status,
        "location": location,
        "evidence": list(finding.evidence),
        "suggested_classification": finding.suggested_classification,
        "recommended_action": finding.recommended_action,
        "related_invariants": sorted(set(finding.related_invariants)),
        "related_paths": sorted(set(finding.related_paths)),
        "fingerprint": finding.fingerprint,
    }


def sort_findings(finding_dicts):
    return sorted(
        finding_dicts,
        key=lambda item: (
            item.get("analyzer_id", ""),
            item.get("category", ""),
            item.get("severity", ""),
            item.get("location", {}).get("file", ""),
            item.get("finding_id", ""),
        ),
    )
