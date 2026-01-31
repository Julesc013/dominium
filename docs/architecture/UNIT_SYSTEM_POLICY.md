# Unit System Policy (UNIT0)

Status: binding.
Scope: canonical units, fixed-point scaling, conversion, and overflow behavior.

## Purpose
Guarantee deterministic, portable unit handling across all systems.

## Core rules
- All quantities are fixed-point integers with explicit scale.
- All unit identifiers are namespaced and stable.
- Conversions are deterministic and rational (no floating point).
- Unknown units MUST be refused or preserved, never guessed.
- Schemas MUST include unit tags for unit-bearing fields.
- Authoritative logic MUST NOT use floating point arithmetic.
- Presentation layers may use floating point only for display.

## Numeric policy (binding)
- Quantities are stored as integers plus a declared unit scale.
- Unit scales are powers of ten unless a schema explicitly declares otherwise.
- Ordering, comparisons, and budgets operate on integer quantities.
- Floating point values MUST be converted to fixed-point before admission.

## Canonical units (initial)
```units
# unit_id, dimension, base_unit, scale, notes
unit.time.act_tick, time, unit.time.act_tick, 1, authoritative ACT tick
unit.length.meter, length, unit.length.meter, 1000000, fixed-point micrometers
unit.volume.m3, volume, unit.volume.m3, 1000000, fixed-point micro-cubic-meter
unit.mass.kilogram, mass, unit.mass.kilogram, 1000000, fixed-point micro-kg
unit.temperature.kelvin, temperature, unit.temperature.kelvin, 1000, fixed-point milli-kelvin
unit.energy.joule, energy, unit.energy.joule, 1000, fixed-point milli-joule
unit.data.symbol, data, unit.data.symbol, 1, symbolic data units
unit.data.symbol_per_tick, data_rate, unit.data.symbol_per_tick, 1, symbolic data units per ACT tick
unit.hazard.intensity, hazard, unit.hazard.intensity, 1, symbolic hazard intensity (0..1)
unit.hazard.exposure, hazard, unit.hazard.exposure, 1, symbolic hazard exposure accumulation
unit.hazard.exposure_per_tick, hazard_rate, unit.hazard.exposure_per_tick, 1, symbolic hazard exposure per ACT tick
unit.hazard.decay_per_tick, hazard_rate, unit.hazard.decay_per_tick, 1, symbolic hazard decay per ACT tick
unit.risk.impact, risk, unit.risk.impact, 1, symbolic loss/impact units
unit.risk.exposure, risk, unit.risk.exposure, 1, symbolic risk exposure accumulation
unit.risk.exposure_per_tick, risk_rate, unit.risk.exposure_per_tick, 1, symbolic risk exposure per ACT tick
unit.trust.level, trust, unit.trust.level, 1, symbolic trust level (0..1)
unit.trust.decay_per_tick, trust_rate, unit.trust.decay_per_tick, 1, trust decay per ACT tick
unit.reputation.score, reputation, unit.reputation.score, 1, symbolic reputation score (0..1)
unit.reputation.incident_rate, reputation_rate, unit.reputation.incident_rate, 1, symbolic incident rate (0..1)
unit.legitimacy.compliance_rate, legitimacy_rate, unit.legitimacy.compliance_rate, 1, symbolic compliance rate (0..1)
unit.legitimacy.challenge_rate, legitimacy_rate, unit.legitimacy.challenge_rate, 1, symbolic challenge rate (0..1)
unit.legitimacy.symbolic_support, legitimacy, unit.legitimacy.symbolic_support, 1, symbolic legitimacy support (0..1)
unit.dimensionless.ratio, dimensionless, unit.dimensionless.ratio, 1, unitless ratio/weight
unit.pressure.pascal, pressure, unit.pressure.pascal, 1000, fixed-point milli-pascal
unit.currency.credit, currency, unit.currency.credit, 100, fixed-point centi-credits
```

## Conversion rules
- Convert only through base units.
- Apply scale as integer multiplication/division with deterministic rounding.
- Rounding rule: round toward zero.
- If conversion would overflow, refuse.

## Overflow behavior
- Overflow is a refusal with REFUSE_INVALID_INTENT.
- No silent saturation.

## Tolerance annotations
Tolerances must be explicit and unit-aware:
- A tolerance MUST reference a tolerance identifier and a unit identifier.
- Tolerance magnitudes are expressed in canonical fixed-point units.
- If a tolerance is not declared, exact equality is required.
- Tolerances MUST NOT be evaluated using floating point in authoritative code.

Tolerance policy is defined in:
- `docs/architecture/INVARIANTS_AND_TOLERANCES.md`

## Enforcement
- Unit tables are schema-validated and tested for consistency.
- Unit ids are immutable; new units require new ids.

## See also
- `schema/measurement_artifact.schema`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/NAMESPACING_RULES.md`
