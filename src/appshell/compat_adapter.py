"""AppShell adapters for CAP-NEG product descriptor and version surfaces."""

from __future__ import annotations

from src.compat import emit_product_descriptor
from src.release import build_product_build_metadata


def emit_descriptor_payload(repo_root: str, product_id: str, descriptor_file: str = "") -> dict:
    return emit_product_descriptor(
        repo_root,
        product_id=str(product_id).strip(),
        descriptor_file=str(descriptor_file or "").strip(),
    )


def build_version_payload(repo_root: str, product_id: str) -> dict:
    emitted = emit_descriptor_payload(repo_root, product_id=str(product_id).strip(), descriptor_file="")
    descriptor = dict(emitted.get("descriptor") or {})
    extensions = dict(descriptor.get("extensions") or {})
    build_meta = build_product_build_metadata(repo_root, str(product_id).strip())
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "product_version": str(descriptor.get("product_version", "")).strip(),
        "build_id": str(extensions.get("official.build_id", "")).strip(),
        "inputs_hash": str(build_meta.get("inputs_hash", "")).strip(),
        "git_commit_hash": str(extensions.get("official.git_commit_hash", "")).strip(),
        "semantic_contract_registry_hash": str(extensions.get("official.semantic_contract_registry_hash", "")).strip(),
        "compilation_options_hash": str(extensions.get("official.compilation_options_hash", "")).strip(),
        "descriptor_hash": str(emitted.get("descriptor_hash", "")).strip(),
    }


__all__ = ["build_version_payload", "emit_descriptor_payload"]
