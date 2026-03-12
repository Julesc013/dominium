"""E446 MVP stress gate missing smell analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E446_STRESS_GATE_MISSING_SMELL"
RULE_ID = "INV-MVP-STRESS-MUST-PASS-BEFORE-RELEASE"
DOCTRINE_REL = "docs/mvp/MVP_STRESS_GATE.md"
HASHES_REL = "build/mvp/mvp_stress_hashes.json"
REPORT_REL = "build/mvp/mvp_stress_report.json"
PROOF_REL = "build/mvp/mvp_stress_proof_report.json"
BASELINE_REL = "data/regression/mvp_stress_baseline.json"
FINAL_REL = "docs/audit/MVP_STRESS_FINAL.md"
TEST_RELS = (
    "tools/xstack/testx/tests/test_stress_orchestrator_order_deterministic.py",
    "tools/xstack/testx/tests/test_proof_validation_passes.py",
    "tools/xstack/testx/tests/test_cross_thread_hash_match.py",
    "tools/xstack/testx/tests/test_stress_hashes_match_baseline.py",
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
        category="release.stress_gate_missing_smell",
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
        (DOCTRINE_REL, "MVP stress doctrine is missing."),
        ("tools/mvp/tool_run_all_stress.py", "MVP stress orchestrator is missing."),
        ("tools/mvp/tool_verify_proofs.py", "MVP stress proof verifier is missing."),
        (HASHES_REL, "MVP stress hash artifact is missing."),
        (REPORT_REL, "MVP stress report artifact is missing."),
        (PROOF_REL, "MVP stress proof report artifact is missing."),
        (BASELINE_REL, "MVP stress regression baseline is missing."),
        (FINAL_REL, "MVP stress final audit report is missing."),
    ) + tuple((rel, "MVP stress TestX artifact is missing.") for rel in TEST_RELS)
    for rel, message in required_files:
        abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(_missing_file_finding(rel, message))

    doctrine_text = _read_text(os.path.join(repo_root, DOCTRINE_REL.replace("/", os.sep))).lower()
    for token, message in (
        ("mvp-stress-regression-update", "MVP stress doctrine must declare the regression update tag."),
        ("canonical gate seed is `70101`", "MVP stress doctrine must pin the canonical gate seed."),
        ("proof anchors stable across runs", "MVP stress doctrine must declare proof-anchor stability checks."),
        ("negotiation records stable", "MVP stress doctrine must declare negotiation-record stability checks."),
        ("deterministic degrade behavior only", "MVP stress doctrine must declare deterministic-only degrade behavior."),
    ):
        if token in doctrine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.stress_gate_missing_smell",
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
        findings.append(_missing_file_finding(REPORT_REL, "MVP stress report must be valid JSON."))
    else:
        if str(report_payload.get("gate_id", "")).strip() != "mvp.stress.gate.v1":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.stress_gate_missing_smell",
                    severity="RISK",
                    confidence=0.93,
                    file_path=REPORT_REL,
                    evidence=["MVP stress report must record gate_id mvp.stress.gate.v1."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )
        assertions = dict(report_payload.get("assertions") or {})
        for key in ("all_suites_passed", "cross_thread_hash_match", "no_unexpected_refusals", "suite_order_deterministic"):
            if bool(assertions.get(key, False)):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.stress_gate_missing_smell",
                    severity="RISK",
                    confidence=0.93,
                    file_path=REPORT_REL,
                    evidence=["MVP stress report assertion '{}' must pass before release.".format(key)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[REPORT_REL],
                )
            )

    proof_payload, proof_error = _load_json(os.path.join(repo_root, PROOF_REL.replace("/", os.sep)))
    if proof_error:
        findings.append(_missing_file_finding(PROOF_REL, "MVP stress proof report must be valid JSON."))
    else:
        if str(proof_payload.get("result", "")).strip() != "complete":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.stress_gate_missing_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=PROOF_REL,
                    evidence=["MVP stress proof report must record result=complete before release."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[PROOF_REL],
                )
            )
        checks = dict(proof_payload.get("checks") or {})
        for key in (
            "gate_report_complete",
            "proof_anchors_stable",
            "negotiation_records_stable",
            "contract_bundle_pinned",
            "pack_locks_stable",
            "compaction_replay_matches",
            "cross_thread_hash_match",
            "no_unexpected_refusals",
        ):
            if bool(checks.get(key, False)):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.stress_gate_missing_smell",
                    severity="RISK",
                    confidence=0.91,
                    file_path=PROOF_REL,
                    evidence=["MVP stress proof check '{}' must pass before release.".format(key)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[PROOF_REL],
                )
            )

    baseline_payload, baseline_error = _load_json(os.path.join(repo_root, BASELINE_REL.replace("/", os.sep)))
    if baseline_error:
        findings.append(_missing_file_finding(BASELINE_REL, "MVP stress baseline must be valid JSON."))
    else:
        update_policy = dict(baseline_payload.get("update_policy") or {})
        if str(update_policy.get("required_commit_tag", "")).strip() != "MVP-STRESS-REGRESSION-UPDATE":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.stress_gate_missing_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=BASELINE_REL,
                    evidence=["MVP stress baseline must require MVP-STRESS-REGRESSION-UPDATE for updates."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="DOC_FIX",
                    related_invariants=[RULE_ID],
                    related_paths=[BASELINE_REL],
                )
            )
        if not isinstance(baseline_payload.get("cross_thread_hashes"), dict) or not baseline_payload.get("cross_thread_hashes"):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.stress_gate_missing_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=BASELINE_REL,
                    evidence=["MVP stress baseline must pin cross_thread_hashes."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[BASELINE_REL],
                )
            )
        pack_lock_hashes = baseline_payload.get("pack_lock_hashes")
        if not isinstance(pack_lock_hashes, dict) or not str(dict(pack_lock_hashes).get("runtime", "")).strip():
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="release.stress_gate_missing_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=BASELINE_REL,
                    evidence=["MVP stress baseline must pin pack_lock_hashes.runtime."],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[BASELINE_REL],
                )
            )

    final_text = _read_text(os.path.join(repo_root, FINAL_REL.replace("/", os.sep))).lower()
    for token, message in (
        ("# mvp stress final", "MVP stress final report must declare the canonical title."),
        ("## run summary", "MVP stress final report must include a run summary section."),
        ("## hashes", "MVP stress final report must include a hashes section."),
        ("## degradations", "MVP stress final report must include a degradations section."),
        ("## gates", "MVP stress final report must include a gates section."),
        ("## proof checks", "MVP stress final report must include a proof checks section."),
        ("- result: `complete`", "MVP stress final report must record a complete stress result."),
        ("- repox strict:", "MVP stress final report must include RepoX gate status."),
        ("- auditx strict:", "MVP stress final report must include AuditX gate status."),
        ("- testx:", "MVP stress final report must include TestX gate status."),
        ("- stress orchestrator:", "MVP stress final report must include stress orchestrator gate status."),
    ):
        if token in final_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.stress_gate_missing_smell",
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
