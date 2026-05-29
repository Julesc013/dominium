import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools" / "docs_corpus"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_conversation_reports_anthology as anthology  # noqa: E402


class ConversationReportsAnthologyTests(unittest.TestCase):
    def test_candidate_selection_accepts_human_report_names(self):
        path = Path("docs/archive/conversations/demo/demo__01_human_readable_report.md")
        self.assertTrue(anthology.is_candidate(path))

    def test_candidate_selection_excludes_generated_reader_root(self):
        path = Path("docs/archive/conversations/_reader/by_chat/demo.md")
        self.assertFalse(anthology.is_candidate(path))

    def test_mobile_latex_uses_dark_ragged_no_hyphen_style(self):
        latex = anthology.mobile_latex("# Title\n\n## Chapter\n\nText", "pdflatex")
        self.assertIn("\\pagecolor{MobileDarkBg}", latex)
        self.assertIn("\\raggedright", latex)
        self.assertIn("\\hyphenpenalty=10000", latex)
        self.assertIn("\\setcounter{tocdepth}{0}", latex)

    def test_mobile_markdown_preserves_report_headings_below_conversation(self):
        prepared = anthology.prepare_mobile_markdown(
            "# Dominium Conversation Human-Readable Reports Anthology\n\n"
            "# Conversation Group\n\n"
            "## Report Title\n\n"
            "### Original Source Heading\n"
        )
        self.assertNotIn("# Dominium Conversation Human-Readable Reports Anthology", prepared)
        self.assertIn("# Conversation Group", prepared)
        self.assertIn("## Report Title", prepared)
        self.assertIn("### Original Source Heading", prepared)

    def test_regular_latex_suppresses_hyphenation(self):
        latex = anthology.regular_latex("# Title\n\nText", "pdflatex")
        self.assertIn("a4paper", latex)
        self.assertIn("\\raggedright", latex)
        self.assertIn("\\hyphenpenalty=10000", latex)


if __name__ == "__main__":
    unittest.main()
