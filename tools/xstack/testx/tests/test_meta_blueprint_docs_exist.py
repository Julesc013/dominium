"""FAST test: Π-0 blueprint docs exist and contain the expected anchor sections."""

from __future__ import annotations


TEST_ID = "test_meta_blueprint_docs_exist"
TEST_TAGS = ["fast", "pi", "blueprint", "docs"]


def run(repo_root: str):
    from tools.xstack.testx.tests.meta_blueprint_testlib import committed_docs

    docs = committed_docs(repo_root)
    required_markers = {
        "docs/archive/blueprint/META_BLUEPRINT_INDEX.md": "Best Practices to Borrow and Adapt",
        "docs/archive/blueprint/META_BLUEPRINT_SUMMARY.md": "Innovation Angle",
        "docs/archive/blueprint/RUNTIME_ARCHITECTURE_DIAGRAM.md": "Layered Diagram",
        "docs/archive/blueprint/REPOSITORY_GOVERNANCE_DIAGRAM.md": "Governance Diagram",
        "docs/archive/blueprint/DISTRIBUTION_AND_ARCHIVE_DIAGRAM.md": "Distribution and Archive Flow",
        "docs/archive/blueprint/LIVE_OPERATIONS_DIAGRAM.md": "Future Ζ Capability Groups",
        "docs/archive/blueprint/SERIES_DEPENDENCY_MAP.md": "Series Table",
        "docs/archive/blueprint/CAPABILITY_LADDER.md": "Level 0 - Frozen MVP foundations",
        "docs/archive/blueprint/FOUNDATION_READINESS_MATRIX.md": "Readiness Table",
        "docs/archive/blueprint/PIPE_DREAMS_MATRIX.md": "Advanced Concepts",
        "docs/archive/blueprint/SNAPSHOT_MAPPING_NOTES.md": "Final Mapping Pass Requirements",
        "docs/archive/audit/PI_0_FINAL.md": "Generated Artifacts",
    }
    for rel_path, marker in required_markers.items():
        text = str(docs.get(rel_path, "")).strip()
        if not text:
            return {"status": "fail", "message": f"missing required blueprint doc '{rel_path}'"}
        if marker not in text:
            return {"status": "fail", "message": f"blueprint doc '{rel_path}' missing marker '{marker}'"}
    return {"status": "pass", "message": "Π-0 blueprint docs exist and expose the expected anchor sections"}
