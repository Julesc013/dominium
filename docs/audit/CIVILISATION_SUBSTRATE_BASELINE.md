Status: DERIVED
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: CIV-1/4 structural baseline
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Civilisation Substrate Baseline

## Summary
CIV-1 establishes deterministic, process-driven foundations for factions, affiliations, territory claims, and diplomacy stubs without adding economy/combat/survival semantics.

## Faction Model
- Truth-side assembly: `assembly.faction.*` represented in `universe_state.faction_assemblies`.
- Deterministic create/dissolve process surface:
  - `process.faction_create`
  - `process.faction_dissolve`
- Deterministic faction ID path:
  - auto: `faction.{H(founder_agent_id, created_tick)[:16]}`
  - override: explicit `inputs.faction_id` (must be unique)
- Ownership authority:
  - faction extension `owner_peer_id` enforces mutation ownership in multiplayer paths.
  - admin override allowed via entitlement path (`entitlement.control.admin` or `entitlement.civ.admin`).

## Affiliation Model
- Field substrate in `universe_state.affiliations`.
- Deterministic mutation processes:
  - `process.affiliation_join`
  - `process.affiliation_leave`
- `subject_id` supports agent IDs now and cohort IDs structurally for CIV-2 expansion.
- Duplicate join rejected with deterministic refusal:
  - `refusal.civ.already_affiliated`

## Territory Claim Rules
- Territory substrate in `universe_state.territory_assemblies`.
- Deterministic mutation processes:
  - `process.territory_claim`
  - `process.territory_release`
- Claim behavior:
  - unclaimed -> owner set, status `claimed`
  - conflicting owner -> status `contested`, contested set tracked deterministically
- Deterministic conflict tie-break for owner field in contested state:
  - lexical faction ordering to keep order-invariant output

## Diplomacy Stub
- Relation substrate in `universe_state.diplomatic_relations`.
- Process surface:
  - `process.diplomacy_set_relation`
- CIV-1 relation behavior:
  - symmetric updates over canonical pair `(min(faction_a,faction_b), max(...))`
  - relation states constrained by `data/registries/diplomatic_state_registry.json`
- No gameplay effects (war/trade mechanics deferred).

## Refusal Codes
- `refusal.civ.entitlement_missing`
- `refusal.civ.law_forbidden`
- `refusal.civ.already_affiliated`
- `refusal.civ.territory_invalid`
- `refusal.civ.claim_forbidden`
- `refusal.civ.relation_invalid`
- `refusal.civ.ownership_violation`

## Multiplayer Integration Notes
- Lockstep: CIV intents are carried as deterministic process intents.
- Server-authoritative: server remains authoritative over faction/territory/diplomacy state mutation.
- SRZ hybrid: ownership checks enforce peer/faction authority; invalid ownership mutation paths refuse deterministically.
- CIV changes remain process-log anchored and hash-stable.

## Guardrails
- RepoX:
  - `INV-CIV-PROCESSES-ONLY-MUTATION`
  - `INV-NO-PLAYER-FACTION-SPECIALCASE`
  - `INV-FACTION-ID-STABLE`
- AuditX analyzers:
  - `E30_FACTION_ORPHAN_SMELL`
  - `E31_TERRITORY_OWNERSHIP_DRIFT_SMELL`
- TestX coverage:
  - `testx.civilisation.faction_create_deterministic`
  - `testx.civilisation.affiliation_join_leave_deterministic`
  - `testx.civilisation.territory_claim_conflict_order`
  - `testx.civilisation.diplomacy_update_deterministic`
  - `testx.civilisation.no_agents_world_runs_ok`
  - `testx.civilisation.single_agent_world_runs_ok`

## Validation Snapshot (2026-02-26)
- RepoX PASS:
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Result: `status=pass` (`repox scan passed`, findings=`1` warn-level only).
- AuditX run:
  - `py -3 tools/auditx/auditx.py scan --repo-root .`
  - Result: `result=scan_complete`, findings=`1532`.
- TestX PASS (CIV-1 required suite):
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.civilisation.faction_create_deterministic,testx.civilisation.affiliation_join_leave_deterministic,testx.civilisation.territory_claim_conflict_order,testx.civilisation.diplomacy_update_deterministic,testx.civilisation.no_agents_world_runs_ok,testx.civilisation.single_agent_world_runs_ok`
  - Result: `status=pass` (`selected_tests=6`).
- strict build PASS:
  - `C:\Program Files\CMake\bin\cmake.exe --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
  - Result: build complete for all strict targets.
- `ui_bind --check` PASS:
  - `py -3 tools/xstack/ui_bind.py --repo-root . --check`
  - Result: `result=complete`, `checked_windows=21`.

Known environment limitation observed during full profile run:
- `py -3 tools/xstack/run.py strict --repo-root .` currently reports non-CIV failures in unrelated baseline suites (cross-drive temp-path tests, baseline hash drifts, and packaging registry artifact drift). CIV-1 substrate tests remain green.

## Extension Points (CIV-2+)
- Cohort/population affiliation and macro cohort abstractions.
- Governance policy behaviors (`governance_type_id`) as solver/domain modules.
- Treaty metadata and directional diplomacy.
- Claim-to-conflict escalation integration (war/trade systems).
- Cross-shard faction governance and explicit global civ coordinator patterns.
