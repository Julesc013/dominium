--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
- Stable IDs and hashing helpers.
GAME:
- Continuation policy rules, eligibility selection, and control binding.
SCHEMA:
- Continuation policy records and ability package definitions.
TOOLS:
- Future inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit respawn or fabricated heirs.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_CONTINUATION_POLICIES — Continuation Policy Catalog

Status: legacy (superseded by LIFE0+)
Version: 1

Note: LIFE0+ canonical specs live in `schema/life/SPEC_REINCARNATION.md` and
`schema/life/SPEC_IDENTITY_AND_LINEAGE.md`. This document remains for legacy
context; if any statement conflicts with LIFE0+, LIFE0+ wins.

## Purpose
Define continuation policies and ability packages that govern control after
death. Policies are data-defined and deterministic. No runtime logic is
introduced here.

## Ability packages (mode presets)
Ability packages define control and UI capabilities for a controller.

Inclusion order (explicit):
HARDCORE < SOFTCORE < CREATIVE < SPECTATOR

Rules:
- Higher packages are supersets unless explicitly revoked in the package.
- Capability conflicts are resolved by explicit package rules, not by defaults.

### AbilityPackage schema (conceptual)
Required fields:
- ability_package_id
- name (HARDCORE | SOFTCORE | CREATIVE | SPECTATOR or custom)
- allowed_control_modes (list)
- ui_capability_mask
- debug_capability_mask
- death_end_control (bool)
- transfer_allowed (bool)

Optional fields:
- notes_ref (non-sim)
- restrictions (explicit overrides)

Default:
- World default uses HARDCORE.

## Continuation policy records

### ContinuationPolicy schema (conceptual)
Required fields:
- policy_id
- policy_code (S1 | S2 | S3 | S4)
- ability_package_id
- authority_scope_id
- prerequisites_ref
- refusal_rules_ref
- selection_rule_id (deterministic)

Optional fields:
- contract_ref
- jurisdiction_ref
- organization_ref
- schedule_ref (ACT)

## Policy catalog (mandatory)

### S1 — Transfer to existing eligible person
Prerequisites:
- Eligible person exists within authority scope.
- Consent or delegated authority is valid.

Refusal conditions:
- No eligible person.
- Authority invalid or expired.
- Legal/jurisdiction refusal.

Provenance requirements:
- Control transfer must reference the authority record and audit trail.

### S2 — Clone/Vat embodiment (late tech)
Prerequisites:
- Constructed facility exists (clone/vat).
- Resources and time allocated by contract.

Refusal conditions:
- Facility absent or offline.
- Resources insufficient or contract invalid.

Provenance requirements:
- Body construction provenance must be recorded and linked.

### S3 — Drone/Robot embodiment
Prerequisites:
- Constructed drone/robot exists and is authorized.
- Permissions and ownership recorded.

Refusal conditions:
- No authorized drone available.
- Control permissions revoked.

Provenance requirements:
- Embodiment provenance must reference the constructed unit.

### S4 — Backup embodiment (far future)
Prerequisites:
- Constructed recording and instantiation infrastructure.
- Valid backup record and contract.

Refusal conditions:
- No valid backup record.
- Instantiation infrastructure unavailable.

Provenance requirements:
- Backup lineage and info-loss policy must be recorded.

## Determinism and scalability
- Continuation selection is deterministic and event-driven.
- Eligible candidates are bounded by authority scope and interest sets.
- No global scans over all persons are permitted.

## Implementation notes (LIFE1)
- Runtime code lives under `game/include/dominium/life/*` and `game/core/life/*`.
- Ability packages resolve inheritance deterministically with explicit overrides and additive capability masks.
- S1 selection filters by epistemic knowledge and authority, then selects by reason priority and stable `person_id`.
- S2–S4 are prerequisite-validation stubs only; they return `PENDING` and MUST NOT fabricate persons or bodies.
- Refusal codes are stable enums and are required for auditability and replay parity.

## Prohibitions (absolute)
- "Respawn at nearest spawn point" without causal pipeline.
- Creating a new body without construction provenance.
- Fabricating heirs or eligible candidates.
- Automatic continuation without a policy record.

## Test plan (spec-level)
Implementations MUST provide tests for:
- deterministic control transfer selection
- refusal when no eligible person exists (hardcore)
- replay equivalence for policy resolution
- batch vs step invariance for scheduled resolution
- epistemic correctness (death knowledge delayed)

## Integration points
- Control authority: `schema/life/SPEC_CONTROL_AUTHORITY.md`
- Death and estate: `schema/life/SPEC_DEATH_AND_ESTATE.md`
- Provenance: `docs/specs/SPEC_PROVENANCE.md`
