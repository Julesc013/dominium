Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UPS Runtime API (Engine)

This document defines the engine-facing UPS runtime contract. It is normative
for `engine/include/domino/ups.h`.

## Responsibilities

- Load pack manifests without accessing pack contents.
- Index provided capabilities deterministically.
- Resolve capability providers by explicit precedence only.
- Expose inspection hooks for packs, providers, fallbacks, and compat mode.

## Deterministic Resolution

- Provider ordering MUST be deterministic for the same manifests and precedence.
- Tie-breaks MUST NOT depend on filesystem ordering or pointer identity.

## Inspection Hooks

- Loaded pack manifests and precedence: `dom_ups_registry_pack_get`.
- Capability providers: `dom_ups_registry_resolve_capability`,
  `dom_ups_registry_list_providers`.
- Active capability sets: `dom_ups_registry_provided_caps`.
- Fallback activations: `dom_ups_registry_report_fallback`,
  `dom_ups_registry_fallback_get`.
- Selected compatibility mode: `dom_ups_registry_set_compat_decision`,
  `dom_ups_registry_get_compat_decision`.

## Zero-Pack Operation

- All APIs MUST behave safely when zero packs are registered.
- No API may require assets to be present.