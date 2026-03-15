Status: DERIVED
Stability: provisional
Future Series: OBSERVABILITY
Replacement Target: release-pinned observability registry and redaction policies

# Observability Contract

## Guaranteed Log Categories

The following categories are guaranteed and must remain available through the structured log engine:

- `compat`: negotiation, degrade, compatibility refusal, install-selection outcomes
- `packs`: pack verification, pack-lock generation, trust evaluation summaries
- `lib`: install, instance, save, and migration lifecycle operations
- `update`: release-index resolution, plan/apply/rollback decisions
- `supervisor`: spawn, restart, stop, attach, and child lifecycle events
- `server`: connection lifecycle and proof-anchor emission
- `diag`: repro bundle capture and replay support events
- `refusal`: all explicit refusals

## Canonical vs Derived

- Canonical records:
  - compatibility and negotiation records
  - proof anchors
  - install plans and update plans
  - refusal payloads
  - transaction-log entries
- Derived logs:
  - informational lifecycle events
  - compactable operator summaries
  - UI-mode and presentation summaries

Canonical records must remain replayable. Derived logs may be compacted, but only after canonical records remain available.

## Filtering

Structured logs must be filterable by:

- `category`
- `severity`
- `session_id`
- `connection_id`

Filtered output must remain deterministically ordered by canonical log ordering, never by reader timing.

## Privacy

Default observability surfaces must not log:

- secrets
- private signing material
- passwords
- raw authentication tokens
- machine-private identifiers

Sensitive fields must be deterministically redacted. Redaction policy is category-bound and may be further restricted by EpistemicProfile.

## Repro Bundle Minimum Set

Every DIAG-0 repro bundle must include:

- negotiation records
- pack verification report
- install plan
- update plan
- proof anchors
- last `N` canonical events
- last `N` logs

If a capture surface has no live payload for one of these artifacts, the bundle must include a deterministic `unavailable/not_captured` placeholder instead of silently omitting the file.

## Enforcement

- Guaranteed categories must declare stable category ids and message keys.
- Guaranteed-category events must satisfy their minimum fields.
- Refusals must always log `refusal_code`, `reason`, and `remediation_hint`.
- Structured logs must remain deterministic and must not drift into ad hoc debug printing in governed logging surfaces.
