Status: AUTHORITATIVE
Last Reviewed: 2026-03-06
Version: 1.0.0
Scope: SYS-7 system-level forensics and explainability model.

# System Forensics Model

## Purpose
SYS-7 defines a uniform deterministic "why" model for system events across micro and macro tiers.
Forensics artifacts are derived-only, compactable, and anchored to canonical evidence chains.

## A) Explain Artifact Levels
- `L1` boundary-level explanation:
  - boundary input/output behavior,
  - active boundary invariants,
  - immediate trigger reason.
- `L2` component-level explanation:
  - subsystem contributors,
  - safety/compliance/reliability contributors,
  - dominant hazards and threshold context.
- `L3` event-chain explanation:
  - bounded canonical event sequence,
  - provenance-linked cause entries,
  - deterministic ordering over referenced events.

## B) Bounded Cause Chain
Each explain artifact uses a fixed bounded cause chain.

Selection policy:
1. Gather candidate canonical evidence rows from system reliability, certification, macro output, safety, ledger, and domain fault channels.
2. Assign deterministic severity rank per cause entry.
3. Sort by:
   - severity descending,
   - tick descending (most recent first),
   - stable tie-break by `event_id`/`entry_id`.
4. Truncate to bounded `N` entries (policy default `N=16`, request-level override allowed if lower).

No adaptive or nondeterministic ranking is permitted.

## C) Epistemic Redaction
Redaction is requester-policy driven and deterministic:
- diegetic:
  - coarse primary cause,
  - short cause chain,
  - no privileged internals/spec thresholds unless law allows.
- inspector:
  - includes threshold/spec references,
  - richer remediation hints,
  - bounded canonical references.
- admin:
  - full bounded reference set,
  - complete cause chain within configured limit.

No default omniscient access is allowed.

## D) MacroCapsule Forensics
When systems are collapsed:
- forensics uses `macro_output_record` history and `macro_runtime_state` snapshots,
- forced-expand events and error-bound breaches must link to capsule records and hashes,
- explain output remains derived and does not mutate canonical truth.

## Determinism and Caching
Explain generation cache key:
- `(system_id, event_id, truth_hash_anchor, requester_policy)`

Caching rules:
- cache stores derived explain artifacts only,
- cache invalidates on truth hash anchor change,
- cache lookup and write order is deterministic.

## Integration Contracts
SYS-7 forensics integrates with:
- SYS-6 reliability (`system.warning`, `system.failure`, forced expand),
- SYS-5 certification (`system.certification_failure`, `system.certificate_revocation`),
- SYS-2 macro behavior (`system.capsule_error_bound_exceeded`, output degradation/safety shutdown),
- SYS-1/SYS-3 invariant and transition refusal channels.
