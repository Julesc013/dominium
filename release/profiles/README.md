Status: CANONICAL
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Stability: provisional
Task: PROVIDER-STRUCTURE-CANON-01

# Release Provider Profiles

Release profiles select providers for development, validation, release, and
packaging recipes. They are not authored game/user payloads; those remain under
`content/profiles`.

Provider IDs in these files must reference `contracts/provider/provider.registry.json`.
