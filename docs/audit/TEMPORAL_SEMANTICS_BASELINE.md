Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# TEMP-0 Temporal Semantics Baseline

Date: 2026-03-04  
Scope: `TEMP-0` constitution baseline for temporal domains, mappings, causality governance, deterministic warp/substep policy, and branching policy.

## Canonical Domains and Mappings

### Temporal domains (`data/registries/temporal_domain_registry.json`)
- `time.canonical_tick` (global authoritative tick domain)
- `time.proper` (per-assembly derived domain)
- `time.civil` (per-session institutional calendar domain)
- `time.warp` (per-session derived warp interpretation domain)
- `time.replay` (per-session reenactment interpretation domain)

### Time mappings (`data/registries/time_mapping_registry.json`)
- `mapping.proper_default_stub` (`time.canonical_tick -> time.proper`)
- `mapping.civil_calendar_stub` (`time.canonical_tick -> time.civil`)
- `mapping.warp_session_stub` (`time.canonical_tick -> time.warp`)

### Schedule-time binding
- Schedule schema now requires `temporal_domain_id`.
- Core/aggregation schedule normalization defaults legacy rows to `time.canonical_tick` for deterministic migration compatibility.

## Causality and Determinism Rules

- `INV-SCHEDULE-DOMAIN-DECLARED`
- `INV-NO-WALLCLOCK-TIME`
- `INV-NO-FUTURE-RECEIPTS`
- `INV-DETERMINISTIC-SUBSTEP-POLICY`

AuditX temporal analyzers added and registered:
- `E229_WALLCLOCK_USE_SMELL`
- `E230_FUTURE_RECEIPT_REFERENCE_SMELL`
- `E231_UNDECLARED_TEMPORAL_DOMAIN_SMELL`

## Batching/Substepping Policy

Registered deterministic policies (`data/registries/substep_policy_registry.json`):
- `substep.none`
- `substep.fixed_4`
- `substep.fixed_8`
- `substep.closed_form_only`

Forbidden contract:
- adaptive error-driven substep sizing in authoritative paths.

## Branching Policy

Registered branch policies (`data/registries/branch_policy_registry.json`):
- `branch.disabled`
- `branch.allowed_private`
- `branch.allowed_lab`
- `branch.forbidden_ranked`

Branch semantics are lineage-based (fork + branch id + authority/proof), never retroactive truth rewrite.

## TestX Coverage Added

- `test_temporal_domains_registry_valid`
- `test_time_mapping_registry_valid`
- `test_schedule_has_domain_binding`
- `test_no_future_receipt_references`
- `test_substep_policy_deterministic`

## Gate Results

- RepoX STRICT: **PASS**
- AuditX STRICT: **FAIL** (existing repository-wide strict blockers unrelated to TEMP-0 changes, notably promoted `E179_INLINE_RESPONSE_CURVE_SMELL` findings)
- TestX STRICT (TEMP-0 subset): **PASS**
- TestX STRICT (full suite): **not completed** (runner timed out in this environment)
- Strict pipeline (`tools/xstack/run.py strict`): **not completed** (timed out in this environment)
- Topology map: **updated** (`docs/audit/TOPOLOGY_MAP.json`, `docs/audit/TOPOLOGY_MAP.md`)

## Readiness

TEMP-0 baseline artifacts are in place for LOGIC timer-style systems and future time-aware domains without introducing a bespoke wall-clock subsystem:
- canonical tick anchoring preserved
- domain/mapping declarations formalized
- schedule domain binding formalized
- causality invariants enforced in RepoX/TestX scaffolding
- deterministic substep and branch policy registries established
