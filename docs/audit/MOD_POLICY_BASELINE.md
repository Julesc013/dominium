Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/modding/MOD_TRUST_AND_CAPABILITIES.md`, `docs/meta/EXTENSION_DISCIPLINE.md`, `docs/geo/OVERLAY_CONFLICT_POLICIES.md`, `src/modding/mod_policy_engine.py`, `tools/xstack/registry_compile/compiler.py`, and `tools/xstack/sessionx/creator.py`.

# MOD-POLICY-0 Baseline

## Trust Levels

Canonical trust levels established for pack governance:
- `trust.official_signed`
- `trust.thirdparty_signed`
- `trust.unsigned`
- `trust.local_dev`

Trust is carried by adjacent deterministic descriptors:
- `pack.trust.json`
- `pack.capabilities.json`

Current authoritative default posture:
- MVP default runtime artifacts pin `mod_policy.lab`
- strict/ranked flows pin `mod_policy.strict`
- anarchy flows may pin `mod_policy.anarchy`

## Capability Surface

Canonical pack capability declarations for MOD-POLICY-0:
- `cap.overlay_patch`
- `cap.add_templates`
- `cap.add_processes`
- `cap.add_logic_elements`
- `cap.add_profiles`
- `cap.add_contracts`
- `cap.allow_exception_profiles`

Policy decisions are deterministic and explicit:
- packs must declare the capabilities they use
- policy evaluation compares declared capabilities to allowed capabilities
- profile-exception-capable packs require `cap.allow_exception_profiles`
- nondeterministic allowances are explicit metadata and proof-visible

## Policy Modes

### `mod_policy.anarchy`
- allows unsigned and local-dev content
- keeps capability evaluation and proof deterministic
- resolves overlay conflicts through `overlay.conflict.last_wins`

### `mod_policy.strict`
- allows only signed trust categories
- forbids `cap.add_contracts`
- forbids explicit nondeterministic allowances
- resolves overlay conflicts through `overlay.conflict.refuse`

### `mod_policy.lab`
- default local development posture
- allows `trust.local_dev`
- supports experimental iteration without code forks
- resolves overlay conflicts through `overlay.conflict.last_wins`

## Enforcement Summary

Pack loading / compile / boot now enforce:
- trust-level allowance
- capability allowance
- nondeterminism-forbidden policy
- replay/resume policy-hash match

Stable refusal codes:
- `refusal.mod.trust_denied`
- `refusal.mod.capability_denied`
- `refusal.mod.nondeterminism_forbidden`
- `refusal.mod.policy_mismatch`

## Proof And Replay

Proof and lock surfaces now carry:
- `mod_policy_id`
- `mod_policy_registry_hash`
- `mod_policy_proof_hash`
- `overlay_conflict_policy_id`
- per-pack trust/capability descriptor hashes

Replay/resume refusal occurs when:
- saved/runtime `mod_policy_id` differs
- saved/runtime mod policy registry hash differs
- required proof metadata is missing

## Known Limits

Intentionally stubbed in MOD-POLICY-0:
- no online signature verification
- no GUI prompt flow for policy remediation
- no new overlay merge semantics beyond profile-selected conflict policy
- no simulation behavior changes beyond validation/refusal and proof pinning

## Readiness

MOD-POLICY-0 is ready for:
- MW-4 caching and refinement keys that include mod-policy/contract pins
- future trust/capability gating for mods without code forks
- later SecureX strengthening without changing the deterministic policy surface
