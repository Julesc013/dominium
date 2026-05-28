import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "docs_corpus"))

import build_human_readable_book as human


class HumanReadableBookTests(unittest.TestCase):
    def test_machine_named_manifest_is_not_main_book_prose(self):
        self.assertTrue(human.is_machine_named("docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.md"))
        self.assertTrue(human.is_machine_named("docs/archive/docs_corpus/_audit/DOCS_CONTRADICTION_MATRIX_v0.md"))

    def test_priority_source_is_full_text(self):
        record = {
            "path": "docs/architecture/WHAT_THIS_IS.md",
            "extension": ".md",
            "first_heading": "What This Is",
            "authority_class": "architecture_current",
            "directory_family": "architecture",
            "size": 100,
            "is_text": True,
        }
        item = human.classify_record(record)
        self.assertEqual(item.disposition, "human_full_text")

    def test_machine_extension_is_index_only(self):
        record = {
            "path": "docs/example.json",
            "extension": ".json",
            "first_heading": "",
            "authority_class": "unknown",
            "directory_family": "other",
            "size": 100,
            "is_text": True,
        }
        item = human.classify_record(record)
        self.assertEqual(item.disposition, "machine_index_only")

    def test_book_chapter_contains_source_trail(self):
        text = human.chapter(
            "Example",
            1,
            "Focus.",
            "Current.",
            "Archive.",
            "Unresolved.",
            ["README.md"],
        )
        self.assertIn("Source trail:", text)
        self.assertIn("README.md", text)

    def test_compact_metadata_removes_header_block(self):
        metadata, body = human.compact_metadata("Status: DERIVED\nAuthority Class: advisory_synthesis\n\n# Title\nBody\n")
        self.assertEqual(metadata["Status"], "DERIVED")
        self.assertTrue(body.startswith("# Title"))

    def test_appendix_table_rendering_uses_row_cards(self):
        rendered = human.table_block_to_cards([
            "| Topic | Status |",
            "| --- | --- |",
            "| Authority | Advisory |",
        ])
        self.assertIn("row cards", rendered)
        self.assertIn("**Topic:** Authority", rendered)
        self.assertIn("**Status:** Advisory", rendered)

    def test_appendix_safe_markdown_closes_unbalanced_fences(self):
        rendered = human.appendix_safe_markdown("Intro\n```text\nunfinished\n")
        self.assertTrue(rendered.rstrip().endswith("```"))


if __name__ == "__main__":
    unittest.main()
