Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# CAPABILITY-REFUSAL-LAW-01 Audit

Result: PASS_WITH_WARNINGS, pending final commit and post-commit checks.

## Why

Dominium needs explicit capability negotiation and refusal semantics before
optional providers, renderers, platforms, packs, Workbench modules, commands,
and release gates become product behavior. Silent fallback and free-text-only
refusals would make setup, support, AIDE/Codex repair, and Workbench reporting
unreliable.

## Added

- `contracts/capability/capability.contract.toml`
- `contracts/capability/capability.schema.json`
- `contracts/capability/capability.registry.json`
- `contracts/capability/capability_kind.registry.json`
- `contracts/capability/capability_request.schema.json`
- `contracts/capability/capability_decision.schema.json`
- `contracts/capability/degradation_policy.contract.toml`
- `contracts/capability/recovery_policy.contract.toml`
- `contracts/refusal/refusal.contract.toml`
- `tools/validators/contracts/check_capability_refusal.py`
- `tests/contract/capability_refusal/**`
- `docs/architecture/capability_refusal_law.md`
- `docs/development/capability_refusal_guidelines.md`

## Registry Changes

- capabilities registered: 9
- refusal codes registered: 13
- capability/refusal diagnostic codes added: 7 new codes plus the existing
  missing-capability code
- public surface registry updated with capability/refusal surfaces
- command surface contract updated with capability/refusal cross-references

## Inventory

The initial descriptive inventory scanned 17,837 tracked files and classified
1,190 capability/refusal/provider/trust candidates:

- 86 capability candidates.
- 66 provider candidates.
- 97 future provider-model items.
- 6 command-required capability candidates.
- 650 artifact/trust candidates.
- 285 deferred provider/AIDE/release-adjacent files.

The inventory records scope only. Current providers, runtime backends, packs,
Workbench modules, and product behavior are not migrated by this task.

## Proof

- Capability/refusal validator strict mode passes.
- Capability/refusal fixture mode passes.
- Inventory mode is warning-only and descriptive.
- Diagnostics, command-surface, public-surface, schema/protocol, artifact, ABI,
  repo layout, root allowlist, distribution, component, docs, build-boundary,
  UI shell, and ABI-boundary checks pass.
- Dependency-direction validator still reports the known existing debt: 358
  violations and 38 warnings.
- Fast strict passes: 32/32 commands in 313.656 seconds.

## Known Limitations

- Law is provisional.
- Runtime capability resolver is not implemented.
- Provider model is not implemented.
- Renderer/platform fallback and package/mod trust runtime are not implemented.
- Existing dependency-direction debt remains visible.
- Full CTest is not run; it remains T4 full/release proof.

Next task: `PROVIDER-MODEL-01`.
