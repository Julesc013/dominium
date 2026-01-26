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

## Canonical units (initial)
```units
# unit_id, dimension, base_unit, scale, notes
unit.time.act_tick, time, unit.time.act_tick, 1, authoritative ACT tick
unit.length.meter, length, unit.length.meter, 1000000, fixed-point micrometers
unit.mass.kilogram, mass, unit.mass.kilogram, 1000000, fixed-point micro-kg
unit.temperature.kelvin, temperature, unit.temperature.kelvin, 1000, fixed-point milli-kelvin
unit.energy.joule, energy, unit.energy.joule, 1000, fixed-point milli-joule
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

## Enforcement
- Unit tables are schema-validated and tested for consistency.
- Unit ids are immutable; new units require new ids.

## See also
- `schema/measurement_artifact.schema`
- `docs/arch/REFUSAL_SEMANTICS.md`
- `docs/arch/NAMESPACING_RULES.md`
