"""E414 missing pack compatibility manifest smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E414_MISSING_PACK_COMPAT_SMELL"
REQUIRED_FILES = {
    "docs/packs/PACK_COMPATIBILITY_MANIFEST.md": (
        "pack.compat.json",
        "strict policy surfaces must refuse packs missing it",
        "refusal.pack.compat_manifest_missing",
    ),
    "schemas/pack_compat_manifest.schema.json": (
        "\"title\": \"Pack Compatibility Manifest Schema\"",
        "\"required_contract_ranges\"",
        "\"degrade_mode_id\"",
    ),
    "data/registries/pack_degrade_mode_registry.json": (
        "\"pack.degrade.strict_refuse\"",
        "\"pack.degrade.best_effort\"",
        "\"pack.degrade.read_only_only\"",
    ),
    "packs/compat/pack_compat_validator.py": (
        "PACK_COMPAT_MANIFEST_NAME",
        "REFUSAL_PACK_COMPAT_MANIFEST_MISSING",
        "validate_pack_compat_manifest(",
    ),
}
REQUIRED_OFFICIAL_COMPAT = (
    "packs/official/pack.sol.pin_minimal/pack.compat.json",
)


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
    related_paths = list(REQUIRED_FILES.keys()) + list(REQUIRED_OFFICIAL_COMPAT)
    for rel_path, tokens in REQUIRED_FILES.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="packs.missing_pack_compat_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required pack compatibility surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-OFFICIAL-PACKS-HAVE-COMPAT-MANIFEST",
                        "INV-STRICT-MODE-REFUSES-MISSING-COMPAT",
                    ],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="packs.missing_pack_compat_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing pack-compat marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-OFFICIAL-PACKS-HAVE-COMPAT-MANIFEST",
                        "INV-STRICT-MODE-REFUSES-MISSING-COMPAT",
                    ],
                    related_paths=related_paths,
                )
            )
    for rel_path in REQUIRED_OFFICIAL_COMPAT:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="packs.missing_pack_compat_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["official pack compatibility sidecar is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-OFFICIAL-PACKS-HAVE-COMPAT-MANIFEST",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
