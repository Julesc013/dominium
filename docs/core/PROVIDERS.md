# Providers

This repo quarantines external ecosystem integrations behind small, stable provider ABIs so launcher/setup kernels remain platform-agnostic and deterministic.

## Provider Categories
- content_source: resolve/acquire artifacts (local store, offline sources)
- trust: signature/manifest verification (policy is outside the provider)
- keychain: secure storage (optional)
- net: network transport (optional)
- os_integration: shortcuts, file associations, open-folder

## ABI Rules
- C89-compatible vtables with `DOM_ABI_HEADER`, `abi_version`, `struct_size`, and `query_interface`.
- No STL or exceptions; outputs via out-params; errors via `err_t`.
- Provider IDs are stable ASCII tokens and must never be renamed.

## Selection + Recording
- Providers are registered in `source/dominium/providers/provider_registry.c`.
- Each entry declares typed caps + constraints for the solver.
- Selection results are recorded in `selection_summary.tlv` and audit.

## Built-in Providers
- null: returns `ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL` for operations.
- content_source local_fs: resolves artifacts from the local store deterministically.

## Policy Interaction
- Offline/trust requirements are enforced by policy; providers only report capabilities.
- If a required capability is missing, the solver refuses deterministically.

## Adding a Provider
1) Implement a new `provider_*_v1` vtable (C, deterministic).
2) Add a registry entry with caps/constraints and stable provider_id.
3) Add headless tests to cover selection + refusal behavior.
4) Update this document if new categories or keys are introduced.
