import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools" / "docs_corpus"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_project_vision_corpus as pvc  # noqa: E402


class ProjectVisionCorpusTests(unittest.TestCase):
    def test_report_candidate_accepts_human_readable_report(self):
        path = Path("docs/archive/conversations/demo/demo__01_human_readable_report.md")
        self.assertTrue(pvc.is_human_source_candidate(path, Path("docs/archive/conversations")))

    def test_report_candidate_excludes_exports(self):
        path = Path("docs/archive/conversations/_exports/generated_report.md")
        self.assertFalse(pvc.is_human_source_candidate(path, Path("docs/archive/conversations")))

    def test_block_classification_detects_decision(self):
        text = "The conversation decided that renderer work must not own truth and should remain presentation only."
        self.assertEqual(pvc.classify_block(text), "decision")

    def test_theme_tags_detect_renderer_and_authority(self):
        text = "The renderer is presentation only, and authority must be checked by capability and law."
        tags = pvc.theme_tags_for(text)
        self.assertIn("ui_renderer_presentation", tags)
        self.assertIn("law_authority_refusal", tags)

    def test_clean_block_text_collapses_whitespace(self):
        self.assertEqual(pvc.clean_block_text("A\n\n  B\tC"), "A B C")


if __name__ == "__main__":
    unittest.main()
