Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Pollution Constitution Baseline

Status: BASELINE (POLL-0)  
Date: 2026-03-05  
Scope: POLL-0 constitutional substrate (pollutant quantities, source-event canon, P0 totals engine, explain hooks, enforcement, and TestX coverage).

## 1) Pollutant Taxonomy

Canonical pollutant quantity and IDs frozen in POLL-0:

- `quantity.pollutant_mass` (kg)
- `pollutant.smoke_particulate`
- `pollutant.co2_stub`
- `pollutant.toxic_gas_stub`
- `pollutant.oil_spill_stub`

Canonical registries/schemas:

- `data/registries/pollutant_type_registry.json`
- `schema/pollution/pollutant_type.schema`
- `schemas/pollutant_type.schema.json`

## 2) Emission Event Model

Authoritative emission path is process-only:

- `process.pollution_emit` in `tools/xstack/sessionx/process_runtime.py`
- canonical source-event artifact class: `artifact.record.pollution_source_event`
- P0 totals ledger: `pollution_total_rows` and `pollutant_mass_total`

Canonical emission schema:

- `schema/pollution/pollution_source_event.schema`
- `schemas/pollution_source_event.schema.json`

POLL-0 invariant: no silent pollutant creation/disappearance outside explicit process/model transforms.

## 3) Tier Policy

Declared tier envelope:

- `P0`: bookkeeping totals (implemented in POLL-0)
- `P1`: coarse field policy scaffold (declared; dispersion implementation deferred to POLL-1)
- `P2`: ROI micro detail reserved

Policy registry:

- `data/registries/pollution_field_policy_registry.json`
  - `poll.policy.none` (`P0`)
  - `poll.policy.coarse_diffuse` (`P1`)
  - `poll.policy.rank_strict` (`P1`)

## 4) Invariants and Contract Impact

Relevant constitutional/invariant coverage upheld:

- Canon axioms: deterministic execution, process-only mutation, observer/render separation, pack-driven integration.
- RepoX invariant set additions:
  - `INV-POLLUTION-EMIT-THROUGH-PROCESS`
  - `INV-NO-DIRECT-POLLUTION-FIELD-WRITES`
  - `INV-POLLUTANT-TYPE-REGISTERED`
- Explain contracts:
  - `explain.pollution_spike`
  - `explain.exposure_threshold`

Contract/schema impact:

- Changed: added POLL schema family (`pollutant_type`, `pollution_source_event`, `pollution_field_policy`, `exposure_state`) and POLL registries/contracts.
- Unchanged: no CompatX major version bump introduced in POLL-0; no migration route required for existing save payloads.

## 5) Gate Execution

Validation level executed for this phase: `FAST` minimum + requested strict governance gates.

- topology map updated: `py -3 tools/governance/tool_topology_generate.py --repo-root .`
  - result: `complete`
  - deterministic_fingerprint: `4c2bc6ace9ab411961aacdd83b1c4969be3f26fc1811d467a260efbf38fe177f`
- RepoX STRICT: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - result: `pass` (`findings=17`, warnings only)
- AuditX STRICT: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - result: `pass` (`promoted_blockers=0`)
- TestX PASS (POLL suite):  
  `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --subset test_pollutant_registry_valid,test_pollution_emit_deterministic,test_pollution_totals_conserved,test_explain_spike_deterministic,test_null_boot_pollution_none_ok`
  - result: `pass` (`selected_tests=5`)
- strict build gate: `py -3 tools/xstack/run.py strict --repo-root . --cache on`
  - result: `refusal` (global baseline blockers outside POLL-0 scope)
  - blocking steps:
    - `01.compatx.check` refusal
    - `04.registry.compile` refusal
    - `05.lockfile.validate` refusal
    - `07.session_boot.smoke` refusal
    - `10.testx.run` fail (global strict suite)
    - `13.packaging.verify` refusal

Additional strict TestX evidence:

- `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache on`
- result: `fail` with broad pre-existing non-POLL failures (session/create/packaging/network/control suites).

## 6) Readiness for POLL-1 / POLL-2

Ready for POLL-1 (P1 dispersion implementation):

- pollutant taxonomy, source-event canon, policy scaffolding, and explain hooks are in place.
- enforcement rails exist for process-only emission and registered pollutant IDs.

Ready for POLL-2 (exposure-first health coupling):

- exposure schema and explain contract anchor are present.
- hazard integration can be added as constitutive model extensions without changing POLL-0 ledger invariants.
