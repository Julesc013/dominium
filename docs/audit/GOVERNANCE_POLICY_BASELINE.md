Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: GOVERNANCE/ARCHIVE
Replacement Target: signed release publication bundles and archive governance policy

# Governance Policy Baseline

## Default Governance Mode For v0.0.0-mock

- governance_mode_id: `gov.open`
- governance_version: `1.0.0`
- governance_profile_hash: `09273dc808ff2cf8edab36eb30ce4139212bcce8903a3ab5a3043a9fcfd08187`
- mock release remains usable under hash-mandatory, signature-optional policy.

## Fork And Namespace Rules

- Official tag example: `v0.0.0-mock`
- Fork tag example: `fork.<org>.v0.0.0-mock`
- Invalid unprefixed fork example is refused with `refusal.governance.fork_prefix_required`.

## Archive Policy Summary

- Primary archive plus at least one secondary mirror.
- Offline cold storage recommended.
- Release index must record the matching governance profile hash.

## Readiness

- PERFORMANCE-ENVELOPE-0: ready
- ARCHIVE-POLICY-0: ready
