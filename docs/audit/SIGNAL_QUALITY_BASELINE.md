Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SIGNAL_QUALITY_BASELINE

Status: BASELINE  
Last Updated: 2026-03-03  
Scope: SIG-3 deterministic attenuation, interference, corruption, and jamming.

## 1) Attenuation Model

- Added first-class signal quality contracts:
  - `schema/signals/attenuation_policy.schema`
  - `schema/signals/jamming_effect.schema`
- Loss policies now reference attenuation policies via `attenuation_policy_id`.
- Transport quality evaluation remains centralized in:
  - `src/signals/transport/transport_engine.py`
  - `src/signals/transport/channel_executor.py`
- Delivery outcomes remain constrained to:
  - `delivered`
  - `lost`
  - `corrupted`

## 2) RNG Usage Policy

- Deterministic RNG remains named-stream only for policies with `uses_rng_stream=true`.
- Deterministic loss rolls are derived from stable materialized tuples:
  - stream name
  - channel id
  - envelope id
  - queue key
  - tick
- Non-RNG attenuation/loss paths remain pure deterministic functions.

## 3) FIELD Integration

- Added deterministic FIELD modifier path in transport quality execution:
  - visibility
  - radiation
  - wind (stub weighting)
- Field samples are consumed through deterministic node-scoped sample input and cache:
  - cache key: `(tick, node_id)` string token
  - cache surfaced in transport output for inspection/debug
- Channel-specific defaults:
  - optical channels bias visibility attenuation
  - radio channels bias radiation/wind attenuation

## 4) Jamming Semantics

- Added process helpers:
  - `process_signal_jam_start`
  - `process_signal_jam_stop`
- Added deterministic jamming effect lifecycle:
  - start/end ticks
  - strength modifier
  - per-channel active effect selection
- Session runtime now routes these processes through authority-gated process dispatch.
- Jamming contributes explicitly to quality outcomes and delivery event metadata.

## 5) Corruption Semantics

- Artifact payload remains canonical and unchanged.
- Corruption is represented in transport delivery state + event metadata:
  - `delivery_state = corrupted`
  - `extensions.corrupted_view = true`
- No silent corruption path: corrupted outcomes remain event logged.

## 6) UX and Inspection Integration

- Added inspection section:
  - `section.signal.quality_summary`
- Exposes deterministic coarse diegetic indicators:
  - radio static indicator
  - line noisy flag
  - jammer detected flag
- Overlay summary includes signal quality bucket and static status.

## 7) Enforcement

RepoX additions:
- `INV-LOSS-POLICY-REGISTERED`
- `INV-NO-DIRECT-MESSAGE-DROP`

AuditX additions:
- `E170_ADHOC_LOSS_SMELL` (`AdHocLossSmell`)
- `E171_SILENT_CORRUPTION_SMELL` (`SilentCorruptionSmell`)

## 8) TestX Coverage (SIG-3)

Added and passing:
1. `testx.signals.attenuation_deterministic_no_rng`
2. `testx.signals.attenuation_deterministic_with_named_rng`
3. `testx.signals.field_scaled_loss_effect`
4. `testx.signals.jamming_increases_loss`
5. `testx.signals.corruption_logged`
6. `testx.signals.replay_stability_under_loss`

## 9) Gate Results (2026-03-03)

1. RepoX
- Command: `python tools/xstack/repox/check.py --repo-root . --profile FAST`
- Result: `status=pass` (warning findings present, including topology declaration warnings resolved by topology update pass)

2. AuditX
- Command: `python tools/xstack/auditx/check.py --repo-root . --profile FAST`
- Result: `status=pass` (repository-level warning findings remain)

3. TestX (SIG-3 subset)
- Command: `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.signals.attenuation_deterministic_no_rng,testx.signals.attenuation_deterministic_with_named_rng,testx.signals.field_scaled_loss_effect,testx.signals.jamming_increases_loss,testx.signals.corruption_logged,testx.signals.replay_stability_under_loss`
- Result: `status=pass` (6 selected, 6 passed)

4. strict build
- Command: `python tools/xstack/run.py --repo-root . --skip-testx strict`
- Result: `status=refusal` due pre-existing strict gate failures outside SIG-3 scope (`compatx` findings and packaging lab-build refusal)

5. topology map update
- Command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- Result: `complete` (`node_count=2605`, `edge_count=146510`, fingerprint `df36912b9a97c926f542b28a73c54a4bf0808ca6b76a65ef04d5a56ae74554ae`)

## 10) Extension Notes

- SIG-4 (encryption/auth):
  - quality layer remains transport metadata-level and does not alter artifact payload.
- SIG-5 (trust graph):
  - corrupted/lost outcomes remain explicit inputs for receipt/trust weighting policies.
- Future RF/propagation domains:
  - can extend attenuation policy registry and deterministic function IDs without transport refactor.
