"""Registry families and file inventories for META-STABILITY."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
REGISTRY_ROOT = os.path.join(REPO_ROOT_HINT, "data", "registries")


SCOPED_REGISTRY_GROUPS: dict[str, tuple[str, ...]] = {
    "geo_mw_sol_earth": (
        "contracts/registry/galaxy_priors_registry.json",
        "contracts/registry/generator_version_registry.json",
        "contracts/registry/illumination_model_registry.json",
        "contracts/registry/shadow_model_registry.json",
        "contracts/registry/sky_model_registry.json",
        "contracts/registry/surface_generator_registry.json",
        "contracts/registry/surface_generator_routing_registry.json",
        "contracts/registry/tide_params_registry.json",
        "contracts/registry/wind_params_registry.json",
    ),
    "logic": (
        "contracts/registry/logic_behavior_model_registry.json",
        "contracts/registry/logic_compile_policy_registry.json",
        "contracts/registry/logic_element_registry.json",
        "contracts/registry/logic_network_policy_registry.json",
        "contracts/registry/logic_security_policy_registry.json",
        "contracts/registry/logic_state_machine_registry.json",
        "contracts/registry/verification_procedure_registry.json",
    ),
    "sys": (
        "contracts/registry/system_boundary_invariant_registry.json",
        "contracts/registry/system_macro_model_registry.json",
        "contracts/registry/system_priors_registry.json",
        "contracts/registry/system_template_registry.json",
    ),
    "proc": (
        "contracts/registry/process_capsule_registry.json",
        "contracts/registry/process_drift_policy_registry.json",
        "contracts/registry/process_lifecycle_policy_registry.json",
        "contracts/registry/process_registry.json",
        "contracts/registry/process_stabilization_policy_registry.json",
    ),
    "cap_neg": (
        "contracts/registry/capability_fallback_registry.json",
        "contracts/registry/compat_mode_registry.json",
        "contracts/registry/degrade_ladder_registry.json",
        "contracts/registry/product_registry.json",
        "contracts/registry/protocol_registry.json",
        "contracts/registry/semantic_contract_registry.json",
    ),
    "pack_compat": (
        "contracts/registry/pack_degrade_mode_registry.json",
        "contracts/registry/provides_registry.json",
    ),
    "lib": (
        "contracts/registry/bundle_profiles.json",
        "contracts/registry/install_registry.json",
        "contracts/registry/platform_registry.json",
        "contracts/registry/server_config_registry.json",
        "contracts/registry/server_profile_registry.json",
        "contracts/registry/software_toolchain_registry.json",
    ),
    "appshell": (
        "contracts/registry/command_registry.json",
        "contracts/registry/exit_code_registry.json",
        "contracts/registry/log_category_registry.json",
        "contracts/registry/log_message_key_registry.json",
        "contracts/registry/refusal_code_registry.json",
        "contracts/registry/tui_layout_registry.json",
        "contracts/registry/tui_panel_registry.json",
    ),
}

SCOPED_REGISTRY_PATHS: tuple[str, ...] = tuple(
    path for group_paths in SCOPED_REGISTRY_GROUPS.values() for path in group_paths
)

LEGACY_TEXT_REGISTRY_PATHS: tuple[str, ...] = (
    "contracts/registry/control_capabilities.registry",
    "contracts/registry/law_targets.registry",
)


def _all_registry_paths() -> tuple[str, ...]:
    if not os.path.isdir(REGISTRY_ROOT):
        return ()
    rows = []
    for name in sorted(os.listdir(REGISTRY_ROOT)):
        abs_path = os.path.join(REGISTRY_ROOT, name)
        if not os.path.isfile(abs_path):
            continue
        rows.append("data/registries/{}".format(str(name).replace("\\", "/")))
    return tuple(rows)


ALL_REGISTRY_PATHS: tuple[str, ...] = _all_registry_paths()


def grouped_registry_paths() -> dict[str, tuple[str, ...]]:
    return dict((key, tuple(value)) for key, value in SCOPED_REGISTRY_GROUPS.items())


def scoped_registry_paths() -> tuple[str, ...]:
    return tuple(SCOPED_REGISTRY_PATHS)


def all_registry_paths() -> tuple[str, ...]:
    return tuple(ALL_REGISTRY_PATHS)


def family_for_registry(rel_path: str) -> str:
    token = str(rel_path or "").replace("\\", "/")
    for family, rows in SCOPED_REGISTRY_GROUPS.items():
        if token in rows:
            return family
    return ""


__all__ = [
    "ALL_REGISTRY_PATHS",
    "LEGACY_TEXT_REGISTRY_PATHS",
    "SCOPED_REGISTRY_GROUPS",
    "SCOPED_REGISTRY_PATHS",
    "all_registry_paths",
    "family_for_registry",
    "grouped_registry_paths",
    "scoped_registry_paths",
]
