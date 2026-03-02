Status: AUDIT
Scope: SIG-3 deterministic signal quality (attenuation, noise, interference, jamming)
Date: 2026-03-03

# SIG3 Retro Audit

## Audit Scope
- `src/signals/transport/transport_engine.py`
- `src/signals/transport/channel_executor.py`
- `schema/signals/loss_policy.schema`
- `data/registries/loss_policy_registry.json`
- `data/registries/signal_channel_policy_registry.json`
- `tools/xstack/repox/check.py`

## Findings

### F1 - Loss policy exists but attenuation policy is not first-class
- `loss_policy` rows currently embed attenuation knobs only under `parameters`.
- There is no canonical `attenuation_policy` schema/registry contract.
- Impact: attenuation/noise semantics are harder to inspect, reuse, and extend.

### F2 - Field attenuation hook is currently tag-only
- `channel_executor` computes `field_loss_modifier_permille` from edge tags.
- No deterministic FieldLayer cache path is available in SIG transport yet.
- Impact: FIELD integration exists as a stub, but not as a canonical sampled input model.

### F3 - Jamming has no explicit signal process path
- No `process.signal_jam_start` / `process.signal_jam_stop` transport process helpers exist.
- Impact: interference can only be modeled by static policy configuration, not explicit process-driven effects.

### F4 - Corruption state exists but quality metadata is limited
- `delivery_state` supports `corrupted`, but policy/rationale metadata is minimal.
- Impact: replay can show state outcome, but debugging root-cause quality factors is weak.

### F5 - RepoX/AuditX quality-specific enforcement is missing
- Existing checks cover transport-only and routing/capacity ordering.
- Missing explicit checks for:
  - registered loss policy usage only
  - no direct message-drop logic outside transport
  - no silent corruption paths

## Ad-Hoc Flags and Bypasses
- No standalone ad-hoc `radio_down` flag found in signal runtime.
- No direct artifact corruption mutation path found outside SIG transport in audited files.

## Migration Plan
1. Add authoritative SIG-3 docs for attenuation/noise/corruption/jamming contracts.
2. Add `attenuation_policy` and `jamming_effect` schemas and registries.
3. Extend loss policy contract to reference attenuation policy IDs.
4. Extend `channel_executor` and `transport_engine` for deterministic quality outcomes, explicit corruption metadata, and jamming modifiers.
5. Add deterministic field-sampled attenuation inputs (cached per tick+node).
6. Add process helpers for jamming start/stop with deterministic fingerprints.
7. Add inspection section for signal quality summary.
8. Add RepoX/AuditX enforcement for ad-hoc loss/drop/corruption bypasses.
9. Add SIG-3 TestX coverage for deterministic attenuation, RNG policy behavior, field scaling, jamming, corruption logging, and replay stability.
