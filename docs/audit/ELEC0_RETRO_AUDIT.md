Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# ELEC-0 Retro Consistency Audit

Date: 2026-03-03
Scope: Existing power/electrical-like behavior and migration readiness for ELEC-0.

## 1) Existing Electrical Or Power-Like Systems

Observed power-like substrate hooks already present:

- [data/registries/constitutive_model_registry.json](/d:/Projects/Dominium/dominium/data/registries/constitutive_model_registry.json)
  - Includes electrical constitutive stub: `model.elec.load.phasor.default`.
  - Uses `model_type.elec_load_phasor_stub` and emits `derived.elec.power_factor`.
- [schema/core/flow_channel.schema](/d:/Projects/Dominium/dominium/schema/core/flow_channel.schema) and [schema/core/quantity_bundle.schema](/d:/Projects/Dominium/dominium/schema/core/quantity_bundle.schema)
  - Already support bundle-capable flow channels and `bundle.power_phasor`.
- [data/registries/component_capacity_policy_registry.json](/d:/Projects/Dominium/dominium/data/registries/component_capacity_policy_registry.json)
  - Contains `comp_capacity.power_phasor_stub`.

Conclusion: foundational multi-quantity flow substrate exists; ELEC-0 should formalize governance and topology/policy contracts, not add bespoke runtime.

## 2) Energy Hacks Embedded In Machine Operation

Observed legacy scalar energy placeholders:

- [data/registries/machine_operation_registry.json](/d:/Projects/Dominium/dominium/data/registries/machine_operation_registry.json)
  - Uses `energy_delta_raw` scalar per operation.
- [src/machines/port_engine.py](/d:/Projects/Dominium/dominium/src/machines/port_engine.py)
  - Normalizes/consumes operation `energy_delta_raw`.

Assessment:

- This is deterministic and process-compatible, but not yet represented as electrical networked flow (`P/Q/S`) through Flow bundles.
- Migration target is to treat these operation values as demand/supply intents that bind to ELEC channels and constitutive models, instead of ad-hoc machine-local accounting.

## 3) Breaker/Overload Logic Outside SAFETY Patterns

Observed safety substrate coverage:

- [src/safety/safety_engine.py](/d:/Projects/Dominium/dominium/src/safety/safety_engine.py)
  - Canonical safety pattern types include `breaker`.
- [data/registries/safety_pattern_registry.json](/d:/Projects/Dominium/dominium/data/registries/safety_pattern_registry.json)
  - Contains baseline template(s) for breaker trip semantics.

Observed domain docs still referencing legacy power stubs:

- [docs/specs/SPEC_NETWORKS.md](/d:/Projects/Dominium/dominium/docs/specs/SPEC_NETWORKS.md)
- [docs/specs/SPEC_DOMINIUM_RULES.md](/d:/Projects/Dominium/dominium/docs/specs/SPEC_DOMINIUM_RULES.md)

No authoritative Python-domain electrical breaker bypass implementation was found in current `src/` beyond SAFETY substrate declarations.

## 4) Migration Plan To ELEC Series

1. Establish electrical constitution and tier contract (E0/E1/E2) as governance baseline.
2. Register electrical network kinds (nodes/edges), model IDs, and spec templates as data-only skeletons.
3. Route protection semantics through SAFETY pattern instances (`breaker`, `failsafe`, `interlock`, `loto`) only.
4. Move machine-local scalar `energy_delta_raw` usage toward bundle-aware flow bindings over time:
   - E0: continue scalar bookkeeping, but declare migration target.
   - E1+: map to `bundle.power_phasor` and constitutive model outputs.
5. Add enforcement to block ad-hoc PF and breaker logic in domain code.

## 5) Determinism Notes

- No wall-clock dependencies identified in audited electrical-like paths.
- Existing stubs are deterministic and auditable.
- ELEC-0 can proceed as governance/documentation/enforcement without runtime semantic change.
