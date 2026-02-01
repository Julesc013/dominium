Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_EPISTEMIC_GATING — Knowledge, Access, and Uncertainty

Status: draft
Version: 1

## Purpose
Define how standards and renderers are gated by knowledge, device access, and
authority. Epistemic gating ensures fog-of-war and uncertainty are preserved and
prevents silent assumptions.

## Core rules
- A standard is usable only if the actor knows it.
- Some standards require devices or authority to apply.
- Lack of knowledge or access produces UNKNOWN, not defaults.
- Gating applies before standard resolution (see `docs/specs/SPEC_STANDARD_RESOLUTION.md`).

## Knowledge requirements
An actor must have explicit knowledge of:
- the standard identifier
- the standard parameters or version
- any jurisdiction or organization constraints required to interpret it

Knowledge sources (non-exhaustive):
- training, education, or discovery
- organizational onboarding
- device-assisted lookup (if permitted)

## Device access and authority
Standards can require:
- trusted devices (e.g., timing instruments, calibration hardware)
- organizational authority (e.g., legal standards)
- network access (only if deterministically provided by content; no live queries)

If access is missing:
- the standard is BLOCKED
- resolution proceeds to the next candidate
- conflict is recorded

## Uncertainty envelopes
When a standard is known but inputs are partial:
- render as a range or explicitly marked uncertainty
- do not fabricate precise values
- preserve canonical quantities unchanged

## ASCII diagram

  [Actor Context]
       |
       v
  [Knowledge Check] ---no---> UNKNOWN (record reason)
       |
      yes
       |
       v
  [Access/Authority Check] ---no---> BLOCKED (record reason)
       |
      yes
       |
       v
  [Standard Usable]

## Non-examples (forbidden)
- "If unknown, use a default standard"
- "If device missing, assume the last known calibration"
- "If knowledge missing, infer from locale or UI settings"
- "If access denied, silently hide the failure"

## Worked examples

### Time standards
Actor knows HPC-E and SCT but lacks a required timing device for HPC-E.
Result: HPC-E is BLOCKED, SCT may be used if allowed by resolution order.
If SCT is not allowed, the output is UNKNOWN or canonical numeric form.

### Currency standards
Actor views a trade with a currency standard they do not know.
Result: UNKNOWN is rendered for currency labels, base asset units remain visible
if allowed by policy.

### Units with device failure
An SI-like standard requires a calibrated device. The device is offline.
Result: SI-like units are BLOCKED; the resolver may fall back to canonical numeric
form with unknown unit labeling.

### Governance
Actor lacks authority to access a jurisdictional standard. The UI must show the
conflict and produce UNKNOWN for legal labels, not a guessed interpretation.

## Validation requirements (spec-only)
Implementations must provide:
- knowledge gating tests (known vs unknown)
- access gating tests (device/authority missing)
- UNKNOWN propagation tests
- conflict visibility tests for gated standards