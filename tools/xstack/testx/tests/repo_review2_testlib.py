"""Helpers for REPO-REVIEW-2 TestX coverage."""

from __future__ import annotations

import os
import tempfile

from tools.review.repo_inventory_common import build_repo_inventory, scan_product_main_bypasses, unknown_inventory_entries
from tools.xstack.compatx.canonical_json import canonical_json_text


def build_report(repo_root: str) -> dict:
    return build_repo_inventory(repo_root)


def canonical_report_text(repo_root: str) -> str:
    return canonical_json_text(build_report(repo_root))


def unknown_entries(repo_root: str) -> list[dict]:
    return unknown_inventory_entries(build_report(repo_root))


def detect_bypass_in_fixture() -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="repo_review2_bypass_") as temp_root:
        rel_path = os.path.join(temp_root, "src", "server")
        os.makedirs(rel_path, exist_ok=True)
        with open(os.path.join(rel_path, "server_main.py"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(
                "\n".join(
                    (
                        "def main():",
                        "    return 0",
                        "",
                        'if __name__ == "__main__":',
                        "    raise SystemExit(main())",
                        "",
                    )
                )
            )
        return scan_product_main_bypasses(temp_root)
