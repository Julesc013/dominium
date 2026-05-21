#!/usr/bin/env python3
"""Contract test wrapper for composition resolver validation."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


class CompositionResolverContractTests(unittest.TestCase):
    def test_composition_resolver_fixtures(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        validator = repo_root / "tools/validators/contracts/check_composition_resolver.py"
        completed = subprocess.run(
            [
                sys.executable,
                str(validator),
                "--repo-root",
                str(repo_root),
                "--strict",
                "--fixtures",
            ],
            cwd=str(repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
