# Roadmap Overview (Coverage-Driven)

Status: binding.
Scope: roadmap framing for simulation coverage.

This roadmap is coverage-driven, not progression-driven.
Coverage is a test-and-documentation construct that defines what the
simulation should eventually be capable of representing. It does NOT
imply era logic, tech trees, or runtime unlocks.

## Coverage vs Progression

- Coverage is enforced by TESTX suites and contract documents.
- Progression is a content concern and must remain data-driven.
- Runtime code MUST NOT branch on coverage levels, dates, or milestones.

## How Progress Is Measured

- Coverage status is declared in `tests/coverage/*/coverage.json`.
- Tests validate consistency and publish status as:
  UNSUPPORTED, PARTIAL, or COMPLETE.
- Failing coverage targets are visible in tests and docs, but they do not
  create runtime gating or progression flags.

## Mod Extension

Mods can extend coverage by providing new schemas, process families, and
capabilities. Coverage tests are designed to be content-agnostic: capability
presence enables behavior, capability absence yields refusal.

## See also
- `docs/roadmap/SIMULATION_COVERAGE_LADDER.md`
- `docs/roadmap/SLICE_VS_COVERAGE.md`
