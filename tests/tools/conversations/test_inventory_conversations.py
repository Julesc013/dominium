import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "tools" / "conversations"
sys.path.insert(0, str(TOOLS))

import conversation_corpus as corpus  # noqa: E402


class InventoryConversationTests(unittest.TestCase):
    def make_repo(self):
        temp = tempfile.TemporaryDirectory()
        repo = Path(temp.name)
        root = repo / "docs" / "archive" / "conversations"
        chat = root / "Sample_Conversation"
        chat.mkdir(parents=True)
        (chat / "sample__manifest.md").write_text("# Manifest\n", encoding="utf-8")
        (chat / "sample__01_full_chat_report.md").write_text(
            "# Full Chat Report - Sample Conversation\n\n"
            "## 1. One-Page Orientation\n\n"
            "This chat was about deterministic tooling and a future validation task.\n\n"
            "FACT: The archive remains advisory only.\n"
            "UNCERTAIN / UNVERIFIED: Implementation state was not checked.\n",
            encoding="utf-8",
        )
        (chat / "sample__02_spec_sheet.yaml").write_text("title: Sample\n", encoding="utf-8")
        managed = root / "_reader" / "by_chat"
        managed.mkdir(parents=True)
        (managed / "ignored.md").write_text("generated\n", encoding="utf-8")
        return temp, repo

    def test_manifest_excludes_generated_management_dirs(self):
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        manifest, conversations = corpus.build_manifest(repo)
        self.assertEqual(manifest["summary"]["conversation_count"], 1)
        self.assertEqual(conversations[0].folder, "Sample_Conversation")
        self.assertEqual(conversations[0].completeness_status, "complete")
        self.assertNotIn("_reader", [c.folder for c in conversations])

    def test_phase_outputs_validate(self):
        temp, repo = self.make_repo()
        self.addCleanup(temp.cleanup)
        corpus.write_all(repo, ["phase1", "phase2", "phase3", "phase4", "acceptance", "synthesis"])
        errors = corpus.validate_outputs(repo)
        self.assertEqual(errors, [])
        data = json.loads((repo / "docs/archive/conversations/_intake/corpus_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["summary"]["source_file_count"], 3)
        self.assertTrue((repo / "docs/archive/conversations/_reader/by_chat/sample_conversation.md").exists())
        self.assertTrue((repo / "docs/archive/conversations/_audit/INTAKE_ACCEPTANCE_REVIEW.md").exists())
        self.assertTrue((repo / "docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md").exists())


if __name__ == "__main__":
    unittest.main()
