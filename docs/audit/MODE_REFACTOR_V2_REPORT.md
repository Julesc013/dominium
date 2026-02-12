Status: DERIVED
Last Reviewed: 2026-02-12
Supersedes: docs/audit/MODE_REFACTOR_REPORT.md
Superseded By: none

# Mode Refactor V2 Report

## What Changed
- Added a canonical terminology stack with schema + registry (`schema/governance/glossary.schema`, `data/registries/glossary.json`) and deterministic glossary projection (`docs/architecture/TERMINOLOGY_GLOSSARY.md`).
- Introduced explicit universe identity/state split with schema-enforced immutability (`schema/universe/universe_identity.schema`, `schema/universe/universe_state.schema`).
- Extended authority context into a first-class runtime contract (`schema/authority/authority_context.schema`) and propagated enforcement markers into client/server launch + intent paths.
- Expanded session specification for reproducible launch binding (`schema/session/session_spec.schema`) and added default template registry (`data/registries/session_defaults.json`).
- Wired profile registries to session/authority context references and maintained data-first mode composition through law + experience + parameter bundle bindings.

## Enforcement Added/Strengthened
- RepoX:
  - `INV-GLOSSARY-TERM-CANON`
  - `INV-UNIVERSE_IDENTITY_IMMUTABLE`
  - `INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS`
  - `INV-SESSION_SPEC_REQUIRED_FOR_RUN`
  - strengthened `INV-NO-HARDCODED-MODE-BRANCH` to detect branch-pattern smell.
- AuditX analyzers:
  - `C4_TERMINOLOGY_MISUSE`
  - `C5_EXPERIENCE_PROFILE_DRIFT`
  - `C6_AUTHORITY_BYPASS_SMELL`
  - strengthened `C2_MODE_FLAG_SMELL`.
- TestX:
  - `test_universe_identity_immutability`
  - `test_authority_context_enforcement`
  - `test_client_cannot_escalate_entitlements`
  - `test_session_spec_roundtrip`
  - `test_session_spec_required_for_launch`
  - `test_glossary_consistency`
  - systemic `test_future_case_stress_suite`.

## Old-to-New Mapping
- Hardcoded mode branches -> profile resolution (`ExperienceProfile` + `LawProfile` + `ParameterBundle`).
- Ad-hoc launch payloads -> canonical `SessionSpec`.
- Implicit trust assumptions -> explicit `AuthorityContext`.
- Single mutable "universe" record -> immutable `UniverseIdentity` + mutable `UniverseState`.

## Migration Notes
- Existing launch paths must materialize `SessionSpec` before run.
- Multiplayer/session negotiation paths must carry `AuthorityContext` and reject client-side escalation.
- Mode-like additions must be represented as data in registries; code branches with mode tokens are blocked.
- Glossary changes must be made in `data/registries/glossary.json` and regenerated into canonical docs.

## Remaining Non-Semantic Gaps
- Future-case constructibility remains structural validation only; domain behavior is intentionally deferred.
- Authority enforcement is currently marker + refusal-path focused and remains compatible with deeper server policy wiring.
