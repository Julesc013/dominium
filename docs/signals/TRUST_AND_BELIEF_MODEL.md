Status: AUTHORITATIVE
Version: 1.0.0
Last Updated: 2026-03-03
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Trust and Belief Model (SIG-5)

## Purpose
Define deterministic trust and belief dynamics for signal receipts so subjects and institutions can act on epistemic state rather than authoritative truth.

## A) Trust Graph

- Trust graph nodes are `subject_id` values (agents, institutions, system subjects).
- Trust graph edges are directed:
  - `from_subject_id -> to_subject_id`
  - `trust_weight` in fixed-point range `[0.0, 1.0]`
- Edge metadata supports replay-safe adaptation:
  - `evidence_count`
  - `last_updated_tick`
  - optional context tags in `extensions` for future domain-scoped trust.

Invariant:
- No implicit reverse-edge trust. Reverse relationships must be explicit rows.

## B) Belief Formation

- Knowledge remains receipt-driven (`knowledge_receipt`).
- Receipt trust weight is derived from trust graph at delivery time:
  - receiver trusts sender using edge `(receiver -> sender)`.
- Acceptance is policy-driven:
  - if `trust_weight >= acceptance_threshold`: accepted
  - else: untrusted (stored, not silently discarded)

Receipt fields:
- `trust_weight`: deterministic weight at acquisition time.
- `verification_state`: defaults to `unverified` until explicit verification process.
- `extensions.accepted`: deterministic boolean by belief policy threshold.

## C) Verification

- Verification is explicit and process-bound (`process.message_verify_claim`).
- Verification inputs must come from admissible evidence paths:
  - observation artifacts
  - certificate/credential artifacts
  - entitlement-gated truth observer path when explicitly allowed by law/profile
- Trust updates occur only after verification result rows are produced.
- No omniscient trust updates from hidden truth comparisons.

## D) Propagation

- Forwarding/aggregation policy can use acceptance state:
  - accepted-only
  - include-all with confidence tags
- Propagation remains deterministic and queue-based (SIG-1/SIG-2).
- Trust influences whether to forward and how strongly to weight summaries; it does not mutate canonical artifact content.

## E) Determinism Contract

- Trust update function is deterministic:
  - inputs: prior edge row, verification outcome, policy parameters
  - output: clamped trust weight and incremented evidence count
- Update ordering is deterministic:
  - sorted by `(from_subject_id, to_subject_id, artifact_id, result_id)`
- Optional decay is deterministic per tick and policy.
- No wall-clock, no ad-hoc per-agent randomness.

## Integration Notes

- SIG-0..4 transport/security remain authoritative for delivery and access control.
- SIG-5 extends receipt semantics with acceptance and trust adaptation.
- CTRL decision logs should include trust/belief policy decisions for inspectability.
- CIV/institution legitimacy layers can consume trust graph state without redefining trust mechanics.

## Non-Goals (SIG-5)

- Psychological simulation or nondeterministic cognition.
- Domain-specific trust hacks embedded in subsystems.
- Implicit truth oracle corrections.
