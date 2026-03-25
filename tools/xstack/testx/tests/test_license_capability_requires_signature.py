"""FAST test: license capability artifacts require a trusted signature."""

from __future__ import annotations


TEST_ID = "test_license_capability_requires_signature"
TEST_TAGS = ["fast", "omega", "trust", "license"]


def run(repo_root: str):
    from tools.xstack.testx.tests.trust_strict_testlib import build_report, case_by_id

    report = build_report(repo_root)
    case = case_by_id(report, "license_capability_requires_trusted_signature")
    details = dict(case.get("details") or {})
    if str(case.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "license capability signature gate no longer completes"}
    if str(details.get("unsigned_refusal_code", "")).strip() != "refusal.trust.signature_missing":
        return {"status": "fail", "message": "unsigned license capability refusal_code drifted"}
    if str(details.get("untrusted_refusal_code", "")).strip() != "refusal.trust.root_not_trusted":
        return {"status": "fail", "message": "untrusted license capability refusal_code drifted"}
    trusted_signers = list(details.get("trusted_signer_ids") or [])
    if "signer.fixture.official" not in trusted_signers:
        return {"status": "fail", "message": "trusted signer evidence is missing from the license capability case"}
    return {"status": "pass", "message": "license capability artifacts require a trusted signature"}
