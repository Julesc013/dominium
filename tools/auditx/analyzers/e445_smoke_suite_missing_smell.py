"""E445 MVP smoke suite missing smell analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E445_SMOKE_SUITE_MISSING_SMELL"
RULE_ID = "INV-MVP-SMOKE-MUST-PASS-BEFORE-RELEASE"
DOCTRINE_REL = "docs/mvp/MVP_SMOKE_SUITE.md"
HASHES_REL = "build/mvp/mvp_smoke_hashes.json"
REPORT_REL = "build/mvp/mvp_smoke_report.json"
BASELINE_REL = "data/regression/mvp_smoke_baseline.json"
FINAL_REL = "docs/audit/MVP_SMOKE_FINAL.md"
TEST_RELS = (
    "tools/xstack/testx/tests/test_smoke_scenario_deterministic.py",
    "tools/xstack/testx/tests/test_smoke_harness_passes.py",
    "tools/xstack/testx/tests/test_replay_bundle_validates.py",
    "tools/xstack/testx/tests/test_smoke_hashes_match_baseline.py",
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
        category="release.smoke_suite_missing_smell",
        severity="RISK",
        confidence=0.92,
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
        (DOCTRINE_REL, "MVP smoke doctrine is missing."),
        ("tools/mvp/tool_generate_mvp_smoke.py", "MVP smoke scenario generator is missing."),
        ("tools/mvp/tool_run_mvp_smoke.py", "MVP smoke harness is missing."),
        (HASHES_REL, "MVP smoke expected-hash artifact is missing."),
        (REPORT_REL, "MVP smoke report artifact is missing."),
        (BASELINE_REL, "MVP smoke regression baseline is missing."),
        (FINAL_REL, "MVP smoke final audit report is missing."),
    ) + tuple((rel, "MVP smoke TestX artifact is missing.") for rel in TEST_RELS)
    for rel, message in required_files:
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(_missing_file_finding(rel, message))

    doctrine_text = _read_text(os.path.join(repo_root, DOCTRINE_REL.replace("/", os.sep))).lower()
    for token, message in (
        ("mvp-smoke-regression-update", "MVP smoke doctrine must declare the regression update tag."),
        ("default smoke seed is `456`", "MVP smoke doctrine must pin the canonical smoke seed."),
        ("curated verification `pack_lock_hash`", "MVP smoke doctrine must record the curated verification pack lock."),
        ("smoke runtime `pack_lock_hash`", "MVP smoke doctrine must record the smoke runtime pack lock."),
    ):
        if token in doctrine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.smoke_suite_missing_smell",
                severity="WARN",
                confidence=0.8,
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
        findings.append(_missing_file_finding(REPORT_REL, "MVP smoke report must be valid JSON."))
    else:
        if str(report_payload.get("result", "")).strip() != "complete":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.smoke_suite_missing_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=REPORT_REL,
                    evidence=["MVP smoke report must record result=complete before release."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )

    baseline_payload, baseline_error = _load_json(os.path.join(repo_root, BASELINE_REL.replace("/", os.sep)))
    if baseline_error:
        findings.append(_missing_file_finding(BASELINE_REL, "MVP smoke baseline must be valid JSON."))
    else:
        update_policy = dict(baseline_payload.get("update_policy") or {})
        if str(update_policy.get("required_commit_tag", "")).strip() != "MVP-SMOKE-REGRESSION-UPDATE":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.smoke_suite_missing_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=BASELINE_REL,
                    evidence=["MVP smoke baseline must require MVP-SMOKE-REGRESSION-UPDATE for updates."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=[RULE_ID],
                    related_paths=[BASELINE_REL],
                )
            )
        proof_anchor_hashes = baseline_payload.get("proof_anchor_hashes")
        if not isinstance(proof_anchor_hashes, dict) or not proof_anchor_hashes:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.smoke_suite_missing_smell",
                    severity="RISK",
                    confidence=0.89,
                    file_path=BASELINE_REL,
                    evidence=["MVP smoke baseline must pin proof_anchor_hashes by tick."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[BASELINE_REL],
                )
            )

    final_text = _read_text(os.path.join(repo_root, FINAL_REL.replace("/", os.sep))).lower()
    for token, message in (
        ("# mvp smoke final", "MVP smoke final report must declare the canonical title."),
        ("## run summary", "MVP smoke final report must include a run summary section."),
        ("## hashes", "MVP smoke final report must include a hashes section."),
        ("## degradations", "MVP smoke final report must include a degradations section."),
        ("## gates", "MVP smoke final report must include a gates section."),
        ("- result: `complete`", "MVP smoke final report must record a complete smoke result."),
        ("- repox strict:", "MVP smoke final report must include RepoX gate status."),
        ("- auditx strict:", "MVP smoke final report must include AuditX gate status."),
        ("- testx:", "MVP smoke final report must include TestX gate status."),
        ("- smoke harness:", "MVP smoke final report must include smoke harness gate status."),
    ):
        if token in final_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.smoke_suite_missing_smell",
                severity="WARN",
                confidence=0.78,
                file_path=FINAL_REL,
                evidence=[message],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=[RULE_ID],
                related_paths=[FINAL_REL],
            )
        )

    return findings
