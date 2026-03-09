"""E367 embodiment asset dependency smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E367_ASSET_DEPENDENCY_SMELL"
WATCH_PREFIXES = ("src/embodiment/", "data/registries/", "docs/embodiment/")
BODY_SYSTEM_REL = "src/embodiment/body/body_system.py"
LENS_ENGINE_REL = "src/embodiment/lens/lens_engine.py"
BODY_TEMPLATE_REGISTRY_REL = "data/registries/body_template_registry.json"
SYSTEM_TEMPLATE_REGISTRY_REL = "data/registries/system_template_registry.json"
DOC_REL = "docs/embodiment/EMBODIMENT_BASELINE.md"
REQUIRED_TOKENS = {
    BODY_SYSTEM_REL: (
        "instantiate_body_system(",
        '"shape_type": str(template_row.get("collider_kind", "capsule")).strip() or "capsule"',
        '"vertex_ref_id": ""',
        "build_momentum_state(",
    ),
    BODY_TEMPLATE_REGISTRY_REL: (
        "template.body.pill",
        '"collider_kind": "capsule"',
        '"movement_params_ref": "move.body.default_ground"',
    ),
    SYSTEM_TEMPLATE_REGISTRY_REL: (
        "template.body.pill",
        '"art_free": true',
        '"collider_kind": "capsule"',
    ),
    DOC_REL: (
        "no textures are required",
        "no meshes are required",
        "primitive capsule",
        "art-free",
    ),
}
FORBIDDEN_TOKENS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".tga",
    ".dds",
    ".fbx",
    ".gltf",
    ".glb",
    "texture_path",
    "mesh_path",
    "skeleton",
    "rig_ref",
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
    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.asset_dependency_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required EMB-0 artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NO-ASSET-DEPENDENCY-FOR-EMB"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.asset_dependency_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing EMB-0 asset-free marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-ASSET-DEPENDENCY-FOR-EMB"],
                    related_paths=list(REQUIRED_TOKENS.keys()),
                )
            )

    for rel_path in (BODY_SYSTEM_REL, LENS_ENGINE_REL, BODY_TEMPLATE_REGISTRY_REL, SYSTEM_TEMPLATE_REGISTRY_REL):
        text = _read_text(repo_root, rel_path).lower()
        for line_no, line in enumerate(text.splitlines(), start=1):
            snippet = str(line).strip()
            if not snippet or snippet.startswith("#"):
                continue
            token = next((item for item in FORBIDDEN_TOKENS if item in snippet), "")
            if not token:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="embodiment.asset_dependency_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=line_no,
                    evidence=["forbidden embodiment asset token detected: {}".format(token), snippet[:160]],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-ASSET-DEPENDENCY-FOR-EMB"],
                    related_paths=[BODY_SYSTEM_REL, LENS_ENGINE_REL, BODY_TEMPLATE_REGISTRY_REL, SYSTEM_TEMPLATE_REGISTRY_REL],
                )
            )
            break
    return findings
