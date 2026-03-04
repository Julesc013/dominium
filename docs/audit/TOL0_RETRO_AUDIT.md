# TOL-0 Retro Consistency Audit

Date: 2026-03-05
Scope: Global deterministic numeric discipline baseline for authoritative simulation math.

## Method

- Scanned quantity registries:
  - `data/registries/quantity_registry.json`
  - `data/registries/quantity_type_registry.json`
- Scanned runtime/model math for division, rounding, conservation checks, and float usage across:
  - `src/`
  - `tools/xstack/sessionx/`
  - `tools/xstack/repox/`
  - `tools/auditx/`
- Focused on authoritative paths:
  - momentum/velocity derivation
  - energy and conservation ledgers
  - field/time mapping updates
  - threshold checks used for refusal/safety outcomes

## Findings

### Quantity declarations and tolerance coverage

- Status: `missing tolerance`
- Current state:
  - Quantity dimension/type declarations are explicit in `quantity_type_registry`.
  - No per-quantity tolerance/rounding/overflow policy registry exists.
- Impact:
  - Conservation and threshold checks rely on local or contract-specific tolerance values instead of quantity-level canonical policy.

### Division and scaling in authoritative model/runtime paths

- Status: `implicit rounding`
- Current state:
  - Integer division helpers exist in motion/momentum code (`_div_toward_zero`).
  - Some scaling paths still rely on local ad hoc behavior rather than a single shared deterministic rounding policy utility.

### Float usage in authoritative temporal mapping path

- Status: `implicit rounding`
- Current state:
  - `src/time/time_mapping_engine.py` uses float conversion + `round()` for drift multiplication.
- Impact:
  - Violates strict fixed-point-only policy target for invariant math.
  - Increases cross-platform behavior risk.

### Equality/threshold comparisons

- Status: `implicit rounding`
- Current state:
  - Conservation checks are deterministic but use contract-set tolerance values (`conservation_contract_set`) without quantity-level default fallback.
  - Overpressure/overtemp/trip thresholds are deterministic but not backed by unified quantity tolerance metadata.

### Conservation checks

- Status: `implicit rounding`
- Current state:
  - `src/reality/ledger/ledger_engine.py` and `src/physics/energy/energy_ledger_engine.py` enforce conservation with explicit integer checks.
  - No canonical quantity tolerance lookup integrated into these checks.

### Overflow handling

- Status: `implicit rounding`
- Current state:
  - No global quantity-level overflow policy table for authoritative quantities.
  - Overflow behavior is mostly implicit by Python integer semantics in current runtime math.

## Classification Summary

- `compliant (explicit rounding)`:
  - Deterministic ordering and integer-only accumulation in most ledger/momentum paths.
- `implicit rounding`:
  - Ad hoc division/scaling rules outside a shared quantity-driven rounding helper.
  - Float-based drift multiplication in time mapping path.
- `missing tolerance`:
  - No canonical `quantity_tolerance_registry` and `model_residual_policy_registry`.

## Migration Notes

- Introduce canonical registries:
  - `quantity_tolerance_registry`
  - `model_residual_policy_registry`
- Add deterministic shared rounding helper:
  - quantity-aware operation mode (division/scaling/compare).
- Wire conservation checks to quantity tolerance fallback:
  - contract tolerance remains first-class, quantity tolerance supplies default floor.
- Ban raw float in authoritative invariant math with hard RepoX/AuditX guards.
