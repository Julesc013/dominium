import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "tools" / "conversations"
sys.path.insert(0, str(TOOLS))

import conversation_corpus as corpus  # noqa: E402


class ConversationOutputValidationTests(unittest.TestCase):
    def test_extract_lines_skips_tables_and_headings(self):
        text = "\n".join(
            [
                "| Field | Value |",
                "| Decision | This table row should be ignored |",
                "## Decision Heading",
                "FACT: This archived claim should be kept for review.",
                "UNCERTAIN / UNVERIFIED: This needs verification.",
            ]
        )
        facts = corpus.extract_lines(text, ["FACT:", "Decision"], limit=5)
        self.assertEqual(facts, ["FACT: This archived claim should be kept for review."])

    def test_ascii_text_normalizes_common_punctuation(self):
        self.assertEqual(corpus.ascii_text("A \u2192 B \u2014 C"), "A -> B - C")

    def test_slugify_is_stable(self):
        self.assertEqual(corpus.slugify("Dominium Architecture IV"), "dominium_architecture_iv")

    def test_markdown_link_targets_ignore_external_links(self):
        text = "[local](docs/example.md) [web](https://example.invalid) [anchor](#local)"
        self.assertEqual(list(corpus.markdown_link_targets(text)), ["docs/example.md"])


if __name__ == "__main__":
    unittest.main()
