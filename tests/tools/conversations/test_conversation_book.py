import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "tools" / "conversations"
sys.path.insert(0, str(TOOLS))

import build_conversation_book as book  # noqa: E402


class ConversationBookBuildTests(unittest.TestCase):
    def make_repo(self):
        temp = tempfile.TemporaryDirectory()
        repo = Path(temp.name)
        root = repo / book.CORPUS_ROOT
        root.mkdir(parents=True)
        chapters, appendices = book.default_chapters()
        for source_path in book.all_manifest_sources(chapters, appendices):
            path = root / source_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "# " + path.stem.replace("_", " ").title() + "\n\n"
                "Status: DERIVED\n"
                "Authority Class: advisory_only\n\n"
                "This source exists for the temporary book build.\n\n"
                "| Field | Value |\n| --- | --- |\n| Example | Dense row |\n",
                encoding="utf-8",
            )
        manifest = {
            "conversations": [
                {
                    "folder": "Sample_Conversation",
                    "likely_package_type": "conversation_handoff_export",
                    "completeness_status": "complete",
                    "source_file_count": 3,
                }
            ]
        }
        intake = root / "_intake"
        intake.mkdir(exist_ok=True)
        (intake / "corpus_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        reader = root / "_reader" / "by_chat"
        reader.mkdir(parents=True, exist_ok=True)
        (reader / "sample_conversation.md").write_text(
            "# Sample Conversation\n\n"
            "Source Folder: `docs/archive/conversations/Sample_Conversation/`\n\n"
            "## What This Conversation Was About\n"
            "A temporary sample reader page.\n\n"
            "## What Was Decided\n"
            "Nothing was promoted.\n",
            encoding="utf-8",
        )
        return temp, repo

    def test_source_book_builds_without_renderers(self):
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        result = book.build_book(repo, render_outputs=False)
        self.assertEqual(result["renderer"], "custom_html_latex_ooxml_epub")
        self.assertTrue((repo / book.BOOK_DIR / "BOOK_MANIFEST.yml").exists())
        self.assertTrue((repo / book.BOOK_DIR / "chapters" / "00_front_matter.md").exists())
        self.assertTrue((repo / book.EXPORTS_DIR / f"{book.BUILD_REPORT_BASENAME}.md").exists())
        self.assertIn("_synthesis/READ_THIS_FIRST_v0.md", book.parse_manifest_paths((repo / book.BOOK_DIR / "BOOK_MANIFEST.yml").read_text(encoding="utf-8")))
        errors, warnings = book.validate_book_sources(repo, result["included"], result["outputs"])
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_summary_table_mode_limits_rows(self):
        text = "# Title\n\n| A | B |\n| --- | --- |\n" + "\n".join(f"| {i} | row |" for i in range(30))
        summarized = book.summarize_table_blocks(text, max_rows=3)
        self.assertIn("Dense table summarized for the reader edition", summarized)
        self.assertNotIn("| 29 | row |", summarized)


if __name__ == "__main__":
    unittest.main()
