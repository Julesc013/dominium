Status: DERIVED
Last Reviewed: 2026-03-04
Supersedes: docs/audit/TIER_COUPLING_EXPLAIN_BASELINE.md
Superseded By: none

# META-CONTRACT-1 Hardening Report

## Scope
This report captures META-CONTRACT-1 hard-gate promotion for Tier/Coupling/Explain contracts across existing domains without simulation semantics changes.

Audit scope domains:
- PHYS
- ELEC
- THERM
- FLUID
- MOB
- SIG

## Coverage Table (Before -> After)

| Domain | Tier Contract | Coupling Contract | Explain Contract | Delta Applied |
|---|---|---|---|---|
| PHYS | Complete -> Complete | Partial -> Complete | Missing phys exception events -> Complete | Added `coupling.phys.gravity_to_mob.force`; added `phys.exception_event`, `phys.energy_violation`, `phys.momentum_violation` explain contracts |
| ELEC | Complete -> Complete | Complete -> Complete | Partial -> Complete | Added `elec.fault` explain contract |
| THERM | Complete -> Complete | Complete -> Complete | Partial -> Complete | Added `therm.fire`, `therm.runaway` explain contracts |
| FLUID | Complete -> Complete | Declared -> Complete with pathway metadata | Partial -> Complete | Added `fluid.relief` explain contract; added leak process metadata (`process.start_leak`, `process.leak_tick`) |
| MOB | Complete -> Complete | Partial -> Complete | Partial -> Complete | Added `coupling.field.friction_to_mob.traction`; added `mob.collision`, `mob.signal_violation` explain contracts |
| SIG | Complete -> Complete | Complete -> Complete | Partial -> Complete | Added `sig.jamming`, `sig.decrypt_denied`, `sig.trust_update` explain contracts |

Baseline source snapshot:
- `docs/audit/META_CONTRACT1_RETRO_AUDIT.md`

## Enforcement Changes

### RepoX (STRICT hard fail)
Enabled/confirmed strict blockers:
- `INV-TIER-CONTRACT-REQUIRED`
- `INV-COST-MODEL-REQUIRED`
- `INV-COUPLING-CONTRACT-REQUIRED`
- `INV-EXPLAIN-CONTRACT-REQUIRED`
- `INV-NO-UNDECLARED-COUPLING`

Implementation references:
- `repo/repox/rulesets/core.json`
- `tools/xstack/repox/check.py`
- `docs/governance/REPOX_RULESETS.md`

FAST behavior retained as warn-only via strict-only severity path for meta-contract invariants.

### AuditX (STRICT escalation)
Updated analyzers:
- `E216_MISSING_TIER_CONTRACT_SMELL`
- `E217_UNDECLARED_COUPLING_SMELL`
- `E218_MISSING_EXPLAIN_CONTRACT_SMELL`
- `E226_COST_MODEL_MISSING_SMELL` (new)

Implementation references:
- `tools/auditx/analyzers/e216_missing_tier_contract_smell.py`
- `tools/auditx/analyzers/e217_undeclared_coupling_smell.py`
- `tools/auditx/analyzers/e218_missing_explain_contract_smell.py`
- `tools/auditx/analyzers/e226_cost_model_missing_smell.py`
- `tools/auditx/analyzers/__init__.py`

### TestX hard-gate coverage
Added/updated tests:
- `test_all_domains_have_tier_contract`
- `test_all_couplings_declared`
- `test_all_explain_contracts_present`
- `test_contract_schema_valid`
- `test_explain_artifact_generation_smoke`

Implementation references:
- `tools/xstack/testx/tests/test_all_domains_have_tier_contract.py`
- `tools/xstack/testx/tests/test_all_couplings_declared.py`
- `tools/xstack/testx/tests/test_all_explain_contracts_present.py`
- `tools/xstack/testx/tests/test_contract_schema_valid.py`
- `tools/xstack/testx/tests/test_explain_artifact_generation_smoke.py`

## Explain Engine Coverage Expansion
Deterministic derived adapters added for enforced event families:
- ELEC: `safety_event` + `fault_state`
- THERM: `thermal_overheat` + `heat_loss`
- FLUID: `leak/burst` + pressure vessel threshold refs
- MOB: `derailment` + curvature/wear/speed keys
- SIG: `delivery_loss` + attenuation/jamming/policy keys
- PHYS: `exception_event` + ledger/quantity violation keys

Implementation reference:
- `src/meta/explain/explain_engine.py`

## Topology + Semantic Impact Integration
Contract registries are treated as first-class semantic drivers.

Updated behavior:
- Tier contract changes trigger tier envelope + registry hard-gate suites.
- Coupling contract changes trigger registry hard-gate suites and affected domain suites.
- Explain contract changes trigger explain engine suites.

Implementation reference:
- `tools/governance/tool_semantic_impact.py`

Topology regeneration:
- Command: `python tools/governance/tool_topology_generate.py`
- Result: PASS
- Fingerprint: `70ccf21cd3d9ad0805da0993525740bc6f6c3a1bfd03d89c20276bb12e30528c`

## Gate Runs (2026-03-04)

1) RepoX STRICT
- Command: `python tools/xstack/repox/check.py --profile STRICT`
- Result: PASS
- Notes: `status=pass`, `findings=17` (warn-only in this run)

2) AuditX STRICT
- Command: `python tools/xstack/auditx/check.py --profile STRICT`
- Result: FAIL
- Notes: `findings=1657`, `promoted_blockers=7`
- Primary promoted blocker family observed: `E179_INLINE_RESPONSE_CURVE_SMELL` (pre-existing strict blocker set)

3) TestX hard-gate contract set
- Command: `python tools/xstack/testx/runner.py --profile STRICT --cache off --subset test_all_domains_have_tier_contract,test_all_couplings_declared,test_all_explain_contracts_present,test_contract_schema_valid,test_explain_artifact_generation_smoke`
- Result: PASS
- Notes: `selected_tests=5`

4) Strict build orchestration
- Command: `python scripts/dev/gate.py strict`
- Result: FAIL
- Notes: exited in `repox_runner` under `STRICT_DEEP`; failure class `STRUCTURAL` with pre-existing repo-wide structural/doc/ruleset drift in changed tree.

## Readiness Checklist (Phase A2: Energy/Momentum Sweep)
- [x] Domain coverage backfilled for Tier/Coupling/Explain contracts
- [x] RepoX strict hard-gate rule IDs in place for contract governance
- [x] Explain engine coverage expanded for enforced event families
- [x] Contract topology/semantic-impact integration updated
- [x] Hard-gate TestX coverage added and passing for contract set
- [ ] Repo-wide AuditX STRICT promoted blockers reduced to zero
- [ ] Strict orchestration (`gate.py strict`) green on current workspace

## Summary
META-CONTRACT-1 contract hardening and backfill are implemented and validated for the direct contract governance surface (registries, RepoX rules, Explain coverage, TestX hard-gate tests, topology impact wiring). Repository-wide strict gate closure remains blocked by pre-existing strict structural/audit findings outside this patch scope.
