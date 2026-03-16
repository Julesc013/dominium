Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GLOBAL Contract Coverage Audit

Date: 2026-03-05
Scope: `PHYS, TEMP, TOL, PROV, META-ACTION, META-INFO, RWAM, SAFETY, META-MODEL, CTRL, ABS, MOB, SIG, ELEC, THERM, FLUID, CHEM, FIELD, MECH, INT`

## Method
- Audited contract registries:
  - `data/registries/tier_contract_registry.json`
  - `data/registries/coupling_contract_registry.json`
  - `data/registries/explain_contract_registry.json`
- Verified hard-gate contract tests:
  - `test_all_domains_have_tier_contract`
  - `test_all_couplings_declared`
  - `test_all_explain_contracts_present`
  - `test_contract_schema_valid`

## Coverage Table
| Subsystem | Tier Contract | Coupling Declared | Explain Contract | Cost Model Declared | Required Fixes |
| --- | --- | --- | --- | --- | --- |
| PHYS | yes | yes | yes | `cost.physics.default` | none |
| TEMP | yes | n/a (no cross-domain mutation surface) | n/a (no direct fault family emitted) | `cost.signal.default` | none |
| TOL | yes | n/a (governance-only) | n/a (governance-only) | `cost.physics.default` | none |
| PROV | yes | n/a (governance-only) | n/a (governance-only) | `cost.signal.default` | none |
| META-ACTION (`META_ACTION`) | yes | n/a (grammar/governance-only) | n/a (grammar/governance-only) | `cost.signal.default` | none |
| META-INFO (`META_INFO`) | yes | n/a (grammar/governance-only) | n/a (grammar/governance-only) | `cost.signal.default` | none |
| RWAM | yes | n/a (matrix/governance-only) | n/a (matrix/governance-only) | `cost.signal.default` | none |
| SAFETY | yes | n/a (pattern library itself) | n/a (covered by consuming domains) | `cost.signal.default` | none |
| META-MODEL (`META_MODEL`) | yes | n/a (substate read/emit handled by consuming couplings) | n/a (covered by consuming domains) | `cost.signal.default` | none |
| CTRL | yes | n/a (control-plane orchestration) | n/a (domain explain contracts cover emitted event kinds) | `cost.signal.default` | none |
| ABS | yes | n/a (substrate primitives consumed by domains) | n/a (domain explain contracts cover faults) | `cost.physics.default` | none |
| MOB | yes | yes | yes | `cost.mobility.default` | none |
| SIG | yes | yes | yes | `cost.signal.default` | none |
| ELEC | yes | yes | yes | `cost.elec.network_default` | none |
| THERM | yes | yes | yes | `cost.therm.network_default` | none |
| FLUID | yes | yes | yes | `cost.fluid.network_default` | none |
| CHEM | yes | yes | yes | `cost.physics.default` | none |
| FIELD | yes | yes | n/a (field-origin incidents explained via consuming domains) | `cost.physics.default` | none |
| MECH | yes | yes | yes | `cost.mobility.default` | none |
| INT | yes | yes | n/a (INT-linked incidents explained by FLUID/SAFETY event families) | `cost.mobility.default` | none |

## Patches Applied
- Added missing tier contracts (declaration-only, no runtime behavior change) for:
  - `CHEM`, `FIELD`, `MECH`, `INT`, `TEMP`, `CTRL`, `ABS`, `PROV`, `TOL`, `META_ACTION`, `META_INFO`, `META_MODEL`, `RWAM`, `SAFETY`.
- No coupling-contract or explain-contract rows were required for STRICT hard-gate compliance after audit.

## Validation Snapshot
- `python tools/xstack/testx_all.py --repo-root . --profile STRICT --cache off --subset test_all_domains_have_tier_contract,test_all_couplings_declared,test_all_explain_contracts_present,test_contract_schema_valid`
- Result: pass (all selected tests passed).
