"""E448 MVP cross-platform non-canonical serialization smell analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E448_NON_CANONICAL_SERIALIZATION_SMELL"
RULE_ID = "INV-MVP-CROSS-PLATFORM-MUST-PASS"
HELPER_REL = "tools/mvp/cross_platform_gate_common.py"
HASHES_REL = "build/mvp/mvp_cross_platform_hashes.json"
REPORT_REL = "build/mvp/mvp_cross_platform_matrix.json"
BASELINE_REL = "data/regression/mvp_cross_platform_baseline.json"


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _load_json(path):
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid"
    if not isinstance(payload, dict):
        return {}, "invalid"
    return payload, ""


def _finding(rel_path, message, severity="RISK", confidence=0.92):
    return make_finding(
        analyzer_id=ANALYZER_ID,
        category="release.non_canonical_serialization_smell",
        severity=severity,
        confidence=confidence,
        file_path=rel_path,
        evidence=[message],
        suggested_classification="TODO-BLOCKED",
        recommended_action="ADD_RULE",
        related_invariants=[RULE_ID],
        related_paths=[rel_path],
    )


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []

    helper_path = os.path.join(repo_root, HELPER_REL.replace("/", os.sep))
    helper_text = _read_text(helper_path)
    if not helper_text:
        return [_finding(HELPER_REL, "MVP cross-platform helper is missing or unreadable.")]

    for token, message in (
        ("canonical_json_text", "MVP cross-platform helper must use canonical_json_text for persisted artifacts."),
        ("canonical_sha256", "MVP cross-platform helper must derive fingerprints with canonical_sha256."),
        ("compare_canonical_hashes_only", "MVP cross-platform helper must mark comparisons as canonical-hash-only."),
        ('HOST_META_IGNORED = ("timestamps", "path_separators", "absolute_paths")', "MVP cross-platform helper must pin the canonical host-meta exclusion set."),
        ("_write_canonical_json(report_abs, report_payload)", "MVP cross-platform helper must persist the matrix report with canonical JSON."),
        ("_write_canonical_json(hashes_abs, hash_summary)", "MVP cross-platform helper must persist the hash summary with canonical JSON."),
        ("_write_canonical_json(baseline_abs, baseline_payload)", "MVP cross-platform helper must persist the regression baseline with canonical JSON."),
    ):
        if token in helper_text:
            continue
        findings.append(_finding(HELPER_REL, message))

    report_payload, report_error = _load_json(os.path.join(repo_root, REPORT_REL.replace("/", os.sep)))
    if report_error:
        findings.append(_finding(REPORT_REL, "MVP cross-platform report must be valid JSON."))
    else:
        comparison = dict(report_payload.get("comparison") or {})
        if not bool(comparison.get("compare_canonical_hashes_only", False)):
            findings.append(_finding(REPORT_REL, "MVP cross-platform report must record compare_canonical_hashes_only=true."))
        host_meta_ignored = [str(item) for item in list(report_payload.get("host_meta_ignored") or [])]
        if host_meta_ignored != ["timestamps", "path_separators", "absolute_paths"]:
            findings.append(_finding(REPORT_REL, "MVP cross-platform report must record the canonical host-meta exclusion set."))

    hashes_payload, hashes_error = _load_json(os.path.join(repo_root, HASHES_REL.replace("/", os.sep)))
    if hashes_error:
        findings.append(_finding(HASHES_REL, "MVP cross-platform hash summary must be valid JSON."))
    else:
        if str(hashes_payload.get("gate_id", "")).strip() != "mvp.cross_platform.gate.v1":
            findings.append(_finding(HASHES_REL, "MVP cross-platform hash summary must record gate_id mvp.cross_platform.gate.v1."))
        for field in (
            "platform_canonical_fingerprints",
            "platform_proof_anchor_fingerprints",
            "platform_negotiation_record_fingerprints",
            "platform_pack_lock_fingerprints",
            "platform_repro_bundle_fingerprints",
            "platform_bundle_fingerprints",
            "portable_linked_parity_hash",
            "negotiation_matrix_hash",
            "comparison_hash",
            "result_hash",
            "deterministic_fingerprint",
        ):
            value = hashes_payload.get(field)
            if value is None or (isinstance(value, str) and not str(value).strip()):
                findings.append(_finding(HASHES_REL, "MVP cross-platform hash summary missing '{}'.".format(field)))

    baseline_payload, baseline_error = _load_json(os.path.join(repo_root, BASELINE_REL.replace("/", os.sep)))
    if baseline_error:
        findings.append(_finding(BASELINE_REL, "MVP cross-platform baseline must be valid JSON."))
    else:
        update_policy = dict(baseline_payload.get("update_policy") or {})
        if str(update_policy.get("required_commit_tag", "")).strip() != "MVP-CROSS-PLATFORM-REGRESSION-UPDATE":
            findings.append(
                _finding(
                    BASELINE_REL,
                    "MVP cross-platform baseline must require MVP-CROSS-PLATFORM-REGRESSION-UPDATE for updates.",
                )
            )

    return findings
