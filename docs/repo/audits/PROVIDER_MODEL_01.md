Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# PROVIDER-MODEL-01 Audit

Result: PASS_WITH_WARNINGS, pending final commit and post-commit checks.

## Why

Dominium needs replaceable renderers, platforms, storage backends, package
validators, Workbench modules, external adapters, and future native providers
to be governed by identity, capability, selection, refusal, diagnostics,
evidence, ABI, and conformance law instead of ad hoc implementation paths.

## Added

- `contracts/provider/provider.contract.toml`
- `contracts/provider/provider.schema.json`
- `contracts/provider/provider_descriptor.schema.json`
- `contracts/provider/provider_kind.registry.json`
- `contracts/provider/provider_lifecycle.registry.json`
- `contracts/provider/provider_selection_request.schema.json`
- `contracts/provider/provider_selection_decision.schema.json`
- `contracts/provider/provider_conformance.contract.toml`
- `contracts/provider/provider_capability_policy.contract.toml`
- `contracts/provider/provider_trust_policy.contract.toml`
- `contracts/provider/provider.registry.json`
- `tools/validators/contracts/check_provider_model.py`
- `tests/contract/provider/**`
- `docs/architecture/provider_model.md`
- `docs/development/provider_guidelines.md`

## Registry Changes

- provider descriptors registered: 5
- provider kinds registered: 15
- provider lifecycle states registered: 9
- provider trust levels registered: 10
- public surface registry updated with provider model surfaces
- diagnostics registry updated with provider diagnostic codes
- refusal registry updated with provider refusal codes
- capability registry updated with narrow `provided_by` cross-references

## Inventory

The initial descriptive inventory scanned 17,865 tracked files and classified
1,396 provider/backend/service/adapter/capability candidates:

- 152 backend candidates.
- 96 service candidates.
- 215 command handler candidates.
- 97 Workbench module candidates.
- 195 external adapter candidates.
- 10 capability relationship files.
- 631 pack hints that are not provider runtime truth.

The inventory records scope only. Current runtime backends, tools, Workbench
modules, and pack data are not migrated by this task.

## Proof

- Provider validator strict mode passes.
- Provider fixture mode passes with 9 fixtures.
- Provider inventory mode is warning-only and descriptive.
- Capability/refusal, diagnostics, command-surface, public-surface,
  schema/protocol, artifact, ABI, repo layout, root allowlist, distribution,
  component, docs, build-boundary, UI shell, and ABI-boundary checks pass.
- Dependency-direction validator still reports the known existing debt: 358
  violations and 38 warnings.
- Fast strict passes: 32/32 commands in 315.484 seconds.

## Known Limitations

- Provider model is provisional.
- Runtime provider resolver is not implemented.
- Dynamic/native loading is not implemented.
- Provider conformance suites are skeletal fixtures only.
- Mod/native trust hardening remains future work.
- Existing dependency-direction debt remains visible.
- Full CTest is not run; it remains T4 full/release proof.

Next task: `MODULE-COMPOSITION-LAW-01`.
