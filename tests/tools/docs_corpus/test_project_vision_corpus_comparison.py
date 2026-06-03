import tempfile
import unittest
from pathlib import Path

from tools.docs_corpus.compare_project_vision_corpus_variants import (
    count_shadowed_duplicates,
    extract_first_int,
    normalize_basename,
    parse_source_paths,
)


class ProjectVisionCorpusComparisonTests(unittest.TestCase):
    def test_extract_first_int_accepts_commas(self):
        text = "Human-readable sources selected: 2,500"
        self.assertEqual(extract_first_int([r"selected:\s*([0-9,]+)"], text), 2500)

    def test_parse_source_paths_from_bullets_and_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source_selection").mkdir()
            (root / "source_selection" / "SOURCE_PRIORITY_LIST.md").write_text(
                "- P1: `docs/archive/conversations/example_report.md`\n"
                "| Rank | Score | Bytes | Title | Path |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| 1 | 9 | 100 | Example | nested/other_report.txt |\n",
                encoding="utf-8",
            )
            (root / "source_selection" / "HUMAN_READABLE_SOURCE_SELECTION.md").write_text(
                "",
                encoding="utf-8",
            )
            self.assertEqual(
                parse_source_paths(root),
                [
                    "docs/archive/conversations/example_report.md",
                    "nested/other_report.txt",
                ],
            )

    def test_normalize_basename(self):
        self.assertEqual(normalize_basename("Some/Path/Report.MD"), "report.md")

    def test_count_shadowed_duplicates(self):
        text = "- `a.md` shadowed 2 duplicate block(s).\n- `b.md` shadowed 10 duplicate block(s)."
        self.assertEqual(count_shadowed_duplicates(text), 12)


if __name__ == "__main__":
    unittest.main()
