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
unit.readiness.level, readiness, unit.readiness.level, 1, symbolic readiness level (0..1)
unit.morale.level, morale, unit.morale.level, 1, symbolic morale level (0..1)
unit.morale.decay_per_tick, morale_rate, unit.morale.decay_per_tick, 1, morale decay per ACT tick
unit.force.capacity, force_capacity, unit.force.capacity, 1, symbolic force capacity units
unit.order.key, ordering, unit.order.key, 1, deterministic ordering key
unit.weapon.rate_per_tick, weapon_rate, unit.weapon.rate_per_tick, 1, symbolic weapon rate per ACT tick
unit.institution.enforcement_capacity, institution_capacity, unit.institution.enforcement_capacity, 1, symbolic enforcement capacity
unit.institution.resource_budget, institution_budget, unit.institution.resource_budget, 1, symbolic enforcement/resource budget
unit.institution.capacity_limit, institution_capacity, unit.institution.capacity_limit, 1, symbolic capacity limit
unit.knowledge.confidence, knowledge, unit.knowledge.confidence, 1, symbolic knowledge confidence (0..1)
unit.knowledge.decay_per_tick, knowledge_rate, unit.knowledge.decay_per_tick, 1, knowledge decay per ACT tick
unit.skill.variance_reduction, skill, unit.skill.variance_reduction, 1, symbolic variance reduction (0..1)
unit.skill.failure_bias_reduction, skill, unit.skill.failure_bias_reduction, 1, symbolic failure bias reduction (0..1)
unit.skill.decay_per_tick, skill_rate, unit.skill.decay_per_tick, 1, skill decay per ACT tick
unit.history.confidence, history, unit.history.confidence, 1, symbolic history confidence (0..1)
unit.history.uncertainty, history, unit.history.uncertainty, 1, symbolic history uncertainty (0..1)
unit.history.bias, history, unit.history.bias, 1, symbolic history bias magnitude (0..1)
unit.history.decay_per_tick, history_rate, unit.history.decay_per_tick, 1, history decay per ACT tick
unit.history.myth_weight, history, unit.history.myth_weight, 1, symbolic myth amplification weight (0..1)
unit.standard.adoption_rate, standard, unit.standard.adoption_rate, 1, symbolic standard adoption rate (0..1)
unit.standard.compliance_rate, standard, unit.standard.compliance_rate, 1, symbolic standard compliance rate (0..1)
unit.standard.lock_in_index, standard, unit.standard.lock_in_index, 1, symbolic standard lock-in index (0..1)
unit.standard.compatibility_score, standard, unit.standard.compatibility_score, 1, symbolic standard compatibility score (0..1)
unit.standard.enforcement_level, standard, unit.standard.enforcement_level, 1, symbolic standard enforcement level (0..1)
unit.toolchain.capacity, toolchain_capacity, unit.toolchain.capacity, 1, symbolic toolchain capacity units
unit.autonomy.priority, autonomy, unit.autonomy.priority, 1, symbolic autonomy priority (0..1)
unit.autonomy.planning_budget, autonomy_budget, unit.autonomy.planning_budget, 1, symbolic planning budget units
unit.dimensionless.ratio, dimensionless, unit.dimensionless.ratio, 1, unitless ratio/weight
unit.pressure.pascal, pressure, unit.pressure.pascal, 1000, fixed-point milli-pascal
unit.currency.credit, currency, unit.currency.credit, 100, fixed-point centi-credits
unit.resource.symbol, resource, unit.resource.symbol, 1, symbolic resource unit
unit.logistics.decay_per_tick, logistics_rate, unit.logistics.decay_per_tick, 1, symbolic spoilage/decay per ACT tick
unit.market.price, market_price, unit.market.price, 1, symbolic local price unit
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
