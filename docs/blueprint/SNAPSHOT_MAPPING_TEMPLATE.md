Status: DERIVED
Last Reviewed: 2026-03-31
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
| Σ-0 | Σ | control, data, docs, governance, tools | undetermined | yes |
| Σ-1 | Σ | control, data, docs, governance, tools | undetermined | no |
| Σ-2 | Σ | control, data, docs, governance, tools | undetermined | yes |
| Σ-3 | Σ | control, data, docs, governance, tools | undetermined | no |
| Σ-4 | Σ | control, data, docs, governance, tools | undetermined | yes |
| Σ-5 | Σ | control, data, docs, governance, tools | undetermined | yes |
| Σ-6 | Σ | control, data, docs, governance, tools | undetermined | no |
| Φ-0 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-1 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-2 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-3 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-4 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-5 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-6 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-7 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-8 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-9 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | no |
| Φ-10 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-11 | Φ | apps, compat, data, docs, engine, game, platform, runtime, ui | undetermined | yes |
| Φ-12 | Φ | apps, compat, data, docs, engine, game, net, platform, runtime, ui | undetermined | yes |
| Φ-13 | Φ | apps, compat, data, docs, engine, game, net, platform, runtime, ui | undetermined | yes |
| Φ-14 | Φ | apps, compat, data, docs, engine, game, net, platform, runtime, ui | undetermined | yes |
| Υ-0 | Υ | data, dist, docs, release, tools | undetermined | yes |
| Υ-1 | Υ | data, dist, docs, release, tools | undetermined | no |
| Υ-2 | Υ | data, dist, docs, release, tools | undetermined | yes |
| Υ-3 | Υ | data, dist, docs, release, tools | undetermined | no |
| Υ-4 | Υ | data, dist, docs, release, tools | undetermined | no |
| Υ-5 | Υ | data, dist, docs, release, tools | undetermined | no |
| Υ-6 | Υ | data, dist, docs, release, tools | undetermined | yes |
| Υ-7 | Υ | data, dist, docs, release, tools | undetermined | no |
| Υ-8 | Υ | data, dist, docs, release, tools | undetermined | no |
| Υ-9 | Υ | data, dist, docs, release, tools | undetermined | yes |
| Υ-10 | Υ | data, dist, docs, release, tools | undetermined | yes |
| Υ-11 | Υ | data, dist, docs, release, tools | undetermined | yes |
| Υ-12 | Υ | data, dist, docs, release, tools | undetermined | yes |
| Ζ-0 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-1 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-2 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-3 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-4 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-5 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-6 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-7 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-8 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-9 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-10 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-11 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-12 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-13 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-14 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-15 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-16 | Ζ | apps, compat, data, docs, engine, game, platform, security, tools, ui | undetermined | yes |
| Ζ-17 | Ζ | apps, compat, data, docs, engine, game, platform, security, tools, ui | undetermined | yes |
| Ζ-18 | Ζ | apps, compat, data, docs, engine, game, platform, security, tools, ui | undetermined | yes |
| Ζ-19 | Ζ | apps, compat, data, docs, engine, game, platform, security, tools, ui | undetermined | yes |
| Ζ-20 | Ζ | apps, compat, data, docs, engine, game, platform, security, tools, ui | undetermined | yes |
| Ζ-21 | Ζ | apps, compat, data, docs, engine, game, platform, security, tools, ui | undetermined | yes |
| Ζ-22 | Ζ | apps, compat, data, docs, engine, game, platform, security, tools, ui | undetermined | yes |
| Ζ-23 | Ζ | apps, compat, data, docs, engine, game, platform, security, tools, ui | undetermined | yes |
| Ζ-24 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-25 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-26 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-27 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-28 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-29 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-30 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-31 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-32 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-33 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-34 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-35 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-36 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-37 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-38 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-39 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-40 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-41 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-42 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | yes |
| Ζ-43 | Ζ | apps, data, docs, engine, game, platform, tools, ui | undetermined | no |
| Ζ-44 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-45 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-46 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-47 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-48 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-49 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-50 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-51 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-52 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-53 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | no |
| Ζ-54 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | no |
| Ζ-55 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | yes |
| Ζ-56 | Ζ | apps, data, docs, engine, game, modding, packs, platform, tools, ui | undetermined | no |
| Ζ-57 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-58 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-59 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-60 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-61 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-62 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-63 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-64 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-65 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-66 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-67 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-68 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-69 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-70 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-71 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-72 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-73 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
| Ζ-74 | Ζ | apps, data, docs, engine, game, net, platform, runtime, tools, ui, updates | undetermined | yes |
