Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to Prompt 15 structural domain foundation artifacts.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Domain Foundation Report

## Scope
Final audit report for Domain + Contract + Solver registry foundation formalization.

## Domain List
- `dom.domain.gravity.macro` (active)
- `dom.domain.orbital.mechanics` (active)
- `dom.domain.geology.terrain` (active)
- `dom.domain.fluids.basic` (active)
- `dom.domain.energy.basic` (active)
- `dom.domain.heat.basic` (active)
- `dom.domain.signals.basic` (active)
- `dom.domain.economy.basic` (experimental)
- `dom.domain.psych.social` (experimental)
- `dom.domain.magic.pack` (experimental, pack-gated)

## Contract List
- `dom.contract.mass_conservation`
- `dom.contract.energy_conservation`
- `dom.contract.charge_conservation`
- `dom.contract.ledger_balance`
- `dom.contract.epistemic_non_omniscience`
- `dom.contract.deterministic_transition`
- `dom.contract.port_contract_preservation`

## Solver Bindings Matrix
- `solver.collapse.macro_capsule`
  - domains: `dom.domain.gravity.macro`, `dom.domain.energy.basic`, `dom.domain.economy.basic`
  - contracts: `dom.contract.mass_conservation`, `dom.contract.energy_conservation`, `dom.contract.deterministic_transition`, `dom.contract.port_contract_preservation`
  - transition_support: `collapse`, `expand`
- `solver.expand.local_high_fidelity`
  - domains: `dom.domain.orbital.mechanics`, `dom.domain.geology.terrain`, `dom.domain.fluids.basic`, `dom.domain.heat.basic`, `dom.domain.signals.basic`
  - contracts: `dom.contract.mass_conservation`, `dom.contract.energy_conservation`, `dom.contract.charge_conservation`, `dom.contract.deterministic_transition`, `dom.contract.port_contract_preservation`
  - transition_support: `expand`, `collapse`

## Active vs Experimental
- Active domains: 7
- Experimental domains: 3
- Deprecated domains: 0

## Enforcement Summary
- Domain/contract/solver cross-link validation implemented in `tools/domain/tool_domain_validate.py`.
- Deterministic JSON/Markdown reporting implemented in `tools/domain/tool_domain_report.py`.
- Runtime structural guards enforce transition support with deterministic refusal:
  - `refusal.contract_violation`
  - `refusal.solver_unbound`
- RepoX invariants enforced:
  - `INV-DOMAIN-REGISTRY-VALID`
  - `INV-SOLVER-DOMAIN-BINDING`
  - `INV-NO-HARDCODED-DOMAIN-TOKENS`
  - `INV-CONTRACT-ID-STABILITY`

## Known Extension Points
- Add new domain rows through `data/registries/domain_registry.json` only.
- Add new contract rows through `data/registries/domain_contract_registry.json` only.
- Add or evolve solver rows through `data/registries/solver_registry.json` with explicit `domain_ids`, `contract_ids`, `transition_support`.
- Bump schema versions + CompatX entries for any breaking shape changes.

## Cross-References
- `docs/scale/DOMAIN_MODEL.md`
- `docs/scale/CONTRACTS_AND_CONSERVATION.md`
- `docs/scale/SOLVER_DOMAIN_BINDINGS.md`
- `docs/scale/DOMAIN_REGISTRY.md`
- `docs/audit/DOMAIN_REGISTRY_REPORT.md`
