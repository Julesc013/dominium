"""Release identity helpers with lazy exports to avoid cross-layer import cycles."""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "DEFAULT_BUILD_NUMBER": ("tools.release.build_id_engine", "DEFAULT_BUILD_NUMBER"),
    "DEFAULT_BUILD_CONFIGURATION": ("tools.release.build_id_engine", "DEFAULT_BUILD_CONFIGURATION"),
    "DEFAULT_PRODUCT_SEMVER": ("tools.release.build_id_engine", "DEFAULT_PRODUCT_SEMVER"),
    "DEFAULT_RELEASE_CHANNEL": ("tools.release.release_manifest_engine", "DEFAULT_RELEASE_CHANNEL"),
    "DEFAULT_COMPONENT_GRAPH_ID": ("tools.release.component_graph_resolver", "DEFAULT_COMPONENT_GRAPH_ID"),
    "DEFAULT_COMPONENT_GRAPH_REGISTRY_REL": ("tools.release.component_graph_resolver", "DEFAULT_COMPONENT_GRAPH_REGISTRY_REL"),
    "DEFAULT_INSTALL_PROFILE_ID": ("tools.release.component_graph_resolver", "DEFAULT_INSTALL_PROFILE_ID"),
    "DEFAULT_INSTALL_PROFILE_REGISTRY_REL": ("tools.release.component_graph_resolver", "DEFAULT_INSTALL_PROFILE_REGISTRY_REL"),
    "DEFAULT_RELEASE_MANIFEST_REL": ("tools.release.release_manifest_engine", "DEFAULT_RELEASE_MANIFEST_REL"),
    "DEFAULT_RELEASE_MANIFEST_VERSION": ("tools.release.release_manifest_engine", "DEFAULT_RELEASE_MANIFEST_VERSION"),
    "DEFAULT_RELEASE_INDEX_REL": ("tools.release.update_resolver", "DEFAULT_RELEASE_INDEX_REL"),
    "DEFAULT_RELEASE_RESOLUTION_POLICY_ID": ("tools.release.update_resolver", "DEFAULT_RELEASE_RESOLUTION_POLICY_ID"),
    "DEFAULT_RELEASE_RESOLUTION_POLICY_REGISTRY_REL": ("tools.release.update_resolver", "DEFAULT_RELEASE_RESOLUTION_POLICY_REGISTRY_REL"),
    "DEFAULT_RELEASE_SERIES": ("tools.release.update_resolver", "DEFAULT_RELEASE_SERIES"),
    "DEFAULT_SIGNATURE_SCHEME_ID": ("tools.release.release_manifest_engine", "DEFAULT_SIGNATURE_SCHEME_ID"),
    "DEFAULT_INSTALL_TRANSACTION_LOG_REL": ("tools.release.update_resolver", "DEFAULT_INSTALL_TRANSACTION_LOG_REL"),
    "build_build_id_input_payload": ("tools.release.build_id_engine", "build_build_id_input_payload"),
    "build_compilation_options_payload": ("tools.release.build_id_engine", "build_compilation_options_payload"),
    "build_id_identity_from_input_payload": ("tools.release.build_id_engine", "build_id_identity_from_input_payload"),
    "build_product_build_metadata": ("tools.release.build_id_engine", "build_product_build_metadata"),
    "build_default_component_install_plan": ("tools.release.component_graph_resolver", "build_default_component_install_plan"),
    "build_release_manifest": ("tools.release.release_manifest_engine", "build_release_manifest"),
    "build_mock_signature_block": ("tools.release.release_manifest_engine", "build_mock_signature_block"),
    "canonicalize_component_descriptor": ("tools.release.component_graph_resolver", "canonicalize_component_descriptor"),
    "canonicalize_install_profile": ("tools.release.component_graph_resolver", "canonicalize_install_profile"),
    "canonicalize_release_index": ("tools.release.update_resolver", "canonicalize_release_index"),
    "canonicalize_release_resolution_policy": ("tools.release.update_resolver", "canonicalize_release_resolution_policy"),
    "canonicalize_update_plan": ("tools.release.update_resolver", "canonicalize_update_plan"),
    "component_managed_paths": ("tools.release.update_resolver", "component_managed_paths"),
    "cross_check_release_manifest_build_ids": ("tools.release.release_manifest_engine", "cross_check_release_manifest_build_ids"),
    "append_install_transaction": ("tools.release.update_resolver", "append_install_transaction"),
    "infer_dist_root_from_manifest_path": ("tools.release.release_manifest_engine", "infer_dist_root_from_manifest_path"),
    "infer_release_index_path": ("tools.release.update_resolver", "infer_release_index_path"),
    "load_product_capability_defaults": ("tools.release.build_id_engine", "load_product_capability_defaults"),
    "load_component_graph_registry": ("tools.release.component_graph_resolver", "load_component_graph_registry"),
    "load_default_component_graph": ("tools.release.component_graph_resolver", "load_default_component_graph"),
    "load_install_transaction_log": ("tools.release.update_resolver", "load_install_transaction_log"),
    "load_release_resolution_policy_registry": ("tools.release.update_resolver", "load_release_resolution_policy_registry"),
    "load_install_profile_registry": ("tools.release.component_graph_resolver", "load_install_profile_registry"),
    "load_release_index": ("tools.release.update_resolver", "load_release_index"),
    "load_release_manifest": ("tools.release.release_manifest_engine", "load_release_manifest"),
    "load_signature_blocks": ("tools.release.release_manifest_engine", "load_signature_blocks"),
    "product_capability_default_rows_by_id": ("tools.release.build_id_engine", "product_capability_default_rows_by_id"),
    "platform_targets_for_tag": ("tools.release.component_graph_resolver", "platform_targets_for_tag"),
    "release_index_hash": ("tools.release.update_resolver", "release_index_hash"),
    "release_index_signed_hash": ("tools.release.update_resolver", "release_index_signed_hash"),
    "resolve_component_graph": ("tools.release.component_graph_resolver", "resolve_component_graph"),
    "resolve_release_artifact_root": ("tools.release.update_resolver", "resolve_release_artifact_root"),
    "resolve_release_index_platform_entry": ("tools.release.update_resolver", "resolve_release_index_platform_entry"),
    "resolve_update_plan": ("tools.release.update_resolver", "resolve_update_plan"),
    "RESOLUTION_POLICY_EXACT_SUITE": ("tools.release.update_resolver", "RESOLUTION_POLICY_EXACT_SUITE"),
    "RESOLUTION_POLICY_LATEST_COMPATIBLE": ("tools.release.update_resolver", "RESOLUTION_POLICY_LATEST_COMPATIBLE"),
    "RESOLUTION_POLICY_LAB": ("tools.release.update_resolver", "RESOLUTION_POLICY_LAB"),
    "select_component_graph": ("tools.release.component_graph_resolver", "select_component_graph"),
    "select_install_profile": ("tools.release.component_graph_resolver", "select_install_profile"),
    "select_release_resolution_policy": ("tools.release.update_resolver", "select_release_resolution_policy"),
    "select_rollback_transaction": ("tools.release.update_resolver", "select_rollback_transaction"),
    "semantic_contract_registry_hash": ("tools.release.build_id_engine", "semantic_contract_registry_hash"),
    "source_revision_id": ("tools.release.build_id_engine", "source_revision_id"),
    "validate_instance_against_install_plan": ("tools.release.component_graph_resolver", "validate_instance_against_install_plan"),
    "verify_signature_blocks": ("tools.release.release_manifest_engine", "verify_signature_blocks"),
    "verify_release_manifest": ("tools.release.release_manifest_engine", "verify_release_manifest"),
    "write_release_index": ("tools.release.update_resolver", "write_release_index"),
    "write_release_manifest": ("tools.release.release_manifest_engine", "write_release_manifest"),
}

__all__ = sorted(_EXPORTS.keys())


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if not target:
        raise AttributeError("module 'release' has no attribute {!r}".format(name))
    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(__all__))
