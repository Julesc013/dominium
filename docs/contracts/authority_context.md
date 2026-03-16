Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/authority_context.schema.json` v1.0.0 and CompatX `tools/xstack/compatx/version_registry.json`.
Stability: stable
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# AuthorityContext Contract

## Purpose
Define the canonical authority envelope required for lawful process admission and observation filtering.

## Source of Truth
- Schema: `schemas/authority_context.schema.json` (`version: 1.0.0`)
- Related: `docs/contracts/law_profile.md`
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`
- Session lifecycle usage: `docs/architecture/session_lifecycle.md`

## Required Fields (`v1.0.0`)
- `schema_version` (`const "1.0.0"`)
- `authority_origin` (`client|server|tool|replay`)
- `experience_id` (string)
- `law_profile_id` (string)
- `entitlements` (array of strings)
- `epistemic_scope` (object with `scope_id` and `visibility_level`)
- `privilege_level` (`observer|operator|system`)

## Optional Fields (`v1.0.0`)
- `profile_bindings` (array)
  - Authority-scoped overlay bindings resolved after session scope.
- `effective_profile_snapshot` (object)
  - Deterministic resolved profile map used for diagnostics/replay and audit context.

## Invariants
- Authority is explicit and never bypasses law.
- Missing or malformed authority context is refused deterministically.
- `epistemic_scope` constrains observation surfaces and must be preserved.
- Unknown top-level fields are refused in strict mode.
- Headless boot path requires `authority_origin == "client"` and reconstructs context deterministically.
- Lens gating refuses when required entitlements are missing (`ENTITLEMENT_MISSING`).
- Process gating refuses deterministically when law/entitlement/privilege checks fail.

## Entitlement Guidance (Lab v1)
Stable entitlement IDs used by `law.lab.unrestricted`:
- `entitlement.camera_control`: required for `process.camera_move`
- `entitlement.teleport`: required for `process.camera_teleport`
- `entitlement.time_control`: required for `process.time_control_set_rate`, `process.time_pause`, `process.time_resume`
- `session.boot`: required for deterministic boot and `process.region_management_tick`
- `entitlement.inspect`: required for lab inspector/log tool windows
- `lens.nondiegetic.access`: required for nondiegetic lens observation
- `session.boot`: baseline session bootstrap entitlement
- `ui.window.lab.nav`: baseline lab navigation window entitlement
- `entitlement.teleport`: also gates lab navigator/go-to/site-browser tool windows
- `entitlement.control.camera`: required for controller camera bind/unbind processes
- `entitlement.control.possess`: required for controller possess/release processes
- `entitlement.control.lens_override`: required for controller lens override process
- `entitlement.agent.move`: required for `process.agent_move`
- `entitlement.agent.rotate`: required for `process.agent_rotate`
- `entitlement.civ.create_faction`: required for `process.faction_create`
- `entitlement.civ.dissolve_faction`: required for `process.faction_dissolve`
- `entitlement.civ.affiliation`: required for `process.affiliation_join` and `process.affiliation_leave`
- `entitlement.civ.claim`: required for `process.territory_claim` and `process.territory_release`
- `entitlement.civ.diplomacy`: required for `process.diplomacy_set_relation`
- `entitlement.civ.admin`: optional CIV admin override for ownership-gated faction/territory/diplomacy mutations
- `entitlement.control.admin`: administrative control entitlement reserved for server/admin law profiles
- `entitlement.admin.security_view`: required for anti-cheat admin security windows
- `entitlement.admin.kick`: required for administrative peer enforcement action controls (policy-gated)

## Example JSON (`schemas/authority_context.schema.json`)
```json
{
  "schema_version": "1.0.0",
  "authority_origin": "client",
  "experience_id": "profile.lab.developer",
  "law_profile_id": "law.lab.unrestricted",
  "entitlements": [
    "session.boot",
    "entitlement.camera_control",
    "entitlement.teleport",
    "entitlement.time_control",
    "lens.nondiegetic.access",
    "ui.window.lab.nav"
  ],
  "epistemic_scope": {
    "scope_id": "epistemic.lab.placeholder",
    "visibility_level": "placeholder"
  },
  "privilege_level": "operator"
}
```

## TODO
- Add canonical refusal reason mapping for each authority-origin failure class.
- Add explicit linkage contract to entitlement registry schema once published.
- Add migration sample once pre-`1.0.0` compatibility paths exist.

## Cross-References
- `docs/contracts/law_profile.md`
- `docs/contracts/versioning_and_migration.md`
- `docs/architecture/observation_kernel.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/camera_and_navigation.md`
