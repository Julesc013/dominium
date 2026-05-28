from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/docs_corpus"))

import build_omnibus_pdf as omnibus  # noqa: E402


class OmnibusPdfToolTests(unittest.TestCase):
    def test_required_inputs_are_declared(self) -> None:
        self.assertIn("docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json", omnibus.REQUIRED_INPUTS)
        self.assertIn("AGENTS.md", omnibus.REQUIRED_INPUTS)

    def test_manifest_loading_and_selection(self) -> None:
        summary, records = omnibus.load_manifest(ROOT)
        self.assertGreater(summary["file_count"], 0)
        selection = omnibus.select_sources(ROOT, records)
        self.assertGreater(len(selection.full_text), 0)
        self.assertGreater(len(selection.manifest_only), 0)
        self.assertNotIn("docs/archive/docs_corpus/_intake/DOCS_CORPUS_MANIFEST.json", selection.full_text)

    def test_demote_headings(self) -> None:
        source = "# One\n## Two\nplain"
        result = omnibus.demote_headings(source, levels=2)
        self.assertIn("### One", result)
        self.assertIn("#### Two", result)

    def test_manifest_output_contains_non_promotion_fields(self) -> None:
        state = omnibus.create_state(ROOT)
        text = omnibus.build_manifest(state)
        self.assertIn('status: "DERIVED"', text)
        self.assertIn('promotion_status: "not_promoted"', text)
        self.assertIn('output_mode: "single_pdf"', text)


if __name__ == "__main__":
    unittest.main()
