"""FAST test: ARCH-AUDIT scans detect representative forbidden patterns."""

from __future__ import annotations

import json
import os
import tempfile


TEST_ID = "test_arch_audit_detects_forbidden_patterns"
TEST_TAGS = ["fast", "audit", "architecture"]


def _write(path: str, text: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def run(repo_root: str):
    del repo_root
    from tools.audit.arch_audit_common import scan_determinism, scan_renderer_truth_access, scan_truth_purity

    with tempfile.TemporaryDirectory(prefix="arch_audit_fixture_") as temp_root:
        _write(
            os.path.join(temp_root, "schemas", "universe_state.schema.json"),
            json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "sky_gradient": {"type": "object"},
                    },
                },
                indent=2,
                sort_keys=True,
            ),
        )
        _write(
            os.path.join(temp_root, "src", "client", "render", "renderers", "software_renderer.py"),
            "def render_snapshot():\n    return truth_model\n",
        )
        _write(
            os.path.join(temp_root, "src", "server", "server_boot.py"),
            "def boot():\n    return time.time()\n",
        )
        truth_report = scan_truth_purity(temp_root)
        renderer_report = scan_renderer_truth_access(temp_root)
        determinism_report = scan_determinism(temp_root)
        if int(truth_report.get("blocking_finding_count", 0) or 0) < 1:
            return {"status": "fail", "message": "truth purity scan failed to detect forbidden presentation field"}
        if int(renderer_report.get("blocking_finding_count", 0) or 0) < 1:
            return {"status": "fail", "message": "renderer truth scan failed to detect truth leak"}
        if int(determinism_report.get("blocking_finding_count", 0) or 0) < 1:
            return {"status": "fail", "message": "determinism scan failed to detect wallclock usage"}
    return {"status": "pass", "message": "ARCH-AUDIT scans detected representative forbidden patterns"}
