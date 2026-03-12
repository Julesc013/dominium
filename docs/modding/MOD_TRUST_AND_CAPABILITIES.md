Status: CANONICAL
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/meta/EXTENSION_DISCIPLINE.md`
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# MOD-POLICY-0 Mod Trust And Capabilities

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic mod governance for pack loading, server posture, replay, and proof without requiring code forks or online trust checks.

This document governs:
- pack trust categories
- pack capability declarations
- server mod-policy profiles
- refusal behavior for disallowed packs
- deterministic proof and replay integration

This document does not change simulation behavior. It governs validation, composition, and refusal only.

## Trust Levels

Canonical trust level ids:
- `trust.official_signed`
- `trust.thirdparty_signed`
- `trust.unsigned`
- `trust.local_dev`

Interpretation:
- `trust.official_signed`: official or first-party pack accepted as trusted content by local SecureX posture.
- `trust.thirdparty_signed`: non-official pack with a local signed or verified trust posture.
- `trust.unsigned`: third-party pack with no accepted signature posture.
- `trust.local_dev`: local development pack intended for iteration, fixtures, or lab use.

Trust level assignment is explicit pack metadata.
Trust level assignment must not be inferred silently at runtime for authoritative composition.

## Capability Declarations

Every pack must declare the capabilities it uses.

Canonical capability ids for MOD-POLICY-0:
- `cap.overlay_patch`
- `cap.add_templates`
- `cap.add_processes`
- `cap.add_logic_elements`
- `cap.add_profiles`
- `cap.add_contracts`
- `cap.allow_exception_profiles`

Meaning:
- `cap.overlay_patch`: pack contributes overlay layers or property patches.
- `cap.add_templates`: pack contributes templates or template registries.
- `cap.add_processes`: pack contributes process definitions or process registries.
- `cap.add_logic_elements`: pack contributes logic elements or logic behavior registries.
- `cap.add_profiles`: pack contributes law, experience, or related profile artifacts.
- `cap.add_contracts`: pack contributes semantic or compatibility contract surfaces.
- `cap.allow_exception_profiles`: pack contributes profiles whose use can emit META-PROFILE exception events.

`cap.add_contracts` is forbidden by default for MVP policies.

## Policy Profiles

Canonical mod policy ids:
- `mod_policy.anarchy`
- `mod_policy.strict`
- `mod_policy.lab`

Default selection:
- the v0.0.0 default runtime/session creation path pins `mod_policy.lab`
- alternative mod policies must be selected explicitly at session creation or server configuration time

### `mod_policy.anarchy`
- allows `trust.official_signed`
- allows `trust.thirdparty_signed`
- allows `trust.unsigned`
- allows `trust.local_dev`
- allows most runtime-facing content capabilities
- forbids `cap.add_contracts`
- uses `overlay.conflict.last_wins`
- allows experimental/local iteration
- nondeterministic allowances remain explicit metadata and proof-visible

### `mod_policy.strict`
- allows only signed trust levels
- forbids `trust.unsigned`
- forbids `trust.local_dev`
- forbids `cap.add_contracts`
- forbids `cap.allow_exception_profiles`
- uses `overlay.conflict.refuse`
- forbids explicit nondeterministic allowances

### `mod_policy.lab`
- allows `trust.local_dev`
- allows experimental profiles and local tooling
- forbids `cap.add_contracts`
- uses `overlay.conflict.last_wins`
- default for local FAST workflows

## Determinism Rule

Packs must not introduce nondeterminism unless:
- the pack declares the request explicitly in its metadata
- the active mod policy permits that request
- the behavior remains replayable and proof-visible
- any required exception path is logged deterministically

If the active mod policy forbids nondeterminism, load must refuse with a stable refusal code.

## Profile Override Integration

Packs may not introduce profile-exception behavior unless:
- the pack declares `cap.allow_exception_profiles`
- the active mod policy allows that capability
- runtime profile application continues to emit exception events through the existing META-PROFILE exception ledger path

This policy layer does not bypass META-PROFILE controls.

## Refusal Codes

Canonical refusal codes:
- `refusal.mod.trust_denied`
- `refusal.mod.capability_denied`
- `refusal.mod.nondeterminism_forbidden`

Additional deterministic refusal codes may exist for missing descriptors or proof mismatches, but policy denials must use the canonical ids above.

## Proof And Replay

Proof bundles must include:
- `mod_policy_id`
- `mod_policy_registry_hash`
- loaded pack trust descriptor hashes
- loaded pack capability descriptor hashes

Replay and resume must refuse if:
- the saved `mod_policy_id` differs from runtime selection
- the mod policy registry hash differs from the saved proof surface
- pack trust/capability proof hashes differ from the saved proof surface

No silent migration is allowed.

## Implementation Notes

The active repository runtime uses adjacent pack metadata artifacts:
- `pack.trust.json`
- `pack.capabilities.json`

This avoids forcing an incompatible rewrite of every existing `pack.json` while still making trust and capability declarations mandatory for authoritative composition.
