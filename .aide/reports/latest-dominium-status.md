
# Latest Dominium Status

Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

## Current Position

POST-CONVERGE-10M completed as PARTIAL. Focused RepoX improved from 51 failures / 5 warnings to 23 failures / 5 warnings by fixing safe stale retired-domain RepoX rule paths and rule-file cache invalidation.

Two current MW-4 fixture failures remain because `game.domains.embodiment` lazily imports retired `embodiment.*` modules. POST-CONVERGE-11 remains blocked because additional non-proof RepoX governance failures remain.

## Next Recommended Task

`POST-CONVERGE-10N - Tool Hash, Audit Staleness, Ruleset Mapping, and Remaining RepoX Gate Classification`, or `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline` if wall-time reduction is prioritized next.
