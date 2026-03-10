"""E406 missing endpoint descriptor smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E406_MISSING_ENDPOINT_DESCRIPTOR_SMELL"
REQUIRED_TOKENS = {
    "data/registries/product_registry.json": (
        '"product_id": "client"',
        '"product_id": "server"',
        '"product_id": "launcher"',
        '"product_id": "setup"',
        '"product_id": "tool.attach_console_stub"',
    ),
    "src/compat/capability_negotiation.py": (
        "build_default_endpoint_descriptor(",
        "product_rows_by_id(",
        "build_endpoint_descriptor(",
    ),
    "docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md": (
        "Every executable or attachable endpoint exposes a deterministic descriptor",
        "`product_id`",
        "`product_version`",
    ),
}


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    related_paths = sorted(REQUIRED_TOKENS.keys())
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.capability_negotiation.missing_endpoint_descriptor_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required endpoint-descriptor surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-ALL-PRODUCTS-HAVE-ENDPOINT-DESCRIPTOR"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.capability_negotiation.missing_endpoint_descriptor_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing endpoint-descriptor marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-ALL-PRODUCTS-HAVE-ENDPOINT-DESCRIPTOR"],
                    related_paths=related_paths,
                )
            )
    return findings
