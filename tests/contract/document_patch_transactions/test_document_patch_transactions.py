from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = REPO_ROOT / "tests" / "contract" / "document_patch_transactions" / "fixtures"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.document.patch_transaction import (  # noqa: E402
    apply_patch_transaction,
    document_content_hash,
    validate_patch_transaction,
)


def load_case(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


class DocumentPatchTransactionTests(unittest.TestCase):
    def test_valid_patch_transaction_applies_to_content_only(self) -> None:
        case = load_case("valid_patch_case.json")
        original_document = copy.deepcopy(case["document"])

        result = apply_patch_transaction(case["document"], case["transaction"])

        self.assertEqual(result.status, "ok")
        self.assertEqual(result.findings, ())
        self.assertEqual(result.applied_operations, 5)
        self.assertEqual(result.before_hash, case["transaction"]["expected_content_hash"])
        self.assertEqual(result.after_hash, case["expected_after_hash"])
        self.assertIsNotNone(result.document)
        assert result.document is not None
        self.assertEqual(result.document["content"], case["expected_content"])
        self.assertEqual(result.document["preserved_unknown"], {"kept": True})
        self.assertEqual(case["document"], original_document)
        self.assertEqual(document_content_hash(result.document), case["expected_after_hash"])

    def test_validate_patch_transaction_reports_no_findings_for_valid_case(self) -> None:
        case = load_case("valid_patch_case.json")

        findings = validate_patch_transaction(case["document"], case["transaction"])

        self.assertEqual(findings, ())

    def test_content_hash_mismatch_refuses_atomically(self) -> None:
        case = load_case("invalid_hash_case.json")

        result = apply_patch_transaction(case["document"], case["transaction"])

        self.assertEqual(result.status, "refused")
        self.assertIsNone(result.document)
        self.assertEqual(result.applied_operations, 0)
        self.assertEqual({finding.code for finding in result.findings}, {"content_hash_mismatch"})
        self.assertEqual(case["document"]["content"]["title"], "Draft")

    def test_missing_parent_refuses_without_implicit_creation(self) -> None:
        case = load_case("invalid_parent_case.json")

        result = apply_patch_transaction(case["document"], case["transaction"])

        self.assertEqual(result.status, "refused")
        self.assertIsNone(result.document)
        self.assertEqual(result.applied_operations, 0)
        self.assertEqual({finding.code for finding in result.findings}, {"parent_path_missing"})
        self.assertNotIn("missing", case["document"]["content"]["meta"])

    def test_schema_version_mismatch_refuses_without_migration(self) -> None:
        case = load_case("invalid_schema_version_case.json")

        result = apply_patch_transaction(case["document"], case["transaction"])

        self.assertEqual(result.status, "refused")
        self.assertIsNone(result.document)
        self.assertEqual({finding.code for finding in result.findings}, {"schema_version_mismatch"})

    def test_document_patch_transaction_validator_passes_fixtures(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "tools" / "validators" / "contracts" / "check_document_patch_transactions.py"),
                "--repo-root",
                str(REPO_ROOT),
                "--strict",
                "--fixtures",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("document_patch_transactions: pass", result.stdout)
        self.assertIn("fixtures: pass", result.stdout)


if __name__ == "__main__":
    unittest.main()
