# POST-CONVERGE-10N Next Family Recommendation

Status: DERIVED
Last Reviewed: 2026-05-17

## Recommendation

Do not start POST-CONVERGE-11 yet.

The next semantic task should target the residual non-proof RepoX families:

- `INV-REPOX-RULESET-MISSING` for `INV-NO-UNNAMED-RNG` and `INV-WORLDGEN-LOCK-REQUIRED`
- `INV-CANON-NO-SUPERSEDED` for `docs/architecture/DIRECTORY_CONTEXT.md`
- `INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY` for `capability_overrides`
- worldgen retry-loop and shadow bounded policy failures
- MW-4 fixture import failure caused by `game.domains.embodiment` lazy imports

TEST-PERF follow-up remains appropriate for faster validation, especially CTest sharding and slow-test evidence, but it should not be treated as a replacement for the remaining semantic RepoX disposition.
