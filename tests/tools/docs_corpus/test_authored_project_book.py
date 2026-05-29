import unittest

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools" / "docs_corpus"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_authored_project_book as authored  # noqa: E402


class AuthoredProjectBookTests(unittest.TestCase):
    def test_normalize_sentence_removes_evidence_and_paths(self):
        text = authored.normalize_sentence("EVC-00001 from docs/archive/conversations/foo.md says `truth` must not drift.")
        self.assertNotIn("EVC-", text)
        self.assertNotIn("docs/archive", text)
        self.assertIn("truth", text)

    def test_banned_heading_list_blocks_v2_scaffold(self):
        self.assertIn("Integrated Evidence", authored.BANNED_HEADINGS)
        self.assertIn("Source Trail", authored.BANNED_HEADINGS)

    def test_theme_count_and_title(self):
        self.assertGreaterEqual(len(authored.THEMES), 23)
        self.assertEqual(authored.TITLE, "Dominium Project Book")
        self.assertNotIn("v2", authored.TITLE.lower())

    def test_low_value_filters_paths_and_packets(self):
        self.assertTrue(authored.low_value_text("docs/archive/conversations/foo/bar_baz_qux.md"))
        self.assertTrue(authored.low_value_text("context transfer packet raw prompt"))
        self.assertFalse(authored.low_value_text("Deterministic replay requires stable authority boundaries."))

    def test_yaml_scalar_quotes_strings(self):
        self.assertEqual(authored.yaml_scalar("Dominium"), '"Dominium"')
        self.assertEqual(authored.yaml_scalar(True), "true")


if __name__ == "__main__":
    unittest.main()
