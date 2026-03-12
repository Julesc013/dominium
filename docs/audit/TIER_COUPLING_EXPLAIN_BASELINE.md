Status: DERIVED
Last Reviewed: 2026-03-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Tier/Coupling/Explain Contracts Baseline

## Coverage Summary
- Tier contract registry present at `data/registries/tier_contract_registry.json` with baseline subsystem entries for `ELEC`, `THERM`, `MOB`, `SIG`, and `PHYS`.
- Coupling contract registry present at `data/registries/coupling_contract_registry.json` with baseline couplings for:
  - `ELEC -> THERM` (`energy_transform`)
  - `FIELD -> THERM` (`constitutive_model`)
  - `THERM -> MECH` (`constitutive_model`)
  - `SIG -> SIG` trust/acceptance (`signal_policy`)
- Explain contract registry present at `data/registries/explain_contract_registry.json` with baseline event coverage for:
  - `elec.trip`
  - `therm.overheat`
  - `mob.derailment`
  - `sig.delivery_loss`
  - `mech.fracture`
- Deterministic explain artifact engine integrated at `src/meta/explain/explain_engine.py` (derived-only, cache-keyed, redaction-aware).

## Enforcement Readiness
- RepoX STRICT invariants added:
  - `INV-TIER-CONTRACT-REQUIRED`
  - `INV-COUPLING-CONTRACT-REQUIRED`
  - `INV-EXPLAIN-CONTRACT-REQUIRED`
  - `INV-NO-UNDECLARED-COUPLING`
- AuditX analyzers added:
  - `E216_MISSING_TIER_CONTRACT_SMELL`
  - `E217_UNDECLARED_COUPLING_SMELL`
  - `E218_MISSING_EXPLAIN_CONTRACT_SMELL`
- TestX coverage added:
  - `test_all_domains_have_tier_contract`
  - `test_all_couplings_declared`
  - `test_explain_artifact_deterministic`
  - `test_explain_redaction_policy`
  - `test_registry_schema_valid`

## Topology Integration
- Topology generator now emits tier/coupling/explain contract nodes and contract-to-domain edges.
- Semantic impact planner now maps contract-registry changes to affected domain suites.
- Updated topology artifacts:
  - `docs/audit/TOPOLOGY_MAP.json`
  - `docs/audit/TOPOLOGY_MAP.md`
  - latest deterministic fingerprint: `49b4e172853fe394230fd716cfc329f9981023c9b70934892b27672029ce0ade`

## Gate Results (2026-03-04)
- RepoX STRICT: `PASS` (`tools/xstack/repox/check.py --profile STRICT`)
- AuditX STRICT: `FAIL` (`tools/xstack/auditx/check.py --profile STRICT`)
  - promoted blockers reported: `7`
  - blocker class observed in run output: `E179_INLINE_RESPONSE_CURVE_SMELL` (pre-existing)
- TestX STRICT: `FAIL` (`tools/xstack/testx/runner.py --profile STRICT`)
  - failing tests in run output: `146`
  - dominant failures are pre-existing session/bootstrap/packaging and unrelated runtime regressions
- Strict profile orchestration (`tools/xstack/run.py strict --cache on`): `REFUSAL`
  - notable blocking steps: `01.compatx.check`, `07.session_boot.smoke`, `09.auditx.scan`, `10.testx.run`, `13.packaging.verify`

## Gaps
- No baseline contract coverage gaps found in required META-CONTRACT0 registries.
- Repository-wide strict gate instability remains outside this patch scope and blocks full STRICT green status.

## Readiness for FLUID-0
- Structural contract substrate is in place for tier/coupling/explain declarations.
- New domain onboarding can now be mechanically gated by RepoX/AuditX/TestX contract checks.
- Full strict readiness still depends on resolving existing non-META-CONTRACT gate failures listed above.
