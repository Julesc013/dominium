"""A5 Cross-Pack Dependency Entropy Analyzer."""

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "A5_CROSS_PACK_ENTROPY"
WATCH_PREFIXES = ("data/packs/", "data/registries/")
MAX_REQUIRES = 8
MAX_FANIN = 10


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    packs_root = os.path.join(repo_root, "data", "packs")
    manifests = []
    for root, dirs, files in os.walk(packs_root):
        dirs[:] = sorted(dirs)
        for name in sorted(files):
            if name != "pack_manifest.json":
                continue
            manifests.append(os.path.join(root, name))

    pack_requires = {}
    for manifest in sorted(manifests):
        rel = os.path.relpath(manifest, repo_root).replace("\\", "/")
        payload = _load_json(manifest) or {}
        pack_id = str(payload.get("pack_id", "")).strip() or rel
        requires = payload.get("requires", [])
        if not isinstance(requires, list):
            requires = []
        reqs = sorted({str(item).strip() for item in requires if str(item).strip()})
        pack_requires[pack_id] = {"manifest": rel, "requires": reqs}

    fanin = {}
    for pack_id, row in pack_requires.items():
        for req in row["requires"]:
            fanin.setdefault(req, set()).add(pack_id)

    findings = []
    for pack_id in sorted(pack_requires.keys()):
        row = pack_requires[pack_id]
        if len(row["requires"]) > MAX_REQUIRES:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="semantic.cross_pack_entropy",
                    severity="RISK",
                    confidence=0.82,
                    file_path=row["manifest"],
                    evidence=[
                        "Pack has high dependency fan-out ({} requires).".format(len(row["requires"])),
                        "Pack: {}".format(pack_id),
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-PACK-SCOPE-ISOLATION"],
                    related_paths=[row["manifest"]],
                )
            )

    for pack_id in sorted(fanin.keys()):
        dependents = sorted(fanin[pack_id])
        if len(dependents) <= MAX_FANIN:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="semantic.cross_pack_entropy",
                severity="WARN",
                confidence=0.73,
                file_path="data/packs",
                evidence=[
                    "Pack is a high fan-in dependency ({} dependents).".format(len(dependents)),
                    "Pack: {}".format(pack_id),
                ],
                suggested_classification="LEGACY",
                recommended_action="DOC_FIX",
                related_invariants=["INV-PACK-SCOPE-ISOLATION"],
                related_paths=["data/packs"],
            )
        )
    return findings

