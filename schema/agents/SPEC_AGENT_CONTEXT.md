--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Context assembly rules and capability evaluation.
SCHEMA:
- Agent context record formats and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No direct authoritative state exposure in context records.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_AGENT_CONTEXT - Agent Context (AGENT0)

Status: draft
Version: 1

## Purpose
Define the data format for agent contexts as epistemic, bounded snapshots.

## AgentContext schema
Required fields:
- context_id
- owner_agent_id
- epistemic_snapshot_ref
- capability_set_ref
- authority_scope_ref
- resource_summary_ref
- interest_set_ref
- issued_at_act
- next_due_tick
- provenance_ref

Rules:
- Contexts are immutable snapshots at issued_at_act.
- resource_summary_ref is bounded and non-global.
- interest_set_ref constrains spatial and domain scope.

## EpistemicSnapshot schema
Required fields:
- snapshot_id
- belief_set_ref
- uncertainty_model_ref
- observation_refs (bounded list)
- report_refs (bounded list)
- last_update_act
- provenance_ref

Rules:
- Observations and reports are epistemic only.
- No authoritative values appear in snapshot payloads.

## CapabilitySet schema
Required fields:
- capability_set_id
- capability_ids (bounded list)
- provenance_ref

Rules:
- Capabilities must be derived from authority and policy.

## AuthorityScope schema
Required fields:
- scope_id
- jurisdiction_refs (bounded list)
- org_refs (bounded list)
- role_refs (bounded list)
- provenance_ref

Rules:
- Authority scopes are explicit and bounded.
- Absence of authority implies no command rights.

## Determinism and performance rules
- Context assembly is deterministic and batch-safe.
- No global iteration to build contexts.
- Context activation is event-driven via next_due_tick.

## Prohibitions
- No omniscient context payloads.
- No hidden capability grants outside authority rules.

## Integration points
- Epistemics: `schema/knowledge/SPEC_SECRECY.md`
- Governance: `schema/governance/SPEC_JURISDICTIONS.md`
- Interest sets: `docs/SPEC_INTEREST_SETS.md`

## Test plan (spec-level)
Required scenarios:
- Context snapshots are deterministic for identical inputs.
- Authority scope denies commands outside jurisdiction.
- No global iteration for context assembly.
