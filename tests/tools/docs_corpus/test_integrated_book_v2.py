import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "docs_corpus"))

import build_human_readable_book as human
import build_integrated_book_v2 as integrated


class IntegratedBookV2Tests(unittest.TestCase):
    def make_source(self, path="docs/archive/conversations/example_reader_brief.md"):
        return human.SourceItem(
            path=path,
            disposition="human_full_text",
            reason="test source",
            title="Example Source",
            authority_class="conversation_advisory",
            family="conversation_corpus",
            size=100,
            extension=".md",
        )

    def test_claim_type_detects_decision(self):
        claim = integrated.classify_claim_type("The conversation decided that Workbench should remain a governed operator surface.")
        self.assertEqual(claim, "decision")

    def test_topic_tags_detect_authority_and_workbench(self):
        tags = integrated.topic_tags_for("Workbench must not bypass authority or law.", self.make_source())
        self.assertIn("workbench", tags)
        self.assertIn("authority", tags)

    def test_card_maps_to_relevant_chapters(self):
        item = self.make_source()
        card = integrated.card_from_unit("EVC-00001", item, "Workbench must remain governed by authority law and explicit refusal.", 1)
        self.assertTrue(card.applies_to_chapters)
        self.assertIn("workbench", card.topic_tags)

    def test_boilerplate_report_counts_removed_patterns(self):
        report = integrated.boilerplate_report("This chapter is part of the synthesized reader", "Integrated evidence only")
        self.assertIn("v1 occurrences 1", report)
        self.assertIn("v2 occurrences 0", report)

    def test_yaml_cards_include_required_fields(self):
        item = self.make_source()
        card = integrated.card_from_unit("EVC-00001", item, "No silent fallback is allowed.", 1)
        text = integrated.cards_yaml([card])
        self.assertIn("card_id:", text)
        self.assertIn("claim_type:", text)
        self.assertIn("source_path:", text)


if __name__ == "__main__":
    unittest.main()
