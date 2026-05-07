from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / ".aide/scripts/aide_lite.py"
SPEC = importlib.util.spec_from_file_location("aide_lite", MODULE_PATH)
aide_lite = importlib.util.module_from_spec(SPEC)
sys.modules["aide_lite"] = aide_lite
assert SPEC.loader is not None
SPEC.loader.exec_module(aide_lite)


class ExportImportTests(unittest.TestCase):
    def make_source_repo(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "source"
        root.mkdir()
        for rel in [*aide_lite.PORTABLE_SOURCE_FILES, *aide_lite.Q21_REQUIRED_FILES]:
            source = REPO_ROOT / rel
            if source.exists() and source.is_file():
                self.copy_file(source, root / rel)
        for directory in [*aide_lite.PORTABLE_SOURCE_DIRS, ".aide/import"]:
            source_root = REPO_ROOT / directory
            if not source_root.exists():
                continue
            for source in sorted(source_root.rglob("*")):
                if source.is_file():
                    self.copy_file(source, root / source.relative_to(REPO_ROOT))
        aide_lite.write_text(root / "README.md", "# Source Fixture\n")
        aide_lite.write_text(root / "AGENTS.md", "# Source Agents\n")
        aide_lite.write_text(root / ".gitignore", ".aide.local/\n.aide.local/**\n.env\n")
        return root

    def copy_file(self, source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())

    def build_pack(self, source_root: Path) -> Path:
        pack_root, report = aide_lite.build_export_pack(source_root)
        self.assertGreater(len(report["included_files"]), 20)
        self.assertEqual(report["boundary_violations"], [])
        return pack_root

    def test_export_policy_has_required_anchors(self) -> None:
        policy = aide_lite.read_text(REPO_ROOT / aide_lite.EXPORT_IMPORT_POLICY_PATH)
        for anchor in [
            "portable_pack_only",
            "no_external_repo_mutation",
            "no_network",
            "no_provider_calls",
            "aide-lite-pack-v0",
            "never_copy_aide_self_hosting_queue: true",
            "never_copy_aide_generated_context: true",
            "never_copy_aide_local_state: true",
            "never_copy_provider_credentials: true",
        ]:
            self.assertIn(anchor, policy)

    def test_export_includes_required_portable_files_and_manifest(self) -> None:
        source_root = self.make_source_repo()
        pack_root = self.build_pack(source_root)
        self.assertTrue((pack_root / "manifest.yaml").exists())
        self.assertTrue((pack_root / "checksums.json").exists())
        for rel in [
            "files/.aide/scripts/aide_lite.py",
            "files/.aide/policies/token-budget.yaml",
            "files/.aide/policies/export-import.yaml",
            "files/.aide/prompts/compact-task.md",
            "files/.aide/profile.template.yaml",
            "files/.aide/memory/project-state.template.md",
            "files/AGENTS.md.template",
        ]:
            self.assertTrue((pack_root / rel).exists(), rel)
        manifest = aide_lite.read_text(pack_root / "manifest.yaml")
        self.assertIn("included_files:", manifest)
        self.assertIn("excluded_classes:", manifest)
        self.assertIn("raw_prompt_storage: false", manifest)

    def test_export_excludes_source_state_and_generated_artifacts(self) -> None:
        source_root = self.make_source_repo()
        for rel in [
            ".aide/profile.yaml",
            ".aide/queue/index.yaml",
            ".aide/context/latest-task-packet.md",
            ".aide/reports/token-ledger.jsonl",
            ".aide/cache/latest-cache-keys.json",
            ".aide/routing/latest-route-decision.json",
            ".aide/gateway/latest-gateway-status.json",
            ".aide/providers/latest-provider-status.json",
            ".aide.local/state.json",
            ".env",
        ]:
            aide_lite.write_text(source_root / rel, "source-only\n")
        pack_root = self.build_pack(source_root)
        for rel in [
            "files/.aide/profile.yaml",
            "files/.aide/queue/index.yaml",
            "files/.aide/context/latest-task-packet.md",
            "files/.aide/reports/token-ledger.jsonl",
            "files/.aide/cache/latest-cache-keys.json",
            "files/.aide/routing/latest-route-decision.json",
            "files/.aide/gateway/latest-gateway-status.json",
            "files/.aide/providers/latest-provider-status.json",
            "files/.aide.local/state.json",
            "files/.env",
        ]:
            self.assertFalse((pack_root / rel).exists(), rel)

    def test_export_checksums_match_and_are_deterministic(self) -> None:
        source_root = self.make_source_repo()
        pack_root = self.build_pack(source_root)
        ok, problems = aide_lite.validate_pack_checksums(pack_root)
        self.assertTrue(ok, problems)
        first = aide_lite.read_text(pack_root / "checksums.json")
        self.build_pack(source_root)
        second = aide_lite.read_text(pack_root / "checksums.json")
        self.assertEqual(first, second)

    def test_import_dry_run_reports_without_writing(self) -> None:
        source_root = self.make_source_repo()
        pack_root = self.build_pack(source_root)
        target = source_root.parent / "target-dry-run"
        aide_lite.write_text(target / "README.md", "# Target\n")
        result = aide_lite.apply_import_pack(pack_root, target, dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertGreater(result["operation_count"], 10)
        self.assertFalse((target / ".aide").exists())

    def test_import_fixture_creates_templates_and_preserves_agents(self) -> None:
        source_root = self.make_source_repo()
        pack_root = self.build_pack(source_root)
        target = source_root.parent / "target"
        aide_lite.write_text(target / "README.md", "# Target\n")
        aide_lite.write_text(target / "AGENTS.md", "# Target Agents\n\nManual guidance.\n")
        result = aide_lite.apply_import_pack(pack_root, target, dry_run=False)
        self.assertFalse(result["conflicts"])
        agents = aide_lite.read_text(target / "AGENTS.md")
        self.assertIn("Manual guidance.", agents)
        self.assertIn("AIDE-PORTABLE:BEGIN", agents)
        for rel in [
            ".aide/profile.template.yaml",
            ".aide/profile.yaml",
            ".aide/memory/project-state.template.md",
            ".aide/memory/project-state.md",
            ".aide/memory/decisions.template.md",
            ".aide/memory/open-risks.template.md",
        ]:
            self.assertTrue((target / rel).exists(), rel)
        self.assertTrue(aide_lite.gitignore_has_local_state_rules(target))
        self.assertFalse((target / ".aide.local").exists())
        self.assertFalse((target / ".aide/queue/index.yaml").exists())
        self.assertFalse((target / aide_lite.LATEST_PACKET_PATH).exists())

    def test_imported_aide_lite_doctor_snapshot_and_pack_run(self) -> None:
        source_root = self.make_source_repo()
        pack_root = self.build_pack(source_root)
        target = source_root.parent / "target-smoke"
        aide_lite.write_text(target / "README.md", "# Target Smoke\n")
        aide_lite.apply_import_pack(pack_root, target, dry_run=False)
        script = target / ".aide/scripts/aide_lite.py"
        commands = [
            ["doctor"],
            ["snapshot"],
            ["pack", "--task", "Fixture target smoke task"],
        ]
        for command in commands:
            result = subprocess.run(
                [sys.executable, str(script), "--repo-root", str(target), *command],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((target / aide_lite.SNAPSHOT_PATH).exists())
        self.assertTrue((target / aide_lite.LATEST_PACKET_PATH).exists())

    def test_fake_secret_source_file_is_not_exported(self) -> None:
        source_root = self.make_source_repo()
        aide_lite.write_text(source_root / ".aide/prompts/compact-task.md", "api_key = \"abcdefghijklmnop\"\n")
        self.assertFalse(aide_lite.is_exportable_file(source_root, ".aide/prompts/compact-task.md"))
        pack_root = self.build_pack(source_root)
        self.assertFalse((pack_root / "files/.aide/prompts/compact-task.md").exists())


if __name__ == "__main__":
    unittest.main()
