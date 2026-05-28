from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/docs_corpus"))

import docs_corpus  # noqa: E402


class DocsCorpusToolTests(unittest.TestCase):
    def test_metadata_header_parsing(self) -> None:
        text = """Status: CANONICAL
Last Reviewed: 2026-05-28
Supersedes: old.md
Stability: stable

# Example
"""
        metadata = docs_corpus.metadata_from_text(text)
        self.assertEqual(metadata["Status"], "CANONICAL")
        self.assertEqual(metadata["Supersedes"], "old.md")

    def test_path_authority_classification(self) -> None:
        self.assertEqual(docs_corpus.path_family("docs/canon/constitution_v1.md"), "canon")
        self.assertEqual(
            docs_corpus.authority_class("docs/canon/constitution_v1.md", "canon", {"Status": "CANONICAL"}, True),
            "canonical",
        )
        self.assertEqual(docs_corpus.path_family("docs/archive/conversations/_wiki/index.md"), "conversation_corpus")
        self.assertEqual(
            docs_corpus.authority_class("docs/archive/conversations/_wiki/index.md", "conversation_corpus", {"Status": "DERIVED"}, True),
            "derived_synthesis",
        )

    def test_binary_detection_uses_extension_and_null_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            png = root / "image.png"
            png.write_bytes(b"\x89PNG\r\n")
            txt = root / "file.md"
            txt.write_text("# Heading\n", encoding="utf-8")
            nul = root / "blob"
            nul.write_bytes(b"abc\x00def")

            self.assertTrue(docs_corpus.is_binary_path(png))
            self.assertFalse(docs_corpus.is_binary_path(txt))
            self.assertTrue(docs_corpus.is_binary_path(nul))

    def test_book_manifest_path_parser(self) -> None:
        text = """outputs:
    - _exports/example.pdf
source_reports_included:
    - _audit/report.md
source_reports_excluded:
  - path: "_generated/**"
"""
        paths = docs_corpus.parse_book_manifest_paths(text)
        self.assertIn("_exports/example.pdf", paths)
        self.assertIn("_audit/report.md", paths)
        self.assertIn("_generated/**", paths)

    def test_manifest_json_is_parseable(self) -> None:
        record = docs_corpus.FileRecord(
            path="docs/example.md",
            parent="docs",
            directory_family="other",
            extension=".md",
            size=10,
            sha256="0" * 64,
            is_text=True,
            is_binary=False,
            first_heading="Example",
            header_preview=["Status: DERIVED"],
            metadata={"Status": "DERIVED"},
            inferred_document_family="other",
            initial_document_class="unknown",
            authority_class="unknown_or_unclassified",
            freshness="unclear",
            promotion_role="unknown",
            book_role="summarized_reader",
            authority_risk="unknown",
            archive_family="not_archive",
            warnings=[],
        )
        data = docs_corpus.CorpusData(repo_root=ROOT, commit="abc1234", branch="main", files=[record])
        payload = json.loads(docs_corpus.manifest_json(data))
        self.assertEqual(payload["summary"]["file_count"], 1)
        self.assertEqual(payload["files"][0]["path"], "docs/example.md")


if __name__ == "__main__":
    unittest.main()
