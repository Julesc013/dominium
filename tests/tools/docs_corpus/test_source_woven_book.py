import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools" / "docs_corpus"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_human_readable_book as human  # noqa: E402
import build_source_woven_book as woven  # noqa: E402


class SourceWovenBookTests(unittest.TestCase):
    def test_clean_source_text_removes_paths_and_evidence_ids(self):
        text = "EVC-00012 says docs/archive/conversations/demo/file.md owns the point."
        cleaned = woven.clean_source_text(text)
        self.assertNotIn("EVC-", cleaned)
        self.assertNotIn("docs/archive", cleaned)
        self.assertIn("referenced source", cleaned)

    def test_chapter_architecture_has_clean_title_and_no_version(self):
        self.assertEqual(woven.TITLE, "Dominium Source-Woven Project Book")
        self.assertNotRegex(woven.TITLE.lower(), r"\bv[23]\b")
        self.assertGreaterEqual(len(woven.CHAPTERS), 23)

    def test_banned_patterns_include_prior_machine_headings(self):
        self.assertIn("Integrated Evidence", woven.BANNED_PATTERNS)
        self.assertIn("Source Trail", woven.BANNED_PATTERNS)
        self.assertIn("EVC-", woven.BANNED_PATTERNS)

    def test_split_semantic_blocks_keeps_list_together(self):
        source = "# Test\n\nA short introduction that should form one paragraph block with enough text to pass the filter.\n\n- first coherent item with enough detail about determinism, authority, and source weaving to remain together\n- second coherent item with enough detail about archive context, queue boundaries, and review discipline\n"
        blocks = woven.split_semantic_blocks(source)
        kinds = [kind for _heading, _text, kind in blocks]
        self.assertIn("paragraph", kinds)
        self.assertIn("list", kinds)

    def test_candidate_chapters_routes_renderer_to_chapter_11(self):
        item = human.SourceItem(
            path="docs/archive/conversations/demo/ui_renderer_human_readable_report.md",
            disposition="human_full_text",
            reason="test",
            title="Renderer Discussion",
            extension=".md",
        )
        chapters = woven.candidate_chapters(["renderer"], item)
        self.assertEqual(chapters[0], 11)


if __name__ == "__main__":
    unittest.main()
