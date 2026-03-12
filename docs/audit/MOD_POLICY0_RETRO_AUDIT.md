Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/architecture/pack_system.md`, `docs/security/SECUREX_TRUST_MODEL.md`, `tools/xstack/pack_loader/loader.py`, `tools/xstack/sessionx/net_handshake.py`, and `src/geo/overlay/overlay_merge_engine.py`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MOD-POLICY-0 Retro Audit

## Scope
Audit current pack manifest, SecureX, overlay, and session/runtime integration surfaces before adding deterministic mod trust and capability policy enforcement.

## Current Pack Manifest Fields

Primary runtime pack manifests live under:
- `packs/<category>/<pack_id>/pack.json`

Current schema:
- `schemas/pack_manifest.schema.json` v1.0.0

Current required fields:
- `schema_version`
- `pack_id`
- `version`
- `compatibility`
- `dependencies`
- `contribution_types`
- `contributions`
- `canonical_hash`
- `signature_status`

Current trust/capability observations:
- `signature_status` already exists and is used as a coarse trust posture.
- No `trust_level_id` field exists.
- No `capability_ids` field exists.
- No adjacent mod-policy metadata file exists.

## Current SecureX Hooks

Existing SecureX/trust registry:
- `data/registries/securex_policy_registry.json`

Existing policies:
- `securex.policy.private_relaxed`
- `securex.policy.casual_default`
- `securex.policy.rank_strict`

Current SecureX behavior:
- Evaluates per-pack `signature_status`.
- Supports unsigned allowance or refusal.
- Supports classroom-restricted gating.
- Supports verification-required stub posture.

Current SecureX enforcement points:
- `tools/security/tool_securex_verify_pack.py`
- `tools/security/tool_securex_verify_lockfile.py`
- `tools/xstack/sessionx/net_handshake.py`

Audit finding:
- SecureX currently governs signature posture only.
- It does not govern pack capabilities.
- It does not govern profile override capability.
- It does not govern deterministic mod-policy selection for offline boot/runtime.

## Current Overlay Pack Loading Path

Pack discovery and validation:
- `tools/xstack/pack_loader/loader.py`

Registry/lockfile compilation:
- `tools/xstack/registry_compile/compiler.py`
- `tools/xstack/registry_compile/lockfile.py`

Session/runtime consumption:
- `tools/xstack/sessionx/creator.py`
- `tools/xstack/sessionx/runner.py`
- `tools/xstack/sessionx/script_runner.py`

Overlay trust integration:
- `src/geo/overlay/overlay_merge_engine.py`

Current overlay trust observations:
- Overlay policy extensions already control:
  - `allow_unsigned_mods`
  - `require_official_signature`
  - `overlay_conflict_policy_id`
- Official overlay layers are required to resolve to lockfile-backed signed packs when policy requires it.
- Unsigned mod layers can already be refused by overlay policy.

Audit finding:
- Overlay policy trust checks are narrower than required mod governance.
- They do not account for declared pack capabilities.
- They do not provide a unified mod-policy profile shared with pack loading and replay.

## Current Lockfile / Proof State

Current lockfile resolved pack projection:
- `pack_id`
- `version`
- `canonical_hash`
- `signature_status`

Current `pack_lock_hash` inputs:
- sorted tuple of `pack_id`, `version`, `canonical_hash`, `signature_status`

Audit finding:
- Lockfiles currently omit trust-level normalization beyond `signature_status`.
- Lockfiles omit capability declarations.
- Proof/run-meta surfaces therefore cannot currently prove capability governance decisions.

## Current Session / Runtime Policy Injection Points

Current SessionSpec can already pin:
- `pack_lock_hash`
- `contract_bundle_hash`
- `semantic_contract_registry_hash`

Network/session policy surfaces already exist for:
- SecureX handshake policy (`network.securex_policy_id`)
- overlay conflict policy (via overlay policy registry)

Audit finding:
- No `mod_policy_id` is currently pinned in SessionSpec.
- No offline boot/load path enforces a mod policy.
- No replay path checks mod policy compatibility.

## Current Profile Override / Exception Surface

Existing profile override logging:
- `src/meta/profile/profile_engine.py`
- `src/geo/profile_binding.py`

Existing behavior:
- profile override application can emit deterministic `profile_exception_event` rows
- override allowance is law/profile-gated via `profile_override_allowed_rule_ids`

Audit finding:
- Override logging exists and can be reused.
- There is no pack-level capability gate for packs contributing profiles or exception-allowing profiles.

## Integration Points Recommended

Minimum deterministic integration points:
1. Pack metadata loading in `tools/xstack/pack_loader/loader.py`
2. Lockfile resolved pack projection in `tools/xstack/registry_compile/compiler.py`
3. SessionSpec pinning in `tools/xstack/sessionx/creator.py`
4. Boot/load/replay enforcement in `tools/xstack/sessionx/runner.py`, `tools/xstack/sessionx/script_runner.py`, and resume paths
5. Overlay policy composition in `src/geo/overlay/overlay_merge_engine.py`
6. Proof/run-meta emission in session boot/script surfaces

## Risks / Fix List

1. Pack trust is currently fragmented across manifest `signature_status`, SecureX, and overlay policy.
2. Capability governance is currently absent from pack loading.
3. Replay/proof surfaces cannot currently prove capability-based accept/refuse decisions.
4. Profile-contributing packs are not currently gated by explicit mod capability policy.
5. Existing data must remain usable:
   - local lab/dev flows must stay allowed by default
   - strict/ranked flows must refuse deterministically
   - no silent migration of existing packs is acceptable
