Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# MOVE-SCRIPT-00 Routing Preview

Mode: `dry_run`.

## Summary

| Metric | Count |
| --- | ---: |
| Bad-root tracked files | 1765 |
| Route candidates | 1593 |
| Skipped/deferred | 172 |
| Collisions | 0 |

## Route Candidates By Batch

| Batch | Count |
| --- | ---: |
| `authority_policy` | 17 |
| `content_identity` | 1488 |
| `libs_abi` | 86 |
| `templates_models_modding` | 2 |

## Top Skip Reasons

| Reason | Count |
| --- | ---: |
| `active_python_package_requires_import_rewrite_or_shim_plan` | 142 |
| `identity_sensitive_without_clear_identity_safe_route` | 59 |
| `target_uses_forbidden_segment_source` | 13 |
| `authority_sensitive_docs_only_route_requires_review` | 7 |
| `normative_specs_reality_docs_require_authority_review` | 7 |
| `target_uses_forbidden_segment_compat` | 3 |

## First Route Candidates

| Source | Target | Batch | Risk |
| --- | --- | --- | --- |
| `locks/pack_lock.mvp_default.json` | `contracts/package/locks/pack_lock.mvp_default.json` | `authority_policy` | `high` |
| `repo/canon_state.json` | `contracts/repo/canon_state.json` | `authority_policy` | `high` |
| `repo/release_policy.toml` | `contracts/repo/release_policy.toml` | `authority_policy` | `high` |
| `repo/repox/repox_exemptions.json` | `contracts/repo/repox/repox_exemptions.json` | `authority_policy` | `high` |
| `repo/repox/rulesets/abstraction.json` | `contracts/repo/repox/rulesets/abstraction.json` | `authority_policy` | `high` |
| `repo/repox/rulesets/change_shape.json` | `contracts/repo/repox/rulesets/change_shape.json` | `authority_policy` | `high` |
| `repo/repox/rulesets/core.json` | `contracts/repo/repox/rulesets/core.json` | `authority_policy` | `high` |
| `repo/repox/rulesets/data_first.json` | `contracts/repo/repox/rulesets/data_first.json` | `authority_policy` | `high` |
| `repo/repox/rulesets/derived_artifacts.json` | `contracts/repo/repox/rulesets/derived_artifacts.json` | `authority_policy` | `high` |
| `repo/repox/rulesets/packaging.json` | `contracts/repo/repox/rulesets/packaging.json` | `authority_policy` | `high` |
| `repo/repox/rulesets/security.json` | `contracts/repo/repox/rulesets/security.json` | `authority_policy` | `high` |
| `repo/repox/rulesets/ui_parity.json` | `contracts/repo/repox/rulesets/ui_parity.json` | `authority_policy` | `high` |
| `updates/beta.json` | `release/updates/beta.json` | `authority_policy` | `high` |
| `updates/changelog.json` | `release/updates/changelog.json` | `authority_policy` | `high` |
| `updates/nightly.json` | `release/updates/nightly.json` | `authority_policy` | `high` |
| `updates/pinned.json` | `release/updates/pinned.json` | `authority_policy` | `high` |
| `updates/stable.json` | `release/updates/stable.json` | `authority_policy` | `high` |
| `bundles/README.md` | `docs/content/bundles/README.md` | `content_identity` | `high` |
| `bundles/bundle.base.lab/bundle.json` | `content/bundles/bundle.base.lab/bundle.json` | `content_identity` | `high` |
| `bundles/bundle.null/bundle.json` | `content/bundles/bundle.null/bundle.json` | `content_identity` | `high` |
| `data/CONTENT_AUDIT.md` | `archive/generated/CONTENT_AUDIT.md` | `content_identity` | `medium` |
| `data/agents/agent_context.json` | `archive/generated/agents/agent_context.json` | `content_identity` | `low` |
| `data/agents/task_intent_map.json` | `archive/generated/agents/task_intent_map.json` | `content_identity` | `low` |
| `data/analysis/duplicate_cluster_rankings.json` | `archive/generated/analysis/duplicate_cluster_rankings.json` | `content_identity` | `medium` |
| `data/analysis/implementation_scores.json` | `archive/generated/analysis/implementation_scores.json` | `content_identity` | `medium` |
| `data/architecture/architecture_graph.json` | `archive/generated/architecture/architecture_graph.json` | `content_identity` | `low` |
| `data/architecture/architecture_graph.v1.json` | `archive/generated/architecture/architecture_graph.v1.json` | `content_identity` | `low` |
| `data/architecture/module_boundary_rules.v1.json` | `archive/generated/architecture/module_boundary_rules.v1.json` | `content_identity` | `low` |
| `data/architecture/module_dependency_graph.json` | `archive/generated/architecture/module_dependency_graph.json` | `content_identity` | `low` |
| `data/architecture/module_registry.json` | `contracts/registry/architecture/module_registry.json` | `content_identity` | `high` |
| `data/architecture/module_registry.v1.json` | `contracts/registry/architecture/module_registry.v1.json` | `content_identity` | `high` |
| `data/architecture/single_engine_registry.json` | `contracts/registry/architecture/single_engine_registry.json` | `content_identity` | `high` |
| `data/archive/README.md` | `archive/historical/data/README.md` | `content_identity` | `low` |
| `data/archive/scenarios/README.md` | `archive/historical/data/scenarios/README.md` | `content_identity` | `low` |
| `data/archive/scenarios/README_ARCHIVE.md` | `archive/historical/data/scenarios/README_ARCHIVE.md` | `content_identity` | `low` |
| `data/archive/world/README_ARCHIVE.md` | `archive/historical/data/world/README_ARCHIVE.md` | `content_identity` | `low` |
| `data/archive/world/milky_way/README.md` | `archive/historical/data/world/milky_way/README.md` | `content_identity` | `low` |
| `data/archive/world/milky_way/milky_way.anchors.json` | `archive/historical/data/world/milky_way/milky_way.anchors.json` | `content_identity` | `low` |
| `data/archive/world/milky_way/milky_way.arms.json` | `archive/historical/data/world/milky_way/milky_way.arms.json` | `content_identity` | `low` |
| `data/archive/world/milky_way/milky_way.galaxy.json` | `archive/historical/data/world/milky_way/milky_way.galaxy.json` | `content_identity` | `low` |

Additional route candidates are recorded in the JSON report.
