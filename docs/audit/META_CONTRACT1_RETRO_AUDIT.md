Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# META-CONTRACT-1 Retro Consistency Audit

Status: BASELINE
Last Updated: 2026-03-04
Scope: Tier/Coupling/Explain hard-gate promotion and backfill audit for existing domains.

## 1) Audit Scope

Domains audited:

- PHYS
- ELEC
- THERM
- FLUID
- MOB
- SIG

Audit checks:

- Tier contract present and complete
- Coupling contract coverage for declared cross-domain dependencies
- Explain contract coverage for major hazard/failure/refusal events
- `cost_model_id` presence in tier declarations
- `deterministic_degradation_order` presence in tier declarations

## 2) Coverage Table (Pre-Backfill Snapshot)

| Domain | Tier Contract Status | Coupling Contract Status | Explain Contract Status | Required Fixes |
|---|---|---|---|---|
| PHYS | Present, complete (`cost_model_id`, `deterministic_degradation_order` present) | Missing explicit gravity->force coupling declaration | Missing PHYS exception explain events | Add PHYS gravity coupling row; add `phys.exception_event`, `phys.energy_violation`, `phys.momentum_violation` explain contracts |
| ELEC | Present, complete (`cost_model_id`, `deterministic_degradation_order` present) | Core ELEC->THERM loss coupling present | Partial (`elec.trip` present; `elec.fault` missing) | Add `elec.fault` explain contract |
| THERM | Present, complete (`cost_model_id`, `deterministic_degradation_order` present) | THERM->MECH strength modifier coupling present | Partial (`therm.overheat` present; `therm.fire` and `therm.runaway` missing) | Add `therm.fire` and `therm.runaway` explain contracts |
| FLUID | Present, complete (`cost_model_id`, `deterministic_degradation_order` present) | FLUID->THERM/INT/MECH declared | Partial (`fluid.leak`, `fluid.overpressure`, `fluid.cavitation`, `fluid.burst` present; `fluid.relief` missing) | Add `fluid.relief` explain contract; annotate leak coupling with process pathway metadata |
| MOB | Present, complete (`cost_model_id`, `deterministic_degradation_order` present) | Missing explicit friction/traction coupling declaration | Partial (`mob.derailment` present; `mob.collision`, `mob.signal_violation` missing) | Add MOB friction->traction coupling row; add MOB collision/signal-violation explain contracts |
| SIG | Present, complete (`cost_model_id`, `deterministic_degradation_order` present) | SIG trust->acceptance coupling present | Partial (`sig.delivery_loss` present; `sig.jamming`, `sig.decrypt_denied`, `sig.trust_update` missing) | Add missing SIG explain contracts |

## 3) Cost Model + Degradation Declaration Audit

Result:

- All baseline tier contracts already declare `cost_model_id`.
- All baseline tier contracts already declare `deterministic_degradation_order`.
- No immediate tier-row schema gaps detected in baseline rows.

Hardening needed:

- Promote explicit RepoX hard gate for missing `cost_model_id` so future domains/process families cannot omit cost binding.

## 4) Remediation Summary

1. Backfill coupling registry for PHYS gravity and MOB friction/traction declaration.
2. Backfill explain registry for ELEC/THERM/FLUID/MOB/SIG/PHYS event coverage.
3. Promote cost-model requirement to strict hard fail in RepoX.
4. Escalate contract smell severity in strict governance path via AuditX analyzers.
5. Add TestX hard-gate tests for explain coverage + contract schema validation + explain generation smoke.
