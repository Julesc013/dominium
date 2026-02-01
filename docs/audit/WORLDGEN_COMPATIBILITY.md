Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Worldgen Compatibility Audit

Status: canonical.
Scope: worldgen compatibility across versions and pack sets.
Authority: canonical. All tooling and packs MUST conform.

## Scenario: Old saves + new worldgen packs
- Expected behavior: load with preserved unknown fields.
- Degradation mode: `degrade_or_freeze` if required capabilities missing.
- Messaging: explicit warning listing missing capabilities and affected domains.

## Scenario: New packs + old engines
- Expected behavior: older engine preserves unknown fields and tags.
- Degradation mode: `frozen` if required capabilities are unsupported.
- Messaging: explicit refusal to simulate with capability gaps.

## Scenario: Missing reality packs
- Expected behavior: objective truth remains valid without those overlays.
- Degradation mode: `degraded` or `frozen` for dependent views only.
- Messaging: explicit notice of missing reality capabilities.

## Scenario: Conflicting refinement layers
- Expected behavior: precedence rules resolve overlays; conflicts are surfaced.
- Degradation mode: `degrade_or_freeze` when precedence is ambiguous.
- Messaging: explicit conflict report with layer ids and scope.

## Scenario: Removed model families
- Expected behavior: plan layers using missing models are skipped.
- Degradation mode: `degraded` with explicit failure modes.
- Messaging: explicit list of removed models and affected plans.