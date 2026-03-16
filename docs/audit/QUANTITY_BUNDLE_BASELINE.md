Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Quantity Bundle Baseline

Status: Baseline complete (META-MODEL-2)
Date: 2026-03-03

## Scope Summary

META-MODEL-2 upgrades FlowSystem from scalar-only channels to deterministic multi-component QuantityBundles while preserving legacy scalar behavior.

## Schema and Registry Changes

Added/updated schema contracts:
- `schema/core/quantity_bundle.schema` (`1.0.0`)
- `schema/core/component_policy.schema` (`1.0.0`)
- `schema/core/flow_channel.schema` (`1.1.0` additive)
- `schema/core/flow_transfer_event.schema` (`1.1.0` additive)

Added registry datasets:
- `data/registries/quantity_bundle_registry.json`
- `data/registries/component_capacity_policy_registry.json`
- `data/registries/component_loss_policy_registry.json`

CompatX / registry compile integration:
- Version registry now tracks `flow_channel` and `flow_transfer_event` at `1.1.0` with additive migration stubs from `1.0.0`.
- Bundle/component registries are compiled and hashed into lockfile validation.

## Flow Engine Behavior

Bundle channel execution path (`quantity_bundle_id` present):
- deterministic component IDs sourced from bundle registry order
- deterministic per-component transfer/loss maps
- optional component capacity/loss policies
- event payloads include `transferred_components` and `lost_components`

Legacy scalar channel path (`quantity_id` only):
- retained as canonical `1.0.0` behavior
- no component maps required
- deterministic ordering and budget behavior unchanged

## Ledger and Conservation Integration

Bundle loss handling now supports deterministic transform semantics:
- per-component `transform_to_quantity_id`
- surfaced `loss_transform_rows` for audit/ledger consumption
- conservation exception surfacing when transforms are required but absent

## Constitutive Model Integration

Constitutive model flow IO now supports bundle components:
- model `flow_adjustment` payload may include `quantity_bundle_id` + `component_quantity_id`
- runtime flow adjustment indexing is bundle/component-aware
- model input resolution supports selectors:
  - `channel:<channel_id>:component:<quantity_id>`
  - `component:<quantity_id>` (with binding context)

## Backward Compatibility Guarantees

Compatibility posture:
- existing `flow_channel` rows with only `quantity_id` remain valid
- existing `flow_transfer_event` rows remain valid
- upgrade is additive; no required pack changes

Adapter helpers for legacy callers:
- `flow_channel_primary_quantity_id(...)`
- `flow_transfer_components(...)`
- `flow_loss_components(...)`

## Enforcement

RepoX scaffold:
- `INV-NO-COUPLED-QUANTITY-HACKS` (warn ratchet)

AuditX analyzers:
- `E181_COUPLED_CHANNEL_HACK_SMELL`
- `E182_BUNDLE_BYPASS_SMELL`

## TestX Coverage Added

Implemented tests:
1. `test_legacy_flow_behavior_unchanged`
2. `test_bundle_transfer_deterministic`
3. `test_component_loss_policy`
4. `test_transform_loss_to_heat`
5. `test_budget_degrade_bundle_channels`
6. `test_model_reads_bundle_components`

## Gate Results

Executed during this baseline:
- RepoX (`python tools/xstack/repox/check.py --repo-root . --profile STRICT`): **REFUSAL**
  - blocked by pre-existing unrelated finding: `INV-NO-RANKED-FLAGS` in `tools/signals/tool_run_sig_stress.py`
- AuditX (`python tools/auditx/auditx.py scan --repo-root . --format both`): **COMPLETE**
- TestX subset (`python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset ...`): **PASS (6/6)**
- Strict build gate (`python scripts/dev/gate.py strict --repo-root . --only-gate build_strict`): **PASS**
- Topology map (`python tools/governance/tool_topology_generate.py --repo-root .`): **PASS**

## Readiness for ELEC Phasor Models

`bundle.power_phasor (P,Q,S)` is now available as first-class flow substrate input/output.
Constitutive model bindings can read/write per-component phasor quantities deterministically without introducing electricity-specific flow hacks.
