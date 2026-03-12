Status: DERIVED
Version: 1.0.0
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Domain Foundation Report

## Validation Result
- result: `complete`
- domains: `10`
- contracts: `7`
- solvers: `2`

## Domains
- `dom.domain.economy.basic` status=`experimental` deprecated=`false` scopes=`local,macro,region` solver_kinds=`coarse,macro_capsule` contracts=`dom.contract.deterministic_transition,dom.contract.ledger_balance`
- `dom.domain.energy.basic` status=`active` deprecated=`false` scopes=`local,macro,region` solver_kinds=`coarse,macro_capsule,refined` contracts=`dom.contract.deterministic_transition,dom.contract.energy_conservation`
- `dom.domain.fluids.basic` status=`active` deprecated=`false` scopes=`local,region` solver_kinds=`coarse,refined` contracts=`dom.contract.deterministic_transition,dom.contract.mass_conservation`
- `dom.domain.geology.terrain` status=`active` deprecated=`false` scopes=`body,local,region` solver_kinds=`coarse,micro,refined` contracts=`dom.contract.mass_conservation,dom.contract.port_contract_preservation`
- `dom.domain.gravity.macro` status=`active` deprecated=`false` scopes=`macro,system` solver_kinds=`coarse,macro_capsule` contracts=`dom.contract.deterministic_transition,dom.contract.mass_conservation`
- `dom.domain.heat.basic` status=`active` deprecated=`false` scopes=`local,region` solver_kinds=`coarse,micro,refined` contracts=`dom.contract.deterministic_transition,dom.contract.energy_conservation`
- `dom.domain.magic.pack` status=`experimental` deprecated=`false` scopes=`local,region` solver_kinds=`micro,refined` contracts=`dom.contract.epistemic_non_omniscience,dom.contract.port_contract_preservation`
- `dom.domain.orbital.mechanics` status=`active` deprecated=`false` scopes=`body,region,system` solver_kinds=`coarse,micro,refined` contracts=`dom.contract.deterministic_transition,dom.contract.energy_conservation,dom.contract.mass_conservation`
- `dom.domain.psych.social` status=`experimental` deprecated=`false` scopes=`local,region` solver_kinds=`coarse` contracts=`dom.contract.deterministic_transition,dom.contract.epistemic_non_omniscience`
- `dom.domain.signals.basic` status=`active` deprecated=`false` scopes=`local,region,system` solver_kinds=`coarse,refined` contracts=`dom.contract.epistemic_non_omniscience,dom.contract.port_contract_preservation`

## Contracts
- `dom.contract.charge_conservation` tags=`charge` refusals=`refusal.contract_violation`
- `dom.contract.deterministic_transition` tags=`determinism` refusals=`refusal.contract_violation`
- `dom.contract.energy_conservation` tags=`energy` refusals=`refusal.contract_violation`
- `dom.contract.epistemic_non_omniscience` tags=`information_access` refusals=`ENTITLEMENT_MISSING,LENS_FORBIDDEN,refusal.contract_violation`
- `dom.contract.ledger_balance` tags=`ledger_balance` refusals=`refusal.contract_violation`
- `dom.contract.mass_conservation` tags=`mass` refusals=`refusal.contract_violation`
- `dom.contract.port_contract_preservation` tags=`port_contract` refusals=`refusal.contract_violation`

## Solver Bindings
- `solver.collapse.macro_capsule` domains=`dom.domain.economy.basic,dom.domain.energy.basic,dom.domain.gravity.macro` contracts=`dom.contract.deterministic_transition,dom.contract.energy_conservation,dom.contract.mass_conservation,dom.contract.port_contract_preservation` transitions=`collapse,expand` resolution_tags=`coarse,macro`
- `solver.expand.local_high_fidelity` domains=`dom.domain.fluids.basic,dom.domain.geology.terrain,dom.domain.heat.basic,dom.domain.orbital.mechanics,dom.domain.signals.basic` contracts=`dom.contract.charge_conservation,dom.contract.deterministic_transition,dom.contract.energy_conservation,dom.contract.mass_conservation,dom.contract.port_contract_preservation` transitions=`collapse,expand` resolution_tags=`micro,refined`

## Errors
- none

## Cross-References
- `docs/scale/DOMAIN_MODEL.md`
- `docs/scale/CONTRACTS_AND_CONSERVATION.md`
- `docs/scale/SOLVER_DOMAIN_BINDINGS.md`
