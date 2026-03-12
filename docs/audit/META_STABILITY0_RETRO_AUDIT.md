# META-STABILITY-0 Retro Audit

## Purpose

This audit identifies the registry families in scope for the initial stability classification rollout, the existing status-like metadata already present in those families, and the least risky insertion point for stability metadata.

The audit is intentionally conservative. The goal is to add an enforced stability discipline without changing runtime semantics or breaking existing registry consumers.

## Scoped Registry Families

The initial enforcement scope for META-STABILITY-0 covers the registry families created in the project scope called out by the gate:

- `GEO/MW/SOL/EARTH`
  - `data/registries/galaxy_priors_registry.json`
  - `data/registries/generator_version_registry.json`
  - `data/registries/illumination_model_registry.json`
  - `data/registries/shadow_model_registry.json`
  - `data/registries/sky_model_registry.json`
  - `data/registries/surface_generator_registry.json`
  - `data/registries/surface_generator_routing_registry.json`
  - `data/registries/tide_params_registry.json`
  - `data/registries/wind_params_registry.json`
- `LOGIC`
  - `data/registries/logic_behavior_model_registry.json`
  - `data/registries/logic_compile_policy_registry.json`
  - `data/registries/logic_element_registry.json`
  - `data/registries/logic_network_policy_registry.json`
  - `data/registries/logic_security_policy_registry.json`
  - `data/registries/logic_state_machine_registry.json`
  - `data/registries/verification_procedure_registry.json`
- `SYS`
  - `data/registries/system_boundary_invariant_registry.json`
  - `data/registries/system_macro_model_registry.json`
  - `data/registries/system_priors_registry.json`
  - `data/registries/system_template_registry.json`
- `PROC`
  - `data/registries/process_capsule_registry.json`
  - `data/registries/process_drift_policy_registry.json`
  - `data/registries/process_lifecycle_policy_registry.json`
  - `data/registries/process_registry.json`
  - `data/registries/process_stabilization_policy_registry.json`
- `CAP-NEG`
  - `data/registries/capability_fallback_registry.json`
  - `data/registries/compat_mode_registry.json`
  - `data/registries/degrade_ladder_registry.json`
  - `data/registries/product_registry.json`
  - `data/registries/protocol_registry.json`
  - `data/registries/semantic_contract_registry.json`
- `PACK-COMPAT`
  - `data/registries/pack_degrade_mode_registry.json`
  - `data/registries/provides_registry.json`
- `LIB`
  - `data/registries/bundle_profiles.json`
  - `data/registries/install_registry.json`
  - `data/registries/platform_registry.json`
  - `data/registries/server_config_registry.json`
  - `data/registries/server_profile_registry.json`
  - `data/registries/software_toolchain_registry.json`
- `APPSHELL`
  - `data/registries/command_registry.json`
  - `data/registries/exit_code_registry.json`
  - `data/registries/log_category_registry.json`
  - `data/registries/log_message_key_registry.json`
  - `data/registries/refusal_code_registry.json`
  - `data/registries/tui_layout_registry.json`
  - `data/registries/tui_panel_registry.json`
- `DIAG`
  - no dedicated DIAG-only registry was found in `data/registries/`
  - current DIAG scope is expressed through AppShell command registry entries and DIAG schemas/artifact manifests

## Existing Status-Like Fields Already Present

The current registry set already uses multiple ad hoc fields that imply maturity or incompleteness:

- `stub`
  - present in several registries outside the scoped set and in some pack content
- `status`
  - present in registries such as `domain_registry.json`, `thermal_model_registry.json`, `reference_evaluator_registry.json`
- `runtime_status`
  - present in tool/instrument registries
- `module_status`
  - present in `worldgen_module_registry.json`
- `placeholder`
  - present in `surface_generator_registry.json`, `server_config_registry.json`, and several materials/mixture-adjacent registries
- `deprecated`
  - already present in many mature registries, especially `process_registry.json` and contract-like registries

Within the scoped META-STABILITY-0 families specifically:

- `surface_generator_registry.json` already carries `extensions.placeholder`
- `command_registry.json` and related AppShell registries do not currently carry a maturity field
- `compat_mode_registry.json`, `degrade_ladder_registry.json`, `protocol_registry.json`, and `semantic_contract_registry.json` do not currently carry an explicit stability class
- `process_registry.json` already carries `deprecated`, but not an explicit stability plan
- `platform_registry.json` carries `extensions.support_status` on some legacy targets

Conclusion:

- existing `status` or `stub` fields are inconsistent and domain-specific
- they are not sufficient as a cross-cutting stability contract
- they should not be reinterpreted as the authoritative stability class

## Safe Insertion Point

The safest non-breaking insertion point is:

- add optional `stability` as a sibling field on each registry entry object

This is preferred over an entry wrapper such as:

- `{ "id": "...", "stability": {...}, "data": {...existing...} }`

Reason:

- many existing loaders normalize entire entry maps and tolerate unknown fields
- some registry families already declare open-map behavior explicitly
- wrapping existing entry payloads in `data` would require loader/schema migrations and would break current callers that expect fields like `command_id`, `contract_id`, `process_id`, or `generator_id` at the top level of the entry object

Observed loader behavior supporting the sibling-field approach:

- `src/appshell/command_registry.py` normalizes command rows as open maps and computes deterministic fingerprints from the full row
- `src/compat/capability_negotiation.py` normalizes negotiation rows from open maps and preserves unknown fields
- `src/worldgen/earth/sky/sky_view_engine.py` reads registry rows by ID from full entry maps without requiring a closed field set
- `schema/process.registry.schema` explicitly states that process registry records are open maps and unknown fields must be preserved

## Immediate Stable Candidates

Stable classification should stay rare in MVP. The current immediate candidates are:

- all rows in `data/registries/semantic_contract_registry.json`
  - these are already the binding semantic freeze points
- CAP-NEG negotiation semantics that are already treated as release-gating contracts
  - `data/registries/compat_mode_registry.json`
  - `data/registries/protocol_registry.json`
  - `data/registries/degrade_ladder_registry.json`
- the overlay merge contract row already present in `data/registries/semantic_contract_registry.json`

Everything else in the scoped families should default to `provisional` for the initial rollout unless there is a stronger contract reason to freeze it immediately.

## Risk Notes

- `process_registry.json` uses a root `records` array rather than `record.<collection>`; the validator must support both shapes
- `install_registry.json` is currently empty; enforcement must allow empty collections while still validating metadata when entries exist
- DIAG currently has no dedicated registry file; enforcement for DIAG stability must attach through the AppShell command registry and optional artifact-manifest hooks rather than by inventing a synthetic registry

## Decision

META-STABILITY-0 should proceed with:

- optional sibling `stability` markers on scoped registry entries
- deterministic fingerprinting of the stability metadata as part of the containing entry fingerprint
- conservative default classification of `provisional`
- a small, explicit set of `stable` CAP-NEG and semantic-contract rows only
