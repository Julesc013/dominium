Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# FORKING_PROVIDES_BASELINE

## Purpose

LIB-5 establishes deterministic coexistence rules for forks, alternative providers, and ambiguous shared surfaces.

The baseline pins:

- namespace-safe `pack_id` conventions
- deterministic `provides_declaration` records
- deterministic `provides_resolution` records
- explicit resolution policies
- PACK-COMPAT and CAP-NEG integration points

## Namespace Rules

Canonical new pack id forms:

- `official.<org>.<pack>`
- `mod.<author>.<pack>`
- `fork.<origin_pack_id>.<fork_author>.<fork_name>`
- `local.<user>.<pack>`

Rules:

- `pack_id` remains stable and unique.
- forks must not reuse the original `pack_id`.
- legacy reverse-DNS ids remain loadable for compatibility.

## Resolution Policies

- `resolve.strict_refuse_ambiguous`
- `resolve.explicit_required`
- `resolve.deterministic_highest_priority`
- `resolve.deterministic_lowest_pack_id`

Deterministic behavior:

- strict policy refuses ambiguity
- explicit policy requires an instance-level choice
- priority policy tie-breaks by `pack_id`
- lowest-pack-id policy provides a stable anarchy fallback

No silent provider selection is permitted.

## Integration Points

- PACK-COMPAT gathers required provides ids and provider declarations, resolves them deterministically, and pins the result into the lock.
- launcher preflight/start refuses missing or ambiguous required providers under strict policies.
- chosen provider capabilities flow into CAP-NEG and may drive explicit degrade/refuse outcomes.
- instance manifests may carry `resolution_policy_id` and `provides_resolutions` when provider choice is instance-scoped.

## Readiness For LIB-6

LIB-5 is ready for export/import tooling because:

- provider choice is recorded canonically
- fork identity and pack identity stay distinct
- linked and portable instance flows can carry provider resolution without path semantics
- bundle import/export can vendor the same pack artifacts while preserving deterministic provider choice

## Enforced Invariants

- `INV-FORKS-MUST-NAMESPACE`
- `INV-PROVIDES-RESOLUTION-DETERMINISTIC`
- `INV-STRICT-REFUSES-AMBIGUITY`
