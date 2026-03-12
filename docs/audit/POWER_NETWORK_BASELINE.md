Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Power Network Baseline

Status: BASELINE
Series: ELEC-1
Date: 2026-03-03

## Scope

ELEC-1 delivers a deterministic meso electrical network baseline using existing substrates:

- `NetworkGraph` for topology (`PowerNetworkGraph` payloads)
- `FlowSystem` bundle channels (`bundle.power_phasor`)
- `ConstitutiveModels` for load/loss stubs
- `SAFETY` patterns for breaker protection
- `SPEC` for connector/rating validation

No waveform tier (E2) is introduced.

## Phasor Approximation (E1)

Per network tick (deterministic ordering):

1. collect node demand from bound load models
2. derive per-edge component flows (`P/Q/S`) with capacity clamping
3. apply deterministic line-loss proxy from `resistance_proxy`
4. publish per-edge flow state + derived metrics (`V/I/PF` stubs)

If budget denies E1 processing, network falls back to E0 macro active-power mode and logs downgrade metadata.

## Loss Model

Line loss is modeled by a deterministic proxy:

- load factor from apparent power vs capacity
- resistance scale from edge payload
- loss deducted from active component (`P`)
- loss amount exposed as `heat_loss_stub` for THERM hook

## Breaker Logic

Over-capacity handling is mediated via SAFETY patterns:

- overload predicate on channel/edge load
- `safety.breaker_trip` emits `flow_disconnect`
- channel is de-energized through process-mediated flow adjustment/disconnect state

No direct breaker state mutation is allowed outside process/safety paths.

## Tier Fallback

- E1: `P/Q/S` bundle solve (preferred)
- E0: deterministic fallback (`P` only) under budget pressure

Fallback decisions are deterministic and captured in runtime/decision metadata.

## Extension Notes (E2)

Future ELEC-2 waveform tier can attach by:

- adding micro-tier constitutive models
- preserving `PowerNetworkGraph` and bundle interfaces
- keeping process-only mutation and deterministic ordering unchanged

## Gate Summary

This baseline requires:

- RepoX pass
- AuditX run
- TestX pass (ELEC-1 tests)
- strict build pass
- topology map update

Execution run status (2026-03-03):

- RepoX (`python tools/xstack/repox/check.py --profile FAST`):
  - `status=fail` due pre-existing non-ELEC finding in `tools/signals/tool_run_sig_stress.py` (`INV-NO-RANKED-FLAGS`).
  - ELEC-1-specific invariants executed: `INV-POWER-FLOW-THROUGH-BUNDLE`, `INV-BREAKER-THROUGH-SAFETY`.
- AuditX (`python tools/auditx/auditx.py scan --repo-root . --changed-only --format both`):
  - `result=scan_complete`.
  - analyzers include ELEC-1 additions:
    - `E185_INLINE_POWER_LOSS_SMELL`
    - `E186_DIRECT_FLOW_MUTATION_SMELL`
- TestX (`python tools/xstack/testx/runner.py --profile FAST --cache off --subset ...`):
  - `status=pass` for:
    - `test_power_flow_deterministic`
    - `test_pf_calculation`
    - `test_line_loss_applied`
    - `test_breaker_trip_on_overload`
    - `test_budget_fallback_to_E0`
    - `test_spec_refusal`
- strict build (`python tools/xstack/run.py strict --repo-root . --cache on`):
  - `result=refusal` with pre-existing global pipeline findings (CompatX/registry/session/test/packaging) outside ELEC-1 scope.
- topology map (`python tools/governance/tool_topology_generate.py --repo-root .`):
  - updated: `docs/audit/TOPOLOGY_MAP.json`, `docs/audit/TOPOLOGY_MAP.md`
  - fingerprint: `742df7742c9c15973bca0e181060097b3af223b7cd2d1686edcebec36dbca2a1`
