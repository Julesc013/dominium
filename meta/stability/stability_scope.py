"""Registry families and file inventories for META-STABILITY."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
REGISTRY_ROOT = os.path.join(REPO_ROOT_HINT, "data", "registries")


SCOPED_REGISTRY_GROUPS: dict[str, tuple[str, ...]] = {
    "geo_mw_sol_earth": (
        "data/registries/galaxy_priors_registry.json",
        "data/registries/generator_version_registry.json",
        "data/registries/illumination_model_registry.json",
        "data/registries/shadow_model_registry.json",
        "data/registries/sky_model_registry.json",
        "data/registries/surface_generator_registry.json",
        "data/registries/surface_generator_routing_registry.json",
        "data/registries/tide_params_registry.json",
        "data/registries/wind_params_registry.json",
    ),
    "logic": (
        "data/registries/logic_behavior_model_registry.json",
        "data/registries/logic_compile_policy_registry.json",
        "data/registries/logic_element_registry.json",
        "data/registries/logic_network_policy_registry.json",
        "data/registries/logic_security_policy_registry.json",
        "data/registries/logic_state_machine_registry.json",
        "data/registries/verification_procedure_registry.json",
    ),
    "sys": (
        "data/registries/system_boundary_invariant_registry.json",
        "data/registries/system_macro_model_registry.json",
        "data/registries/system_priors_registry.json",
        "data/registries/system_template_registry.json",
    ),
    "proc": (
        "data/registries/process_capsule_registry.json",
        "data/registries/process_drift_policy_registry.json",
        "data/registries/process_lifecycle_policy_registry.json",
        "data/registries/process_registry.json",
        "data/registries/process_stabilization_policy_registry.json",
    ),
    "cap_neg": (
        "data/registries/capability_fallback_registry.json",
        "data/registries/compat_mode_registry.json",
        "data/registries/degrade_ladder_registry.json",
        "data/registries/product_registry.json",
        "data/registries/protocol_registry.json",
        "data/registries/semantic_contract_registry.json",
    ),
    "pack_compat": (
        "data/registries/pack_degrade_mode_registry.json",
        "data/registries/provides_registry.json",
    ),
    "lib": (
        "data/registries/bundle_profiles.json",
        "data/registries/install_registry.json",
        "data/registries/platform_registry.json",
        "data/registries/server_config_registry.json",
        "data/registries/server_profile_registry.json",
        "data/registries/software_toolchain_registry.json",
    ),
    "appshell": (
        "data/registries/command_registry.json",
        "data/registries/exit_code_registry.json",
        "data/registries/log_category_registry.json",
        "data/registries/log_message_key_registry.json",
        "data/registries/refusal_code_registry.json",
        "data/registries/tui_layout_registry.json",
        "data/registries/tui_panel_registry.json",
    ),
}

SCOPED_REGISTRY_PATHS: tuple[str, ...] = tuple(
    path for group_paths in SCOPED_REGISTRY_GROUPS.values() for path in group_paths
)

LEGACY_TEXT_REGISTRY_PATHS: tuple[str, ...] = (
    "data/registries/control_capabilities.registry",
    "data/registries/law_targets.registry",
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
