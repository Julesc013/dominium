from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/docs_corpus"))

import build_omnibus_v1 as v1  # noqa: E402


class OmnibusV1ToolTests(unittest.TestCase):
    def test_title_removes_version_suffix(self) -> None:
        self.assertEqual(v1.title_from_path("docs/archive/docs_corpus/_audit/DOCS_AUTHORITY_MAP_v0.md"), "Authority Map")

    def test_compact_metadata_removes_status_block(self) -> None:
        metadata, body = v1.compact_metadata("Status: DERIVED\nAuthority Class: advisory_synthesis\n\n# Body\nText\n")
        self.assertEqual(metadata["Status"], "DERIVED")
        self.assertNotIn("Status: DERIVED", body)
        self.assertIn("# Body", body)

    def test_reader_source_uses_human_headings(self) -> None:
        state = v1.create_state(ROOT)
        text = v1.build_reader_source(state)
        self.assertIn("## Current Project Picture", text)
        self.assertNotIn("## Source:", text)
        self.assertLessEqual(text.count("Status: DERIVED"), 1)

    def test_manifest_has_v1_style_profile(self) -> None:
        state = v1.create_state(ROOT)
        text = v1.build_manifest(state)
        self.assertIn("version: 1", text)
        self.assertIn('style_profile: "readability_v1"', text)
        self.assertIn('status: "DERIVED"', text)

    def test_latex_renders_semantic_emphasis(self) -> None:
        latex = v1.markdown_to_latex("This has **bold**, *italic*, <u>under</u>, `code`, and [link](https://example.com).")
        self.assertIn(r"\textbf{bold}", latex)
        self.assertIn(r"\emph{italic}", latex)
        self.assertIn(r"\uline{under}", latex)
        self.assertIn(r"\texttt{code}", latex)
        self.assertIn(r"\href", latex)


if __name__ == "__main__":
    unittest.main()
