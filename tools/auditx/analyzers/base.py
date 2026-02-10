"""Analyzer base helpers."""

from model import Finding, FindingLocation


def make_finding(
    analyzer_id,
    category,
    severity,
    confidence,
    file_path,
    evidence,
    suggested_classification,
    recommended_action,
    status="OPEN",
    line=0,
    end_line=0,
    related_invariants=None,
    related_paths=None,
):
    return Finding(
        analyzer_id=analyzer_id,
        finding_id="",
        category=category,
        severity=severity,
        confidence=float(confidence),
        status=status,
        location=FindingLocation(file=file_path, line=line, end_line=end_line),
        evidence=list(evidence or []),
        suggested_classification=suggested_classification,
        recommended_action=recommended_action,
        related_invariants=list(related_invariants or []),
        related_paths=list(related_paths or []),
    )
