import json
import subprocess
import sys
import unittest
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def run_validator(*extra_args: str) -> subprocess.CompletedProcess:
    root = repo_root()
    cmd = [
        sys.executable,
        str(root / "tools" / "validators" / "contracts" / "check_service_conformance.py"),
        "--repo-root",
        str(root),
        "--json",
        *extra_args,
    ]
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


class ServiceConformanceValidatorTests(unittest.TestCase):
    def test_service_conformance_fixtures_pass(self) -> None:
        result = run_validator("--strict", "--fixtures")
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["fixtures"]["status"], "pass")
        self.assertGreaterEqual(payload["fixtures"]["valid"], 1)
        self.assertGreaterEqual(payload["fixtures"]["invalid"], 1)

    def test_invalid_service_fixtures_exercise_errors(self) -> None:
        result = run_validator("--fixtures")
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        invalid_results = [
            item for item in payload["fixtures"]["fixtures"]
            if item["expected"] == "invalid"
        ]
        self.assertTrue(invalid_results)
        self.assertTrue(all(item["status"] == "pass" for item in invalid_results))
        self.assertTrue(all(item["errors"] > 0 for item in invalid_results))


if __name__ == "__main__":
    unittest.main()
