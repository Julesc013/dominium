Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PHYS0 Retro-Consistency Audit

Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-0 Phase 0 retro-audit of existing physics-adjacent substrate contracts.

## 1) Audit Inputs

Audited artifacts:

- `data/registries/quantity_registry.json`
- `data/registries/quantity_type_registry.json`
- `data/registries/dimension_registry.json`
- `data/registries/unit_registry.json`
- `src/reality/ledger/ledger_engine.py`
- `src/electric/power_network_engine.py`
- `src/thermal/network/thermal_network_engine.py`
- `tools/xstack/sessionx/process_runtime.py`
- `tools/xstack/repox/check.py`

Audit method:

- static registry/schema scan
- invariant wiring scan (RepoX/AuditX)
- deterministic path inspection for loss and cross-domain coupling

## 2) Existing Quantity Types (MAT-1)

Current registry state before PHYS-0 canonicalization:

- present aggregate channels:
  - `quantity.mass_energy_total`
  - `quantity.mass`
  - `quantity.energy`
  - `quantity.charge_total`
  - `quantity.ledger_balance`
  - `quantity.entropy_metric`
- present electrical/thermal stubs:
  - `quantity.power.active_stub`
  - `quantity.power.reactive_stub`
  - `quantity.power.apparent_stub`
  - `quantity.thermal.heat_loss_stub`
  - `quantity.thermal.heat_flow_stub`
  - `quantity.thermal.energy_store_stub`

Dimension registry already includes required PHYS vectors for momentum/force/torque/energy/power/specific-energy, so PHYS-0 can bind canonical quantities without introducing solver logic.

## 3) Existing Ledgers And Conservation Scope (RS-2)

Observed conserved/tracked channels in active contracts:

- conserved by default policy sets:
  - mass-like channels (`quantity.mass`)
  - energy-like channels (`quantity.mass_energy_total`, `quantity.energy`)
  - charge (`quantity.charge_total`)
- tracked diagnostics:
  - entropy-like channel (`quantity.entropy_metric`)
  - domain-specific flow/loss stubs

Current conservation substrate is already ledger-mediated and deterministic; gap is naming/coverage consistency for future PHYS domains.

## 4) Existing Loss Conventions (ELEC/THERM)

Current pattern:

- ELEC loss accounting points at:
  - `quantity.thermal.heat_loss_stub`
  - `effect.temperature_increase_local`
- THERM network tracks heat flow/store as explicit quantities.

Identified inconsistency:

- loss quantity naming remains transitional (`quantity.thermal.heat_loss_stub`) instead of canonical PHYS quantity (`quantity.heat_loss`).

## 5) Cross-Domain Mutation Scan

Findings:

- cross-domain coupling guardrail already present in RepoX (`INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL`).
- no approved architecture path should allow direct ELEC->THERM or THERM->MECH state mutation outside model/effect/process routes.
- existing enforcement is present but PHYS-0 will harden rule naming and strict profile wiring for future domains.

## 6) Implicit Magic / Debug Bypass Scan

Findings:

- explicit physics profile and exception pathways exist in universe/session surfaces.
- gap: no PHYS-scoped exception event schema and profile registry for controlled invariant violations (magic/exotic) across all domains.
- required hardening: violation pathways must emit explicit exception artifacts + ledger entries + proof hooks.

## 7) Migration Notes

PHYS-0 canonicalization path:

1. Introduce canonical PHYS quantities while preserving existing aggregate/stub channels for compatibility.
2. Add canonical physics profile + exception event schemas and profile registries.
3. Promote session/profile declaration invariant to PHYS-scoped strict rule.
4. Upgrade loss mapping invariant to PHYS naming while retaining backward compatibility aliasing during migration window.

## 8) Deprecation Entries (Planned)

The following names are marked transitional and must not be used by new domain integrations:

- `quantity.thermal.heat_loss_stub` -> canonical `quantity.heat_loss`
- `quantity.entropy_metric` -> canonical `quantity.entropy_index`

These are migration/deprecation notes only in PHYS-0; runtime removal is deferred to a compatibility-tagged follow-up once all registry consumers are upgraded.
