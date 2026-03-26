Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: filled snapshot-to-blueprint reconciliation packet after fresh repository archaeology

# Snapshot Mapping Template

## Template Fields

Each row must be completed against the fresh repository snapshot before post-snapshot prompts execute.

| Field | Purpose |
| --- | --- |
| planned_module_targets | Expected architectural targets from the blueprint. |
| actual_repo_locations | Observed files, modules, or docs in the live repository. |
| gaps_found | Missing foundations or artifacts that block the prompt. |
| drift_found | Conflicts between the blueprint and live repo state. |
| obsolete_assumptions | Blueprint assumptions invalidated by the live repo. |
| keep_merge_replace_recommendation | Current recommendation before implementation planning. |
| confidence_score | Mapping confidence from 0.0 to 1.0. |
| requires_manual_review | Whether a human review gate is mandatory. |

## Prompt Rows

| Prompt | Series | Planned Module Targets | Default Recommendation | Manual Review |
| --- | --- | --- | --- | --- |
| Σ-0 | Σ | AGENTS.md, docs/blueprint, tools/controlx, tools/xstack | undetermined | yes |
| Σ-1 | Σ | AGENTS.md, docs/blueprint, tools/controlx, tools/xstack | undetermined | no |
| Σ-2 | Σ | AGENTS.md, docs/blueprint, tools/controlx, tools/xstack | undetermined | yes |
| Σ-3 | Σ | AGENTS.md, docs/blueprint, tools/controlx, tools/xstack | undetermined | no |
| Σ-4 | Σ | AGENTS.md, docs/blueprint, tools/controlx, tools/xstack | undetermined | yes |
| Σ-5 | Σ | AGENTS.md, docs/blueprint, tools/controlx, tools/xstack | undetermined | yes |
| Σ-6 | Σ | AGENTS.md, docs/blueprint, tools/controlx, tools/xstack | undetermined | no |
| Φ-0 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-1 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-2 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-3 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-4 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-5 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-6 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-7 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-8 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-9 | Φ | client, docs/blueprint, engine, server | undetermined | no |
| Φ-10 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-11 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-12 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-13 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Φ-14 | Φ | client, docs/blueprint, engine, server | undetermined | yes |
| Υ-0 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | yes |
| Υ-1 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | no |
| Υ-2 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | yes |
| Υ-3 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | no |
| Υ-4 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | no |
| Υ-5 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | no |
| Υ-6 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | yes |
| Υ-7 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | no |
| Υ-8 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | no |
| Υ-9 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | yes |
| Υ-10 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | yes |
| Υ-11 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | yes |
| Υ-12 | Υ | cmake, dist, docs, docs/blueprint, tools/xstack | undetermined | yes |
| Ζ-0 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-1 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-2 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-3 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-4 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-5 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-6 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-7 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-8 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-9 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-10 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-11 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-12 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-13 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-14 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-15 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-16 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-17 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-18 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-19 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-20 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-21 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-22 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-23 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-24 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-25 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-26 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-27 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-28 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-29 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-30 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-31 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-32 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-33 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-34 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-35 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-36 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-37 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-38 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-39 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-40 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-41 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-42 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-43 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | no |
| Ζ-44 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-45 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-46 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-47 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-48 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-49 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-50 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-51 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-52 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-53 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | no |
| Ζ-54 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | no |
| Ζ-55 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | yes |
| Ζ-56 | Ζ | client, data, docs/blueprint, engine, packs, server, tools/xstack | undetermined | no |
| Ζ-57 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-58 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-59 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-60 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-61 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-62 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-63 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-64 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-65 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-66 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-67 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-68 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-69 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-70 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-71 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-72 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-73 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
| Ζ-74 | Ζ | client, docs/blueprint, engine, server, tools/xstack | undetermined | yes |
