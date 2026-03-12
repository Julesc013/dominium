"""E447 MVP cross-platform platform-dependent behavior smell analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E447_PLATFORM_DEPENDENT_BEHAVIOR_SMELL"
RULE_ID = "INV-MVP-CROSS-PLATFORM-MUST-PASS"
DOCTRINE_REL = "docs/mvp/MVP_CROSS_PLATFORM_GATE.md"
HELPER_REL = "tools/mvp/cross_platform_gate_common.py"
TOOL_REL = "tools/mvp/tool_run_cross_platform_matrix.py"
REPORT_REL = "build/mvp/mvp_cross_platform_matrix.json"
BASELINE_REL = "data/regression/mvp_cross_platform_baseline.json"
FINAL_REL = "docs/audit/MVP_CROSS_PLATFORM_FINAL.md"
TEST_RELS = (
    "tools/xstack/testx/tests/test_cross_platform_hash_agreement.py",
    "tools/xstack/testx/tests/test_portable_linked_parity.py",
    "tools/xstack/testx/tests/test_negotiation_record_stable.py",
    "tools/xstack/testx/tests/test_bundle_hash_same_across_os.py",
)


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


def _missing_file_finding(rel_path, message):
    return make_finding(
        analyzer_id=ANALYZER_ID,
        category="release.platform_dependent_behavior_smell",
        severity="RISK",
        confidence=0.93,
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

    required_files = (
        (DOCTRINE_REL, "MVP cross-platform doctrine is missing."),
        (HELPER_REL, "MVP cross-platform helper is missing."),
        (TOOL_REL, "MVP cross-platform matrix orchestrator is missing."),
        (REPORT_REL, "MVP cross-platform matrix report is missing."),
        (BASELINE_REL, "MVP cross-platform regression baseline is missing."),
        (FINAL_REL, "MVP cross-platform final audit report is missing."),
    ) + tuple((rel, "MVP cross-platform TestX artifact is missing.") for rel in TEST_RELS)
    for rel, message in required_files:
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(_missing_file_finding(rel, message))

    doctrine_text = _read_text(os.path.join(repo_root, DOCTRINE_REL.replace("/", os.sep))).lower()
    for token, message in (
        ("windows", "MVP cross-platform doctrine must require the windows lane."),
        ("macos", "MVP cross-platform doctrine must require the macos lane."),
        ("linux", "MVP cross-platform doctrine must require the linux lane."),
        ("portable vs linked parity", "MVP cross-platform doctrine must require portable-vs-linked parity."),
        ("timestamps, path separators, and absolute paths", "MVP cross-platform doctrine must declare the canonical host-meta exclusion set."),
        ("mvp-cross-platform-regression-update", "MVP cross-platform doctrine must declare the regression update tag."),
    ):
        if token in doctrine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.platform_dependent_behavior_smell",
                severity="WARN",
                confidence=0.82,
                file_path=DOCTRINE_REL,
                evidence=[message],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=[RULE_ID],
                related_paths=[DOCTRINE_REL],
            )
        )

    report_payload, report_error = _load_json(os.path.join(repo_root, REPORT_REL.replace("/", os.sep)))
    if report_error:
        findings.append(_missing_file_finding(REPORT_REL, "MVP cross-platform report must be valid JSON."))
    else:
        if str(report_payload.get("gate_id", "")).strip() != "mvp.cross_platform.gate.v1":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.platform_dependent_behavior_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=REPORT_REL,
                    evidence=["MVP cross-platform report must record gate_id mvp.cross_platform.gate.v1."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )
        if str(report_payload.get("result", "")).strip() != "complete":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.platform_dependent_behavior_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=REPORT_REL,
                    evidence=["MVP cross-platform report must record result=complete before release."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )
        platform_order = [str(item) for item in list(report_payload.get("platform_order") or [])]
        if platform_order != ["windows", "macos", "linux"]:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.platform_dependent_behavior_smell",
                    severity="RISK",
                    confidence=0.92,
                    file_path=REPORT_REL,
                    evidence=["MVP cross-platform report must preserve platform_order windows/macos/linux."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )
        if int(report_payload.get("default_degrade_event_count", 0) or 0) != 0:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.platform_dependent_behavior_smell",
                    severity="RISK",
                    confidence=0.94,
                    file_path=REPORT_REL,
                    evidence=["MVP cross-platform report must record zero default-lane degrade events."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )
        assertions = dict(report_payload.get("assertions") or {})
        for key in (
            "gate0_complete",
            "gate1_complete",
            "platform_hashes_match",
            "portable_linked_parity",
            "negotiation_matrix_stable",
            "no_silent_degrade",
        ):
            if bool(assertions.get(key, False)):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.platform_dependent_behavior_smell",
                    severity="RISK",
                    confidence=0.92,
                    file_path=REPORT_REL,
                    evidence=["MVP cross-platform report assertion '{}' must pass before release.".format(key)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )
        comparison = dict(report_payload.get("comparison") or {})
        if list(comparison.get("mismatches") or []):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.platform_dependent_behavior_smell",
                    severity="RISK",
                    confidence=0.94,
                    file_path=REPORT_REL,
                    evidence=["MVP cross-platform report must not record mismatches before release."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )
        for key in (
            "required_platforms_present",
            "hashes_match_across_platforms",
            "portable_linked_parity",
            "negotiation_records_stable",
            "no_platform_mismatches",
            "no_silent_degrade",
        ):
            if bool(dict(comparison.get("assertions") or {}).get(key, False)):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.platform_dependent_behavior_smell",
                    severity="RISK",
                    confidence=0.91,
                    file_path=REPORT_REL,
                    evidence=["MVP cross-platform comparison assertion '{}' must pass before release.".format(key)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )

    final_text = _read_text(os.path.join(repo_root, FINAL_REL.replace("/", os.sep))).lower()
    for token, message in (
        ("# mvp cross-platform final", "MVP cross-platform final report must declare the canonical title."),
        ("## per-platform comparison", "MVP cross-platform final report must include the per-platform comparison section."),
        ("## mismatches", "MVP cross-platform final report must include mismatch reporting."),
        ("- result: `complete`", "MVP cross-platform final report must record a complete result."),
        ("- repox strict:", "MVP cross-platform final report must include RepoX gate status."),
        ("- auditx strict:", "MVP cross-platform final report must include AuditX gate status."),
        ("- testx:", "MVP cross-platform final report must include TestX gate status."),
        ("- cross-platform matrix:", "MVP cross-platform final report must include matrix status."),
    ):
        if token in final_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.platform_dependent_behavior_smell",
                severity="WARN",
                confidence=0.8,
                file_path=FINAL_REL,
                evidence=[message],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=[RULE_ID],
                related_paths=[FINAL_REL],
            )
        )

    return findings
